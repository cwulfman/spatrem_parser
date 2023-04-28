from typing import Optional
from rdflib.namespace import Namespace, NamespaceManager
from rdflib import Graph
from rdflib.term import URIRef
from rdflib.util import from_n3

class SpatremGraph:
    def __init__(self, **namespaces) -> None:
        self.graph = Graph()
        for k, v in namespaces.items():
            self.graph.bind(k, v)
        self.nsm = NamespaceManager(self.graph)

    def term(self, term_string):
        return from_n3(term_string, self.nsm)
