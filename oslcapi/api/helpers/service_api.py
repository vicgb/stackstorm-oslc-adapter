from rdflib import Graph, Literal, Namespace, DCTERMS, RDF
import os
from st2client.client import Client
from st2client import models
import json
import requests
from datetime import datetime
from posixpath import join as urljoin



OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')

ST2 = Namespace('http://localhost:5001/ns/st2_oslc#')




token = os.getenv("TOKEN")
st2_api_url = os.getenv("API_URL")
st2_api_version = os.getenv("API_VERSION")
headers = {'X-Auth-Token': token}



'''

    STACKSTORM API FUNCTIONS

'''

def get_all_rules_prueba():
    rules = client.rules.get_all()
    for rule in json.dumps(rules):
        print(rule)
    return rules

def get_all_rules():

    
    response = requests.get(urljoin(st2_api_url,st2_api_version+"/rules/"), headers=headers)
    
    return response.json()
    
def get_rule_by_id(id):

    
    response = requests.get(urljoin(st2_api_url,st2_api_version+"/rules/", id), headers=headers)  
    
    return response.json()


def delete_rule(id):
  
   
   
    response = requests.delete(urljoin(st2_api_url,st2_api_version+"/rules/", id), headers=headers)
    
    
    return response

def update_rule(id):
    
   
    query_params = get_rule_by_id(id)
    query_params["enabled"] = not query_params["enabled"]

    response = requests.put(urljoin(st2_api_url,st2_api_version+"/rules/", id), headers=headers, data=json.dumps(query_params))
   
    return response.json()

def load_rule(rule):
    
    
    response = requests.post(urljoin(api_url,api_version+"/rules/"), headers=headers, data=json.dumps(rule.to_dict()))   
    return response 




def create_rule(name, enabled, triggerRef, triggerType, actionRef):
    

    body = {
        "name": name,
        "enabled": bool(enabled),
        "trigger": {
            "ref": triggerRef,
            "type": triggerType
        },
        "action": {
            "ref": actionRef
        }
        
    }
    
    
    response = requests.post(urljoin(st2_api_url,st2_api_version+"/rules/"), headers=headers, data=json.dumps(body))  
    return response.json()


def get_st2_instance():

    return [""]


def module_to_service_provider(module, service_provider):

    service_provider.rdf.add((service_provider.uri, DCTERMS.identifier, Literal(1)))
    service_provider.rdf.add((service_provider.uri, DCTERMS.title, Literal("OSLC Stackstorm adapter")))
    service_provider.rdf.add((service_provider.uri, DCTERMS.description, Literal("OSLC Stackstorm adapter")))
    service_provider.rdf.add((service_provider.uri, DCTERMS.created, Literal(datetime.now())))
    service_provider.rdf.add((service_provider.uri, OSLC.details, Literal(st2_api_url)))

def rules_to_oslc_resource(element, resource):
     
    resource.rdf.add((resource.uri, ST2.ruleId, Literal(element['id'])))
    resource.rdf.add((resource.uri, ST2.ruleTitle, Literal(element['name'], datatype=RDF.XMLLiteral)))
    resource.rdf.add((resource.uri, ST2.ruleStatus, Literal(element['enabled'])))
    resource.rdf.add((resource.uri, ST2.ruleRef, Literal(element["ref"])))
    resource.rdf.add((resource.uri, ST2.rulePack, Literal(element["pack"])))
    resource.rdf.add((resource.uri, ST2.triggerType, Literal(element["trigger"]["type"])))
    resource.rdf.add((resource.uri, ST2.triggerRef, Literal(element["trigger"]["ref"])))
    resource.rdf.add((resource.uri, ST2.actionRef, Literal(element["action"]["ref"])))
    
    

