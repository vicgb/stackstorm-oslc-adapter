from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import DCTERMS, RDF
from datetime import datetime
import os
import logging
from oslcapi.api.helpers.service_api import get_rule_by_id, create_rule, get_all_rules, update_rule, load_rule, delete_rule, get_st2_instance



log = logging.getLogger('tester.sub')

OSLC = Namespace('http://open-services.net/ns/core#')
OSLC_CM = Namespace('http://open-services.net/ns/cm#')
TRS = Namespace('http://open-services.net/ns/core/trs#')
LDP = Namespace('http://www.w3.org/ns/ldp#')
# XMLS = Namespace('http://www.w3.org/2001/XMLSchema#')


base_url = 'http://localhost:5000'

class OSLCStore:
    def __init__(self):
        self.store = Graph()

        discover_service_providers(self.store)
        discover_oslc_resources(self.store)
        build_trs_store(self.store)
        log.warning('Store loaded')

    def generate_change_event(self, resource, action):
        change_events = []
        for change in self.store.query("""

            PREFIX trs: <http://open-services.net/ns/core/trs#>

            SELECT ?change_event

            WHERE {
                ?s trs:change ?change_event .
                ?change_event trs:order ?order
            }

            ORDER BY ?order

        """):
            change_events.append(change)

        order = len(change_events)+1
        change_log = None
        for o in self.store.objects(None, TRS.changeLog):
            change_log = o
        last_change_event = Literal('urn:cm1.example.com:'+datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

        self.store.add((change_log, TRS.change, last_change_event))
        self.store.add((last_change_event, RDF.type, TRS[action]))
        self.store.add((last_change_event, TRS.changed, resource))
        self.store.add((last_change_event, TRS.order, Literal(order)))

        n = 1
        order = order - 3
        while order > 0:
            n += 1
            change_event = change_events[order-1][0]
            next_log = change_log
            change_log = URIRef(base_url+'/service/changeLog/'+str(n))
            
            self.store.remove((None, TRS.change, change_event))
            self.store.add((next_log, TRS.previous, change_log))
            self.store.add((change_log, TRS.change, change_event))

            order -= 3



def discover_service_providers(store):

    # Translate from tool api to service provider
    sp_catalog_uri = URIRef(base_url+'/service/serviceProviders/catalog')

    store.add((sp_catalog_uri, DCTERMS.title, Literal('StackStorm OSLC Server')))
    store.add((sp_catalog_uri, DCTERMS.description, Literal('A server that provides OSLC capabilities to Stackstorm')))
    store.add((sp_catalog_uri, RDF.type, OSLC.ServiceProviderCatalog))
    store.add((sp_catalog_uri, OSLC.domain, URIRef('http://open-services.net/ns/cm#')))
    

    g = Github(token)
    for rule in g.get_user().get_repos():

        sp_uri = URIRef(base_url+'/service/serviceProviders/'+str(repo.id))
        store.add((sp_catalog_uri, OSLC.serviceProvider, sp_uri))

        module_to_service_provider(repo, store)

    return

def discover_oslc_resources(store):

    g = Github(token)
    for repo in g.get_user().get_repos():
        for issue in repo.get_issues():
            element_to_oslc_resource(issue, repo, store)

    return

def build_trs_store(store):

    # Translate from tool api to oslc resource
    trs_uri = URIRef(base_url+'/service/trackedResourceSet')
    change_log = BNode()

    store.add((trs_uri, RDF.type, TRS.TrackedResourceSet))
    store.add((trs_uri, TRS.base, URIRef(base_url+'/service/baseResources')))
    store.add((trs_uri, TRS.changeLog, change_log))
    store.add((change_log, RDF.type, TRS.ChangeLog))

    base_uri = URIRef(base_url+'/service/baseResources')

    store.add((base_uri, RDF.type, LDP.DirectContainer))
    store.add((base_uri, LDP.hasMemberRelation, LDP.member))
    store.add((base_uri, TRS.cutoffEvent, RDF.nil))

    for resource in store.subjects(RDF.type, OSLC_CM.ChangeRequest):
        store.add((base_uri, LDP.member, resource))

    return

def module_to_service_provider(module, store):

    sp_uri = URIRef(base_url+'/service/serviceProviders/'+str(module.id))

    store.add((sp_uri, DCTERMS.identifier, Literal(module.id)))
    store.add((sp_uri, DCTERMS.title, Literal(module.name)))
    store.add((sp_uri, DCTERMS.description, Literal(module.description)))
    store.add((sp_uri, DCTERMS.created, Literal(module.created_at)))
    store.add((sp_uri, RDF.type, OSLC.ServiceProvider))
    store.add((sp_uri, OSLC.details, Literal(module.html_url)))

    service = BNode()

    store.add((sp_uri, OSLC.service, service))
    store.add((service, RDF.type, OSLC.Service))
    store.add((service, OSLC.domain, URIRef('http://open-services.net/ns/cm#')))

    creationFactory = BNode()

    store.add((service, OSLC.creationFactory, creationFactory))
    store.add((creationFactory, RDF.type, OSLC.CreationFactory))
    store.add((creationFactory, OSLC.resourceType, OSLC_CM.ChangeRequest))
    store.add((creationFactory, OSLC.label, Literal('Creation Factory')))
    store.add((creationFactory, OSLC.creation, URIRef(base_url+'/service/serviceProviders/'+str(module.id)+'/changeRequests')))

    queryCapability = BNode()

    store.add((service, OSLC.queryCapability, queryCapability))
    store.add((queryCapability, RDF.type, OSLC.QueryCapability))
    store.add((queryCapability, OSLC.resourceType, OSLC_CM.ChangeRequest))
    store.add((queryCapability, OSLC.label, Literal('Query Capability')))
    store.add((queryCapability, OSLC.queryBase, URIRef(base_url+'/service/serviceProviders/'+str(module.id)+'/changeRequests')))

    return sp_uri

def element_to_oslc_resource(element, module, store):

    sp_uri = URIRef(base_url+'/service/serviceProviders/'+str(module.id))
    resource_uri = URIRef(base_url+'/service/serviceProviders/'+str(module.id)+'/changeRequests/'+str(element.number))

    store.add((resource_uri, OSLC.serviceProvider, sp_uri))
    store.add((resource_uri, RDF.type, OSLC_CM.ChangeRequest))
    store.add((resource_uri, DCTERMS.identifier, Literal(element.number)))
    store.add((resource_uri, DCTERMS.title, Literal(element.title)))
    store.add((resource_uri, DCTERMS.description, Literal(element.body)))
    store.add((resource_uri, DCTERMS.created, Literal(element.created_at)))
    store.add((resource_uri, DCTERMS.modified, Literal(element.updated_at)))
    store.add((resource_uri, DCTERMS.contributor, Literal(element.user.name)))
    store.add((resource_uri, OSLC_CM.status, Literal(element.state)))

    return resource_uri
