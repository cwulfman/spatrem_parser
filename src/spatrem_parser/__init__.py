from logging import debug
import os
from rdflib import graph, namespace
from shortuuid import uuid
from csv import DictReader, reader
import rdflib
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF
from rdflib.term import URIRef, Literal


def create_appellation(name: str):
    """Create an rdf.Graph for name."""
    graph = rdflib.Graph()
    id = rdflib.Namespace("http://spacesoftranslation.org/ns/appellations/")[uuid()]
    graph.bind('ecrm', rdflib.Namespace("http://erlangen-crm.org/200717/"))
    graph.bind(
        "appellation",
        rdflib.Namespace("http://spacesoftranslation.org/ns/appellations/"),
    )

    graph.add(
        (
            id,
            RDF.type,
            rdflib.Namespace("http://erlangen-crm.org/200717/")['E41_Appellation'],
        )
    )
    graph.add((id, RDFS.label, Literal(name)))
    return id, graph


class AppellationDb:
    """A class for maintaining a database of appellations.

    Using this class avoids duplicate appellations.
    """

    namespaces = {
        "ecrm": rdflib.Namespace("http://erlangen-crm.org/200717/"),
        "appellation": rdflib.Namespace(
            "http://spacesoftranslation.org/ns/appellations/"
        ),
    }

    def __init__(self):
        self.graph = rdflib.Graph()
        for prefix, namespace in self.namespaces.items():
            self.graph.bind(prefix, namespace)

    def get_name(self, name: str):
        try:
            return next(self.graph.subjects(object=Literal(name)))
        except:
            id, appellation = create_appellation(name)
            self.graph += appellation
            return next(self.graph.subjects(object=Literal(name)))


class Translators:
    """A class for managing translator records/graphs.

    Translators are represented as graphs; this class is a wrapper around a
    graph that contains such graphs."""

    namespaces = {
        "ecrm": rdflib.Namespace("http://erlangen-crm.org/200717/"),
        "person": rdflib.Namespace("http://spacesoftranslation.org/ns/people/"),
        "appellation": rdflib.Namespace(
            "http://spacesoftranslation.org/ns/appellations/"
        ),
    }

    def __init__(self) -> None:
        self.graph = rdflib.Graph()
        for prefix, namespace in self.namespaces.items():
            self.graph.bind(prefix, namespace)

    def get_name(self, name: str):
        try:
            return next(self.graph.subjects(predicate=RDFS.label, object=Literal(name)))
        except:
            id, appellation = create_appellation(name)
            self.graph += appellation
            return next(self.graph.subjects(object=Literal(name)))

    def add_translator(self, translator):
        self.graph += translator.graph
        id, appellation = create_appellation(translator.name)
        self.graph += appellation
        self.graph.add(
            (
                id,
                rdflib.Namespace("http://erlangen-crm.org/200717/")['P1i_identifies'],
                translator.id,
            )
        )
        # Also add pseudonyms.
        if translator.pseudonyms:
            for pseudonym in translator.pseudonyms:
                appellation = self.get_name(pseudonym)
                self.graph.add(
                    (
                        appellation,
                        rdflib.Namespace("http://erlangen-crm.org/200717/")[
                            'P1i_identifies'
                        ],
                        translator.id,
                    )
                )


class Translator:
    namespaces = {
        "ecrm": rdflib.Namespace("http://erlangen-crm.org/200717/"),
        "person": rdflib.Namespace("http://spacesoftranslation.org/ns/people/"),
    }

    def __init__(self, **kwargs) -> None:
        self.id = self.gen_id('person')
        self.name = kwargs['Surname_Name'].strip()
        self.pseudonyms = None
        pseudonym_args = kwargs['Pseudonym(s)']
        if pseudonym_args != "NONE":
            self.pseudonyms = [s.strip() for s in pseudonym_args.split(';')]
        self.create_graph()

    def __repr__(self) -> str:
        return f"Translator({self.name})"

    def namespace(self, prefix):
        return self.namespaces[prefix]

    def gen_id(self, ns):
        return self.namespace(ns)[uuid()]

    def create_graph(self):
        self.graph = rdflib.Graph()
        for prefix, namespace in self.namespaces.items():
            self.graph.bind(prefix, namespace)
        self.graph.add((self.id, RDF.type, self.namespace('ecrm')['E21_Person']))
        self.graph.add((self.id, RDFS.label, rdflib.Literal(f"{self.name}")))


with open('../../data/KA_Translators.csv', mode='r', encoding='utf-8-sig') as csvfile:
    reader = DictReader(csvfile, delimiter=';')
    translator_list = list()
    db = Translators()
    for row in reader:
        translator = Translator(**row)
        translator_list.append(translator)
        db.add_translator(translator)

with open('/tmp/translators.ttl', mode='w', encoding='utf-8') as f:
    f.write(db.graph.serialize())
