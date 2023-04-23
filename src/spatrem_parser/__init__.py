from inspect import trace
from logging import debug
import spatrem_parser.datamodels as dm
import os
from rdflib import Namespace, Graph, namespace
from shortuuid import uuid
from csv import DictReader, reader
import rdflib
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF
from rdflib.term import URIRef, Literal


NOMEN = Namespace("http://spacesoftranslation.org/ns/nomena/")
LRMoo = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
PERSON = Namespace("http://spacesoftranslation.org/ns/people/")


def name_label(name: str):
    new_name = name.replace(' ', '_')
    new_name = new_name.replace(',', '')
    new_name = new_name.replace('.', '')
    return new_name

def spatrem_graph():
    namespaces = {"nomen": NOMEN, "lrm": LRMoo, "crm": CRM, "person": PERSON}
    graph = Graph()
    for prefix, namespace in namespaces.items():
        graph.bind(prefix, namespace)
        graph.bind("nomen", NOMEN)
        graph.bind("person", PERSON)
    return graph


def create_nomen(name: str):
    """Create an rdf.Graph for name."""
    graph = spatrem_graph()
    # id = NOMEN[uuid()]
    id = NOMEN[name_label(name)]
    graph.add((id, RDF.type, LRMoo.F12_Nomen))
    graph.add((id, RDFS.label, Literal(name)))
    graph.add((id, LRMoo.R33_has_string, Literal(name)))
    return id, graph


class Translator:
    def __init__(self, translator: dm.Translator) -> None:
        self.name = translator.Surname_Name.strip()
        self.id = PERSON[name_label(self.name)]
        self.pseudonyms = None
        pseudonym_args: str | None = translator.Pseudonyms
        if pseudonym_args and pseudonym_args != "NONE":
            self.pseudonyms = [s.strip() for s in pseudonym_args.split(';')]
        self.create_graph()

    def __repr__(self) -> str:
        return f"Translator({self.name})"

    def create_graph(self):
        self.graph = spatrem_graph()
        self.graph.add((self.id, RDF.type, CRM.E21_Person))
        self.graph.add((self.id, RDFS.label, rdflib.Literal(f"{self.name}")))

class Translators:
    """A class for managing translator records/graphs.

    Translators are represented as graphs; this class is a wrapper around a
    graph that contains such graphs."""

    def __init__(self) -> None:
        self.graph = spatrem_graph()

    def get_name(self, name: str):
        try:
            return next(self.graph.subjects(predicate=RDFS.label, object=Literal(name)))
        except Exception:
            _, nomen = create_nomen(name)
            self.graph += nomen
            return next(self.graph.subjects(object=Literal(name)))

    def add_translator(self, translator: Translator):
        self.graph += translator.graph
        nomen_id, nomen = create_nomen(translator.name)
        self.graph += nomen
        self.graph.add((translator.id, LRMoo.R13_has_appellation, nomen_id))
        # Also add pseudonyms.
        if translator.pseudonyms:
            for pseudonym in translator.pseudonyms:
                nomen = self.get_name(pseudonym)
                self.graph.add((translator.id, LRMoo.R13_has_appellation, nomen))


class Translation:
    pass


with open('../../data/KA_Translators.csv', mode='r', encoding='utf-8-sig') as csvfile:
    reader: DictReader = DictReader(csvfile, delimiter=';')
    translators: list = []
    db: Translators = Translators()
    for row in reader:
        translator = Translator(dm.Translator(**row))
        translators.append(translator)
        db.add_translator(translator)

with open('/tmp/translators.ttl', mode='w', encoding='utf-8') as f:
    f.write(db.graph.serialize())
