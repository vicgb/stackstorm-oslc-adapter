from rdflib import Graph, URIRef, Literal, Namespace, DCTERMS, RDF, RDFS
from oslcapi.api.helpers.service_api import update_rule, delete_rule,load_rule, create_rule, get_rule_by_id, get_all_rules
import os
import logging


log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')
OSLC_ACTION = Namespace('http://open-services.net/ns/actions#')
token = os.getenv("TOKEN")

def create_resource(service_provider, graph, store):
    
    query_st2 = """

        
        PREFIX st2_oslc: <http://localhost:5001/ns/st2_oslc#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        SELECT ?name ?enabled ?triggerRef ?triggerType ?actionRef

        WHERE { 
            ?s st2_oslc:ruleTitle ?name .
            ?s st2_oslc:ruleStatus ?enabled .
            ?s st2_oslc:triggerRef ?triggerRef .
            ?s st2_oslc:triggerType ?triggerType .
            ?s st2_oslc:actionRef ?actionRef .
        }
        
    """

    g = Graph()
    
    for name, enabled, triggerRef, triggerType, actionRef in graph.query(query_st2):
        
        rule = create_rule(name=name, enabled=enabled, triggerRef=triggerRef, triggerType=triggerType, actionRef=actionRef)
        log.warning('Rule {} created succesfully!'.format(rule['name']))
        #resource = store.add_resource(service_provider, rule)
        g.add((OSLC_ACTION.Action, RDF.type, Literal('Create')))
        

    
    return g


def update_resource(service_provider, graph, store):
    
    query_st2 = """

        PREFIX st2_oslc: <http://localhost:5001/ns/st2_oslc#>

        SELECT ?id

        WHERE { 
            ?s st2_oslc:ruleId ?id .
        }
        
    """

    g = Graph()


    
    for identifier in graph.query(query_st2):
        
        updated_rule = update_rule((str(identifier.asdict()['id'].toPython())))
        log.warning('Rule {} updated succesfully!'.format(updated_rule['id']))
        rule_id = updated_rule['id'] 
        rules_list = []

        for rule in get_all_rules():
            rules_list.append(rule['id'])

        if rule_id == updated_rule['id']:
            pos = rules_list.index(updated_rule['id'])
            updated_resource = store.replace_resource(service_provider, updated_rule, pos)
        
        g.add((OSLC_ACTION.Action, RDF.type, Literal('Update')))
    
    return g



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
       
        
    g.add((OSLC_ACTION.Action, RDF.type, Literal('Deletion')))
    return g
   


