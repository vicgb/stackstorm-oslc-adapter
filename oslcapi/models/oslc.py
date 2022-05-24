from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import DCTERMS, RDF, RDFS
import logging
from oslcapi.api.helpers.service_api import rules_to_oslc_resource, get_all_rules, create_rule, delete_rule, update_rule, get_st2_instance, module_to_service_provider, get_rule_by_id
log = logging.getLogger('tester.sub')
import json
import collections

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')
OSLC_ACTION = Namespace('http://open-services.net/ns/actions#')

# TODO: Modelar reglas st2. De momento URI falsa.
ST2 = Namespace('http://st2-prueba.net/ns/core#')


base_url = 'http://localhost:5000'


class OSLCStore:
    def __init__(self, trs):
        self.catalog = ServiceProviderCatalog()
        self.initialize_oslc()
        self.trs = trs
        self.trs.initialize_trs(self.catalog)
      


    def initialize_oslc(self):

        for module in get_st2_instance():
            service_provider = ServiceProvider(module, len(self.catalog.service_providers)+1)
            self.catalog.add(service_provider)

        for rule in get_all_rules():
            self.add_resource(service_provider, rule)

        log.warning('OSLC store loaded')

    def add_resource(self, service_provider, element):
        resource = OSLCResource(service_provider, element, len(service_provider.oslc_resources)+1)
        service_provider.oslc_resources.append(resource)
        return resource

   
    def remove_resource(self,service_provider, element):
        resource = OSLCResource(service_provider, element, len(service_provider.oslc_resources)-1)
        service_provider.oslc_resources.pop(len(service_provider.oslc_resources)-1)
        return resource

    
    def replace_resource(self, service_provider, element):
        deleted_resource = self.remove_resource(service_provider, element)
        updated_resource = self.add_resource(service_provider, element)
        return updated_resource
    
    
    def update_resources(self,service_provider, rule_id, action):
        rules_list = []
        for rule in get_all_rules():
            rules_list.append(rule['id'])

            if action.__contains__('update'):
                for rule in get_all_rules():
                    rules_list.append(rule['id'])
                    if rule_id == rule['id']:
                        self.replace_resource(service_provider, rule)

            if action.__contains__('delete'):
                for oslc_resource in service_provider.oslc_resources:
                    if oslc_resource.element['id'] not in rules_list:
                        service_provider.oslc_resources.remove(oslc_resource)
                        #oslc_resource.rdf.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
            
            #De momento no se van a crear reglas en la interfaz de Stackstorm, por tiempo.
        
        else:
            log.warning("There is a problem updating the resources.")
       
            
        
        log.warning('Resources updated!')
    

class ServiceProviderCatalog:
    def __init__(self): 
        self.rdf = Graph()
        self.uri = URIRef(base_url+'/service/serviceProviders/catalog')

        self.service_providers = []
        
        # OSLC Actions
        self.oslc_actions = []
         
        self.rdf.add((self.uri, DCTERMS.title, Literal('StackStorm OSLC Server')))
        self.rdf.add((self.uri, DCTERMS.description, Literal('A server that provides OSLC capabilities to Stackstorm')))
        self.rdf.add((self.uri, RDF.type, OSLC.ServiceProviderCatalog))
        self.rdf.add((self.uri, OSLC.domain, URIRef('http://open-services.net/ns/cm#')))

    def add(self, service_provider):
        self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))
        self.service_providers.append(service_provider)
    
    # Crea objeto de la clase Action para guardar
    def create_action(self, id, service_provider, action_type):
        action = Action(id, service_provider, action_type)
        self.oslc_actions.append(action)
        return action
    
class ServiceProvider:
    def __init__(self, module, id):
        self.rdf = Graph()
        self.id = id
        self.uri = URIRef(base_url+'/service/serviceProviders/'+str(self.id))

        self.oslc_resources = []
        
        self.rdf.add((self.uri, RDF.type, OSLC.ServiceProvider))

        service = BNode()

        self.rdf.add((self.uri, OSLC.service, service))
        self.rdf.add((service, RDF.type, OSLC.Service))
        self.rdf.add((service, OSLC.domain, URIRef('http://open-services.net/ns/cm#')))

        creationFactory = BNode()

        self.rdf.add((service, OSLC.creationFactory, creationFactory))
        self.rdf.add((creationFactory, RDF.type, OSLC.CreationFactory))
        self.rdf.add((creationFactory, OSLC.resourceType, OSLC_CM.ChangeRequest))
        self.rdf.add((creationFactory, OSLC.label, Literal('Creation Factory')))
        self.rdf.add((creationFactory, OSLC.creation, URIRef(base_url+'/service/serviceProviders/'+str(self.id)+'/changeRequests')))

        queryCapability = BNode()

        self.rdf.add((service, OSLC.queryCapability, queryCapability))
        self.rdf.add((queryCapability, RDF.type, OSLC.QueryCapability))
        self.rdf.add((queryCapability, OSLC.resourceType, OSLC_CM.ChangeRequest))
        self.rdf.add((queryCapability, OSLC.label, Literal('Query Capability')))
        self.rdf.add((queryCapability, OSLC.queryBase, URIRef(base_url+'/service/serviceProviders/'+str(self.id)+'/changeRequests')))        

        module_to_service_provider(module, self)



class OSLCResource:
    def __init__(self, service_provider, element, id):
        self.rdf = Graph()
        self.id = id
        self.uri = URIRef(base_url+'/service/serviceProviders/'+str(service_provider.id)+'/changeRequests/'+str(self.id))
        self.element = element
        self.rdf.add((self.uri, RDF.type, OSLC_CM.ChangeRequest))
        self.rdf.add((self.uri, OSLC.serviceProvider, service_provider.uri))

        rules_to_oslc_resource(element, self)


'''

    DEFINITION OF OSLC ACTIONS

'''

# Se define la estructura que tendrá el RDF de una OSLC Action
class Action:
    def __init__(self, id, service_provider, action_type):
        self.rdf = Graph()
        self.id = id
        self.service_provider = service_provider
        self.action_type = action_type
        self.uri = URIRef(base_url + '/action/' + str(self.id))

        self.rdf.add((self.uri, RDF.type, OSLC_ACTION.Action))
        self.rdf.add((self.uri, RDF.type, Literal(self.action_type)))
        
        # No se si tiene sentido porque solo hay 1 service provider
        #self.rdf.add((self.uri, OSLC_ACTION.actionProvider, Literal(self.service_provider)))

    def add_result(self, result):
        self.rdf.add((self.uri, OSLC_ACTION.actionResult, Literal(result)))