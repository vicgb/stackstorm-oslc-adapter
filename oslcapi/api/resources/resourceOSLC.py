from oslcapi.api.helpers.service_actions import create_resource, update_resource, delete_resource
from oslcapi.store import store
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_rdf.flask import returns_rdf
from rdflib import Graph, URIRef, Literal, Namespace, RDFS, RDF
import logging
import json
import requests
import os
from oslcapi.api.helpers.service_api import get_rule_by_id
from time import sleep  
from json import dumps  
from kafka import KafkaProducer  
from kafka import KafkaConsumer  
import pymongo
from pymongo import MongoClient  

log = logging.getLogger('tester.sub')
OSLC_EVENT = Namespace('http://open-services.net/ns/events#')
OSLC_ACTION = Namespace('http://open-services.net/ns/actions#')

# initializing the Kafka producer  
my_producer = KafkaProducer(  
    bootstrap_servers = ['localhost:29092'],  
    value_serializer = lambda x:dumps(x).encode('utf-8')  
    ) 

my_consumer = KafkaConsumer(  
    'OSLC_Event',  
        bootstrap_servers = ['localhost:29092'],  
        auto_offset_reset = 'earliest',  
        enable_auto_commit = True,  
        group_id = 'my-group',  
        value_deserializer = lambda x : loads(x.decode('utf-8'))  
        )  
CONNECTION_STRING = "mongodb://fd6bd9c7f88c:27017"
my_client = pymongo.MongoClient(CONNECTION_STRING)
my_collection = my_client.eventmessage.eventmessage 

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
            if str(t).__contains__("Rule"):
                
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
        g = Graph()
       

        if (payload == "update"): 
            
            g.add((OSLC_EVENT.uri, RDF.type, Literal('Modify')))
            
            #g.add((resource.uri, DCTERMS.description, Literal('Update event')))

            #Kafka producer
            #requests.post('http://localhost:5002/service/event/payload', data=Graph.serialize(g, format='application/rdf+xml'))  
            my_producer.send('eventmessage', value = Graph.serialize(g, format='application/rdf+xml'))
            for message in my_consumer:  
                message = message.value  
                my_collection.insert_one(message)  
                print(message + " added to " + my_collection)  
            store.update_resources(store.catalog.service_providers[0], rule_id, 'update')
            
            
            # TRS Store
            resource = store.add_resource(store.catalog.service_providers[0], rule)
            store.trs.generate_change_event(resource, 'Update')
            log.warning("Se ha actualizado el TRS")
            
            

        elif (payload == "delete"):
            g.add((OSLC_ACTION.uri, RDF.type, Literal('Delete')))
        
            #Kafka producer
            requests.post('http://localhost:5002/service/event/payload', data=Graph.serialize(g, format='application/rdf+xml'))

            store.update_resources(store.catalog.service_providers[0], rule_id, 'delete')
            
            # TRS Store
            resource = store.add_resource(store.catalog.service_providers[0], rule)
            store.trs.generate_change_event(resource, 'Update')
            log.warning("Se ha actualizado el TRS")

        elif (payload == "insert"):
           log.warning("This action is not allowed by the adapter.")
        else:
            log.warning("This action is not allowed by the adapter.")
            

        # Returning any 2xx status indicates successful receipt of the message.
        return 'OK', 200

