import logging
import json
import requests
import os
import pymongo
from oslcapi.api.helpers.service_actions import create_resource, update_resource, delete_resource
from oslcapi.store import store
from oslcapi.api.helpers.service_api import get_rule_by_id
from oslcapi.api.helpers.service_api import rules_to_oslc_resource
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_rdf.flask import returns_rdf
from rdflib import Graph, URIRef, Literal, Namespace, RDFS, RDF
from rdflib.plugins.stores import sparqlstore
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID as default
from time import sleep  
from json import dumps, loads
from kafka import KafkaProducer  
from kafka import KafkaConsumer  
from pymongo import MongoClient


FUSEKI_USER = os.getenv("FUSEKI_USER")
FUSEKI_PASSWORD = os.getenv("FUSEKI_PASSWORD")
QUERY_FUSEKI_ENDPOINT = os.getenv("QUERY_FUSEKI_ENDPOINT")
UPDATE_FUSEKI_ENDPOINT = os.getenv("UPDATE_FUSEKI_ENDPOINT")
KAFKA_HOST = os.getenv("KAFKA_HOST")
KAFKA_PORT = os.getenv("KAFKA_PORT")


#Fuseki endpoints
fuseki_store = sparqlstore.SPARQLUpdateStore(auth=(FUSEKI_USER,FUSEKI_PASSWORD))
fuseki_store.open((QUERY_FUSEKI_ENDPOINT, UPDATE_FUSEKI_ENDPOINT))


log = logging.getLogger('tester.sub')

# Namespaces
OSLC_EVENT = Namespace('http://open-services.net/ns/events#')
OSLC_ACTION = Namespace('http://open-services.net/ns/actions#')
ST2 = Namespace('http://localhost:5001/ns/st2_oslc#')
OSLC = Namespace('http://open-services.net/ns/core#')



# Kafka Producer
kafka_producer = KafkaProducer(  
    bootstrap_servers = [KAFKA_HOST+':'+KAFKA_PORT],  
    value_serializer = lambda x:dumps(x).encode('utf-8')  
    ) 



class OSLCResource(Resource):
    @returns_rdf
    def get(self, service_provider_id, oslc_resource_id):
        for service_provider in store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return resource.rdf
        return Graph()
    
    @returns_rdf
    def put(self, service_provider_id, oslc_resource_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return update_resource(service_provider, resource, graph, store)

        return Graph()
    
    @returns_rdf
    def delete(self, service_provider_id, oslc_resource_id):
        graph = Graph()
        # graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                for resource in service_provider.oslc_resources:
                    if resource.id == oslc_resource_id:
                        return delete_resource(service_provider, resource, graph, store)

        return Graph()

  

class OSLCResourceList(Resource):
    @returns_rdf
    def get(self, service_provider_id):
        g = Graph()
        for service_provider in store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                for resource in service_provider.oslc_resources:
                    g += resource.rdf
        return g
    
    @returns_rdf
    def post(self, service_provider_id):
        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for service_provider in store.catalog.service_providers:
            if service_provider_id == service_provider.id:
                return create_resource(service_provider, graph, store)

        return Graph()



class OSLCAction(Resource):
    @returns_rdf
    def get(self):
        g = Graph()
        for oslc_action in store.catalog.oslc_actions:
            g += oslc_action.rdf
        return g

    @returns_rdf
    def post(self):
        query_action = """

                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX oslc_actions: <http://open-services.net/ns/actions#>

                SELECT ?type

                WHERE {
                    ?s rdf:type ?type .
                }
            """

        graph = Graph()
        graph.parse(data=request.data, format=request.headers['Content-type'])

        for t in graph.query(query_action):

            actionProvider = store.catalog.service_providers[0]
            action = store.catalog.create_action(len(store.catalog.oslc_actions) + 1, str(actionProvider.id),
                                                    t.asdict()['type'].toPython())
            
 
            if str(t).__contains__("Create"):
                g = create_resource(actionProvider, graph, store)
                if (g == None):
                    action.add_result('Failed to create an action')
                else:
                    action.add_result('Action created successfully')
                return g
            elif str(t).__contains__("Delete"):
                return delete_resource(actionProvider, graph, store) 
            elif str(t).__contains__("Update"):
                return update_resource(actionProvider, graph, store)

        return Graph()


class ST2Logs(Resource):
    

    def post(self):

        envelope = json.loads(request.data.decode('utf-8'))
        payload = envelope['operationType']

        rule_id = envelope['documentKey']['_id']['$oid']
        rule = get_rule_by_id(rule_id)
        
        service_provider = store.catalog.service_providers[0]  

        if (payload == "update"): 
  
            # TRS Store
            resource = next(resource for resource in service_provider.oslc_resources if Literal(rule_id) in resource.rdf.objects(None, ST2.ruleId))
            store.trs.generate_change_event(resource, 'Update')
            log.warning("Se ha actualizado el TRS")
            
            # Update resources
            store.update_resources(service_provider, rule_id, 'update')
 
            #Send Data to Fuseki
            g = Graph(fuseki_store, identifier=default)
            g.add((OSLC_EVENT.Event, RDF.type, Literal('Modification')))
            g.add((OSLC.resource, ST2.ruleId, resource.uri ))

            #Kafka Producer
            g2 = Graph()
            g2.add((OSLC_EVENT.Event, RDF.type, Literal('Modification')))
            g2.add((OSLC.resource, ST2.ruleId, resource.uri ))
            kafka_producer.send('eventmessage', value = Graph.serialize(g2, format='application/rdf+xml')) 
            
        elif (payload == "delete"):
            
            # TRS Store
            resource = next(resource for resource in service_provider.oslc_resources if Literal(rule_id) in resource.rdf.objects(None, ST2.ruleId))
            store.trs.generate_change_event(resource, 'Deletion')
            log.warning("Se ha actualizado el TRS")

            # Update resources
            store.update_resources(service_provider, rule_id, 'delete')
            
            #Send Data to Fuseki
            g = Graph(fuseki_store, identifier=default)
            g.add((OSLC_EVENT.Event, RDF.type, Literal('Deletion')))
            g.add((OSLC.resource, ST2.ruleId, resource.uri ))
 
            #Kafka Producer
            g2 = Graph()
            g2.add((OSLC_EVENT.Event, RDF.type, Literal('Deletion')))
            g2.add((OSLC.resource, ST2.ruleId, resource.uri ))
            kafka_producer.send('eventmessage', value = Graph.serialize(g2, format='application/rdf+xml')) 

        elif (payload == "insert"):
            
            #TRS Store
            resource = store.add_resource(store.catalog.service_providers[0], rule)
            store.trs.generate_change_event(resource, 'Creation')
            log.warning("Se ha actualizado el TRS")

            #Send Data to Fuseki
            g = Graph(fuseki_store, identifier=default)
            g.add((OSLC_EVENT.Event, RDF.type, Literal('Creation')))
            g.add((OSLC.resource, ST2.ruleId, resource.uri ))

            #Kafka producer
            g2 = Graph()
            g2.add((OSLC_EVENT.Event, RDF.type, Literal('Creation')))
            g2.add((OSLC.resource, ST2.ruleId, resource.uri ))
            kafka_producer.send('eventmessage', value = Graph.serialize(g2, format='application/rdf+xml')) 
  
        else:
            log.warning("This action is not allowed by the adapter.")
            

        # Returning any 2xx status indicates successful receipt of the message.
        return 'OK', 200

