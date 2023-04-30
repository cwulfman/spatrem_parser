from typing import Optional
from pydantic import BaseModel
from rdflib import Graph, Namespace
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from rdflib.term import URIRef, Literal
from shortuuid import uuid


class Translator(BaseModel):
    Surname_Name: str
    Pseudonyms: Optional[str]
    Year_Birth: str
    Year_Death: str
    Nationality: str
    Gender: str
    Journals: Optional[str]
    Notes: str


class Translation(BaseModel):
    Journal: str
    Year: str
    Issue_ID: str
    Vol: str
    No: str
    Listed_Translator: str
    Translator: str
    Author: str
    Title: str
    Genre: str
    SL: str
    TL: str
    Notes: str


class BaseGraph:
    lrm: Namespace = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
    crm: Namespace = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
    spatrem: Namespace = Namespace("http://spacesoftranslation.org/ns/spatrem/")

    def __init__(self, label: Optional[str] = None) -> None:
        self.graph = Graph()
        self.graph.bind("lrm", "http://iflastandards.info/ns/lrm/lrmer/")
        self.graph.bind("crm", "http://www.cidoc-crm.org/cidoc-crm/")
        self.graph.bind("spatrem", "http://spacesoftranslation.org/ns/spatrem/")

        self._id: URIRef

        if label is None:
            self.label = uuid()
        else:
            self.label = label.strip()

        self.id = self.spatrem[self.clean_id(self.label)]
        self.graph.add((self.id, RDFS.label, Literal(self.label)))

    def clean_id(self, id_string: str) -> str:
        id = id_string.strip()
        id = id.replace(' ', '_')
        id = id.replace(',', '')
        id = id.replace(':', '')
        id = id.replace(';', '')
        id = id.replace('.', '')
        return id

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.label}>"

    def __str__(self) -> str:
        return self.graph.serialize()

    @property
    def id(self) -> URIRef:
        return self._id

    @id.setter
    def id(self, iri: URIRef) -> None:
        self._id = iri


class LrmGraph(BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDFS.label, Literal(self.label)))


class CrmGraph(BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDFS.label, Literal(self.label)))


class Work(LrmGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, self.lrm.F1_Work))

    def is_realised_by(self, expr: "Expression") -> None:
        self.graph.add((self.id, self.lrm.R3i_is_realised_by, expr.id))

    def has_part(self, work: "Work") -> None:
        self.graph.add((self.id, self.lrm.R67_has_part, work.id))

    def is_part_of(self, work: "Work") -> None:
        self.graph.add((self.id, self.lrm.R67i_is_part_of, work.id))


class SerialWork(Work):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.remove((self.id, RDF.type, self.lrm.F1_Work))
        self.graph.add((self.id, RDF.type, self.lrm.F18_Serial_Work))


class Expression(LrmGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, self.lrm.F2_Expression))
        self.graph.add((self.id, RDFS.label, Literal(label)))

    def realises(self, work: Work) -> None:
        self.graph.add((self.id, self.lrm.R3_realises, work.id))


class Nomen(LrmGraph):
    def __init__(self, name: str, label: Optional[str] = None) -> None:
        if label:
            super().__init__(label)
        else:
            super().__init__(name)

        self.graph.add((self.id, RDF.type, self.lrm.F12_Nomen))
        self.graph.add((self.id, self.lrm.R33_has_string, Literal(name)))


class Person(CrmGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, self.crm.E21_Person))
