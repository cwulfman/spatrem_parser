from typing import Optional
from rdflib import Graph, Namespace
from rdflib.term import URIRef, Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._XSD import XSD
import shortuuid
from spatrem.classes import LANGUAGES, LRM, CRM, SCHEMA, DCTERMS, SPATREM, NAMES, TYPES, PEOPLE

# LRM = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
# CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
# SCHEMA = Namespace("http://schema.org/")
# DCTERMS = Namespace("http://purl.org/dc/terms/")
# SPATREM = Namespace("http://spacesoftranslation.org/ns/spatrem/")

class BaseGraph:
    
    spatrem_namespaces = {
        "lrm": LRM,
        "crm": CRM,
        "schema": SCHEMA,
        "dcterms": DCTERMS,
        "spatrem": SPATREM,
        "name": NAMES,
        "language": LANGUAGES,
        "type": TYPES,
        "person": PEOPLE,
    }
    def __init__(self, label: Optional[str] = None,
                 namespace:str  = "spatrem") -> None:
        self.graph: Graph = Graph()
        for k, v in self.spatrem_namespaces.items():
            self.graph.bind(k, v)
        ns = self.spatrem_namespaces[namespace]
        self.id = ns[shortuuid.uuid()]
        if label:
            self.label = label
            self.graph.add((self.id, RDFS.label, Literal(label)))
        else:
            self.label = None
    
    def __repr__(self) -> str:
        if self.label:
            return f"<{self.__class__.__name__}: {self.label}>"
        else:
            return f"<{self.__class__.__name__}>"


    def __str__(self) -> str:
        return self.graph.serialize()

    def has_identifier(self, identifier: str) -> None:
        self.graph.add((self.id, DCTERMS.identifier, Literal(identifier)))

    
    def has_type(self, type: "Type") -> None:
        self.graph.add((self.id, LRM.P2_has_type, type.id))


class Type(BaseGraph):
    def __init__(self, label:str) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, CRM.E55_Type))
        self.has_identifier(label)

        
