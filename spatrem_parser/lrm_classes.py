from rdflib import Graph, Namespace
import rdflib
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF
from rdflib.term import URIRef, Literal
from spatrem_parser.spatrem import SpatremClass


class Work(SpatremClass):
    def __init__(self, id: URIRef, **kwargs) -> None:
        super().__init__()
        self.id: URIRef = id
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F1_Work")))


class SerialWork(SpatremClass):
    def __init__(self, id: URIRef, **kwargs) -> None:
        super().__init__()
        self.id: URIRef = id
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F18_Serial_Work")))


class Expression(SpatremClass):
    def __init__(self, id: URIRef, **kwargs) -> None:
        super().__init__()
        self.id: URIRef = id
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F2_Expression")))


class Nomen(SpatremClass):
    def __init__(self, id: URIRef, name: str, **kwargs) -> None:
        super().__init__()
        self.id: URIRef = id
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F12_Nomen")))
        self.graph.add((self.id, RDFS.label, Literal(kwargs["name"])))
        self.graph.add(
            (
                self.id,
                self.uri_ref("lrm", "R33_has_string"),
                Literal(kwargs["name"]),
            )
        )


class Person(SpatremClass):
    def __init__(self, id: URIRef, name: str, **kwargs) -> None:
        super().__init__()
        self.id: URIRef = id
        self.graph.add((self.id, RDFS.label, Literal(name)))
        self.graph.add((self.id, RDF.type, self.uri_ref("crm", "E21_Person")))
