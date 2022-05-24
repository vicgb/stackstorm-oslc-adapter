from rdflib import Graph, URIRef, Literal, Namespace, DCTERMS, RDF, RDFS
from oslcapi.api.helpers.service_api import update_rule, delete_rule,load_rule, create_rule, get_rule_by_id, get_all_rules
import os
import logging


log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')

token = os.getenv("TOKEN")

def create_resource(service_provider, graph, store):
    
    query_st2 = """

        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX st2: <http://st2-prueba.net/ns/core#>
        PREFIX oslc: <http://open-services.net/ns/cm#>

        SELECT ?name ?enabled ?triggerRef ?triggerType ?actionRef

        WHERE { 
            ?s dcterms:title ?name .
            ?s oslc:status ?enabled .
            ?s st2:triggerRef ?triggerRef .
            ?s st2:triggerType ?triggerType .
            ?s st2:actionRef ?actionRef .
        }
        
    """

    
    for name, enabled, triggerRef, triggerType, actionRef in graph.query(query_st2):
        
        rule = create_rule(name=name, enabled=enabled, triggerRef=triggerRef, triggerType=triggerType, actionRef=actionRef)
        log.warning('Rule {} created succesfully!'.format(rule['name']))
        resource = store.add_resource(service_provider, rule)
       
   
    for p, o in graph.predicate_objects(None):
        resource.rdf.add((resource.uri, p, o))
    
    return resource.rdf


def update_resource(service_provider, graph, store):
    
    query_st2 = """

        PREFIX st2_oslc: <http://localhost:5001/ns/st2_oslc#>

        SELECT ?id

        WHERE { 
            ?s st2_oslc:ruleId ?id .
        }
        
    """

    g = Graph()

    #resource_id = next(id.toPython() for id in resource.rdf.objects(resource.uri, DCTERMS.identifier))
    
    for identifier in graph.query(query_st2):
        
        updated_rule = update_rule((str(identifier.asdict()['id'].toPython())))
        log.warning('Rule {} updated succesfully!'.format(updated_rule['id']))
        
        updated_resource = store.replace_resource(service_provider, updated_rule)

    # for p, o in graph.predicate_objects(None):
    #     if p in updated_resource.rdf.predicates(None, None):
    #         for triple in updated_resource.rdf.triples((None, p, None)):
    #             updated_resource.rdf.remove(triple)
    #         updated_resource.rdf.add((updated_resource.uri, p, o))
    
    
    
    return updated_resource.rdf



def delete_resource(service_provider, graph, store):
    
    query_st2 = """

        PREFIX st2_oslc: <http://localhost:5001/ns/st2_oslc#>

        SELECT ?id

        WHERE { 
            ?s st2_oslc:ruleId ?id .
        }
        
    """

    g = Graph()

    
    for identifier in graph.query(query_st2):
        deleted_rule = get_rule_by_id(str(identifier.asdict()['id'].toPython()))
        delete_rule(str(identifier.asdict()['id'].toPython()))
        log.warning('Rule {} deleted succesfully!'.format(deleted_rule['id']))
       
        delete_resource = store.remove_resource(service_provider, deleted_rule)
        
       
        for oslc_resource in service_provider.oslc_resources:  
            if oslc_resource.id == delete_resource.id:
                #Para que se elimine de la lista de recursos
                #oslc_resource.rdf.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
                g.add((oslc_resource.uri, RDFS.comment, Literal('Deleted')))
        
    return g


