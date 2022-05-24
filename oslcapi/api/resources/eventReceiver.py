from oslcapi.api.helpers import generate_creation_event, generate_modification_event, generate_deletion_event
from oslcapi.store import store
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_rdf.flask import returns_rdf
import json
import logging

log = logging.getLogger('tester.sub')

# "Server" que procesa el post que le llega del adaptador, lo trata y ejecuta el evento correspondiente. 
# Lo que le llegará aquí será una acción. El adaptador genera eventos. 
class EventReceived(Resource):
    def post(self):
        payload = json.loads(request.data)
        
        action = payload['action']

        if action == 'opened':
            return generate_creation_event(payload, store)

        elif action == 'edited':
            return generate_modification_event(payload, store)
            
        elif action == 'deleted':
            return generate_deletion_event(payload, store)
            
        else:
            return
        