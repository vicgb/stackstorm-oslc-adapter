from rdflib import Graph, URIRef, Namespace, Literal, DCTERMS
from oslcapi.api.helpers.service_api import rules_to_oslc_resource
#from github import Github
from rdflib.namespace import DCTERMS, RDF
import os
import logging

log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')

token = os.getenv("GITHUB_TOKEN")

def generate_creation_event(payload, store):
    log.warning('Creation event generated')

    g = Github(token)
    repo = g.get_repo(payload['repository']['id'])
    issue = repo.get_issue(payload['issue']['number'])

    service_provider = next(service_provider for service_provider in store.catalog.service_providers if Literal(repo.id) in service_provider.rdf.objects(None, DCTERMS.identifier))

    
    resource = store.add_resource(service_provider, issue)
    store.trs.generate_change_event(resource, 'Creation')

    return

def generate_modification_event(payload, store):
    log.warning('Modification event generated')

    g = Github(token)
    repo = g.get_repo(payload['repository']['id'])
    issue = repo.get_issue(payload['issue']['number'])

    service_provider = next(service_provider for service_provider in store.catalog.service_providers if Literal(repo.id) in service_provider.rdf.objects(None, DCTERMS.identifier))
    resource = next(resource for resource in service_provider.oslc_resources if Literal(issue.number) in resource.rdf.objects(None, DCTERMS.identifier))

    service_provider.oslc_resources.remove(resource)

    resource = store.add_resource(service_provider, issue)
    store.trs.generate_change_event(resource, 'Modification')

    return

def generate_deletion_event(payload, store):
    log.warning('Deletion event generated')
    log.warning(payload)

    g = Github(token)
    return