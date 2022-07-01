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


def stream_mongo():

    client = pymongo.MongoClient("mongodb://"+mongo_url, replicaset=mongo_replicaset)


    # db: st2
    # collection: rule_d_b 
    change_stream = client.st2.rule_d_b.watch()
    
    for change in change_stream:
        
        requests.post("http://localhost:5000/service/ST2Logs", headers=headers, data=dumps(change))
      

stream_mongo()


