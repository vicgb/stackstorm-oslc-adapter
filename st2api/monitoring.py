from pymongo import MongoClient
import pymongo
from bson.json_util import dumps
import os
import requests
import json

mongo_url = os.getenv("MONGO_URL")
mongo_replicaset = os.getenv("MONGO_REPLICASET")
token = os.getenv("TOKEN")

headers = {'X-Auth-Token': token}

def get_database():
    

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb://fd6bd9c7f88c:27017"
 
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    
    client = pymongo.MongoClient(CONNECTION_STRING, replicaset='rs')
    
    # Create the database for our example (we will use the same database throughout the tutorial
    
    return client

def get_mongo_rules():
    
    dbname = get_database()
    rule_collection = dbname["rule_d_b"]
    
    

    return rule_collection


def stream_mongo():

    client = pymongo.MongoClient("mongodb://fd6bd9c7f88c:27017", replicaset='rs')
    headers = headers
    # db: st2
    # collection: rule_d_b 
    change_stream = client.st2.rule_d_b.watch()
    
    for change in change_stream:
        
        requests.post("http://localhost:5000/service/ST2Logs", headers=headers, data=dumps(change))
        print(change)

stream_mongo()


