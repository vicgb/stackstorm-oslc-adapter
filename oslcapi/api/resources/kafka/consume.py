# importing the required modules  
from json import loads  
from kafka import KafkaConsumer  
import pymongo
from pymongo import MongoClient  

# generating the Kafka Consumer  
my_consumer = KafkaConsumer(  
    'testnum',  
        bootstrap_servers = ['localhost:29092'],  
        auto_offset_reset = 'earliest',  
        enable_auto_commit = True,  
        group_id = 'my-group',  
        value_deserializer = lambda x : loads(x.decode('utf-8'))  
        )  


 # Provide the mongodb atlas url to connect python to mongodb using pymongo
CONNECTION_STRING = "mongodb://fd6bd9c7f88c:27017"
 
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    
my_client = pymongo.MongoClient(CONNECTION_STRING)
my_collection = my_client.testnum.testnum  

for message in my_consumer:  
    message = message.value  
    my_collection.insert_one(message)  
    print(message + " added to " + my_collection)  