from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import DCTERMS, RDF
from datetime import datetime
import logging

log = logging.getLogger('tester.sub')

TRS = Namespace('http://open-services.net/ns/core/trs#')
LDP = Namespace('http://www.w3.org/ns/ldp#')

base_url = 'http://localhost:5001'


class TRSStore:
    def __init__(self):
        self.rdf = Graph()
        self.uri = URIRef(base_url+'/service/trackedResourceSet')

        self.change_logs = []
        self.change_events = []

        self.rdf.add((self.uri, RDF.type, TRS.TrackedResourceSet))

        self.change_log = BNode()

        self.rdf.add((self.uri, TRS.changeLog, self.change_log))
        self.rdf.add((self.change_log, RDF.type, TRS.ChangeLog))

        self.base = TRSBase()

        self.rdf.add((self.uri, TRS.base, self.base.uri))


    def initialize_trs(self, catalog):
        for service_provider in catalog.service_providers:
            for resource in service_provider.oslc_resources:
                self.base.rdf.add((self.base.uri, LDP.member, resource.uri))

        log.warning('TRS store loaded')

    def generate_change_event(self, resource, action):
        # order = len(self.change_logs)*3 + len(self.change_logs[len(self.change_logs)-1].change_events)
        order = len(self.change_events) + 1
        for change_log in self.change_logs:
            order += len(change_log.change_events) 
            print(change_log)
        change_event_uri = URIRef('urn:cm1.example.com:'+datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))

        self.rdf.add((self.change_log, TRS.change, change_event_uri))
        self.rdf.add((change_event_uri, RDF.type, TRS[action]))
        self.rdf.add((change_event_uri, TRS.changed, resource.uri))
        self.rdf.add((change_event_uri, TRS.order, Literal(order)))

        self.change_events.insert(0, change_event_uri)

        if len(self.change_events) > 3:
            change_event_uri = self.change_events.pop()
            graph = Graph()

            self.rdf.remove((None, TRS.change, change_event_uri))
            for triple in self.rdf.triples((change_event_uri, None, None)):
                graph.add(triple)
                self.rdf.remove(triple)

            n = 1
            while change_event_uri:

                if n > len(self.change_logs):
                    new_change_log = ChangeLog(n)

                    if n == 1:
                        self.rdf.add((self.change_log, TRS.previous, new_change_log.uri))
                    else:
                        self.change_logs[n-2].previous(new_change_log)
                        

                    self.change_logs.append(new_change_log)

                change_event_uri = self.change_logs[n-1].add_change_event(change_event_uri, graph)
                n += 1


class TRSBase:
    def __init__(self):
        self.rdf = Graph()
        self.uri = URIRef(base_url+'/service/baseResources')

        self.rdf.add((self.uri, RDF.type, LDP.DirectContainer))
        self.rdf.add((self.uri, LDP.hasMemberRelation, LDP.member))
        self.rdf.add((self.uri, TRS.cutoffEvent, RDF.nil))


class ChangeLog:
    def __init__(self, n):
        self.rdf = Graph()
        self.uri = URIRef(base_url+'/service/changeLog/'+str(n))

        self.change_events = []

        self.rdf.add((self.uri, RDF.type, TRS.ChangeLog))

    def add_change_event(self, change_event_uri, graph):

        self.change_events.insert(0, change_event_uri)

        self.rdf.add((self.uri, TRS.change, change_event_uri))
        for triple in graph.triples((None, None, None)):
            self.rdf.add(triple)
            graph.remove(triple)

        if len(self.change_events) > 3:
            change_event_uri = self.change_events.pop()

            self.rdf.remove((None, TRS.change, change_event_uri))
            for triple in self.rdf.triples((change_event_uri, None, None)):
                self.rdf.remove(triple)
                graph.add(triple)
            
            return change_event_uri
        
        else:
            return None


    def previous(self, previous):
        self.rdf.add((self.uri, TRS.previous, previous.uri))