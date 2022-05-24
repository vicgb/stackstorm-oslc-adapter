from st2client.client import Client
#Trigger, Rule, Action, Execution, and KeyValuePair are defined under st2client.models
from st2client import models
from st2client.models import Rule
from dotenv import load_dotenv
load_dotenv()
import os
from posixpath import join as urljoin
import json
import requests



token = os.getenv("TOKEN")
api_url = os.getenv("API_URL")
api_version = os.getenv("API_VERSION")
stream_url = os.getenv("STREAM_URL")
headers = {'X-Auth-Token': token}




client = Client(api_url= api_url, token=token)


def get_all_rules_objects():
    rules = client.rules.get_all()
    print(rules)
    return rules


def get_rule_by_id_object(id):
    rule = client.rules.get_by_id(id)
    print(rule)
    return rule


def get_all_executions():
    executions = client.executions.get_all()
    return executions

def get_all_actions():
    actions = client.actions.get_all()
    return actions


#######
# Rules 
# Two ways: Python CLI rules.get_all() returns a Rule object
#           HTTP request returns a JSON with all rule parameters
#######


def get_all_rules():

    response = requests.get(urljoin(api_url,api_version+"/rules/"), headers=headers)
    print(response.json())
    return response.json()
    
def get_rule_by_id(id):

    response = requests.get(urljoin(api_url,api_version+"/rules/", id), headers=headers)
    print(response.json())
    return response.json()


def delete_rule(id):
  
    response = requests.delete(urljoin(api_url,api_version+"/rules/", id), headers=headers)
    return response

def update_rule(id):
    
    headers = {"X-Auth-Token": token}
    query_params = get_rule_by_id(id)
    query_params["enabled"] = not query_params["enabled"]

    response = requests.put(urljoin(api_url,api_version+"/rules/", id), headers=headers, data=json.dumps(query_params))
    print(response.json())
    return response
  
def load_rule(rule):
    
    headers = {"X-Auth-Token": token}

    response = requests.post(urljoin(api_url,api_version+"/rules/"), headers=headers, data=json.dumps(rule.to_dict()))   
    
    return response

def create_rule(title, status, triggerRef, triggerType, actionRef):
    
    body = {
        "name": title,
        "enabled": status,
        "trigger": {
            "ref": triggerRef,
            "type": triggerType
        },
        "action": {
            "ref": actionRef
           
        }
        
    }
    

    response = requests.post(urljoin(api_url,api_version+"/rules/"), headers=headers, data=json.dumps(body))  
    
    return response

def stream_logs():
    headers = {"X-Auth-Token": token}

    response = requests.get("http://localhost/stream/v1/stream?events=st2.liveaction__create", headers=headers)  
    print(response.json())
    return response.json()


#"name", "pack", "trigger", "criteria", "enabled"]
#new_rule = models.Rule(name="prueba", ref="linux.prueba", pack="chatops",action={'ref': 'chatops.notify'},trigger={'type': 'core.st2.generic.notifytrigger', 'parameters': {}, 'ref': 'core.st2.generic.notifytrigger'},criteria={'trigger.route': {'pattern': 'hubot', 'type': 'equals'}},enabled=False)
create_rule("prueba5", False, "core.st2.generic.notifytrigger","core.st2.generic.notifytrigger", "chatops.notify")

#stream_logs()
#delete_rule("62531f7fac2af13ef158c6ee")
#stream_logs()

#st2.actionexecutionstate__create
# st2.actionexecutionstate__update
# st2.actionexecutionstate__delete
# st2.execution__create
# st2.execution__update
# st2.execution__delete
# st2.execution.output__create
# st2.execution.output__update
# st2.execution.output__delete
# st2.liveaction__create
# st2.liveaction__update
# st2.liveaction__delete
# st2.liveaction.status__<state>
# st2.workflow__create
# st2.workflow__update
# st2.workflow__delete
# st2.workflow.status__<state>
# st2.sensor__create
# st2.sensor__update
# st2.sensor__delete
# st2.trigger__create
# st2.trigger__update
# st2.trigger__delete
# st2.trigger_instances_dispatch__trigger_instance
# st2.announcement__chatops
# st2.announcement__<route in announcement_runner>