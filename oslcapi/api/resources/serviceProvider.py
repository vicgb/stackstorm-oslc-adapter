from oslcapi.store import store
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask_rdf.flask import returns_rdf
from rdflib import Graph
import logging

log = logging.getLogger('tester.sub')

class ServiceProvider(Resource):
    @returns_rdf
    def get(self, service_provider_id):
        for service_provider in store.catalog.service_providers:
            if service_provider.id == service_provider_id:
                return service_provider.rdf

        return Graph()


class ServiceProviderCatalog(Resource):
    @returns_rdf
    def get(self):
        return store.catalog.rdf
