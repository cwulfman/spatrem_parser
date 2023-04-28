from typing import List
import spatrem_parser.datamodels as dm
from rdflib import Namespace, Graph
from csv import DictReader
import rdflib
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF
from rdflib.term import URIRef, Literal

spatrem_namespaces = {
    "nomen": Namespace("http://spacesoftranslation.org/ns/nomena/"),
    "lrm": Namespace("http://iflastandards.info/ns/lrm/lrmer/"),
    "crm": Namespace("http://www.cidoc-crm.org/cidoc-crm/"),
    "person": Namespace("http://spacesoftranslation.org/ns/people/"),
    "journal": Namespace("http://spacesoftranslation.org/ns/journals/"),
    "issue": Namespace("http://spacesoftranslation.org/ns/issues/"),
    "work": Namespace("http://spacesoftranslation.org/ns/works/"),
    "translation": Namespace("http://spacesoftranslation.org/ns/translations/"),
    "spatrem": Namespace("http://spacesoftranslation.org/ns/spatrem/"),
}

NOMEN = Namespace("http://spacesoftranslation.org/ns/nomena/")
LRMoo = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
PERSON = Namespace("http://spacesoftranslation.org/ns/people/")
JOURNAL = Namespace("http://spacesoftranslation.org/ns/journals/")
ISSUE = Namespace("http://spacesoftranslation.org/ns/issues/")
WORK = Namespace("http://spacesoftranslation.org/ns/works/")
TRANSLATION = Namespace("http://spacesoftranslation.org/ns/translations/")
SPATREM = Namespace("http://spacesoftranslation.org/ns/spatrem/")


def clean_name(name: str) -> str:
    new_name = name.replace(' ', '_')
    new_name = new_name.replace(',', '')
    new_name = new_name.replace('.', '')
    return new_name


def spatrem_graph():
    namespaces = {
        "nomen": NOMEN,
        "lrm": LRMoo,
        "crm": CRM,
        "person": PERSON,
        "journal": JOURNAL,
        "issue": ISSUE,
        "work": WORK,
        "translation": TRANSLATION,
        "spatrem": SPATREM,
    }
    graph = Graph()
    for prefix, namespace in namespaces.items():
        graph.bind(prefix, namespace)
    return graph


# class Translator:
#     def __init__(self, translator: dm.Translator) -> None:
#         self.name = clean_name(translator.Surname_Name)
#         self.id = PERSON[clean_name(self.name)]
#         self.pseudonyms = None
#         pseudonym_args: str | None = translator.Pseudonyms
#         if pseudonym_args and pseudonym_args != "NONE":
#             self.pseudonyms = [clean_name(s) for s in pseudonym_args.split(';')]
#         self.create_graph()

#     def __repr__(self) -> str:
#         return f"Translator({self.name})"

#     def create_graph(self):
#         self.graph = spatrem_graph()
#         self.graph.add((self.id, RDF.type, CRM.E21_Person))
#         self.graph.add((self.id, RDFS.label, rdflib.Literal(f"{self.name}")))


class Nomen:
    def __init__(self, name: str) -> None:
        self.graph = spatrem_graph()
        self.id = NOMEN[clean_name(name)]
        self.graph.add((self.id, RDF.type, LRMoo.F12_Nomen))
        self.graph.add((self.id, RDFS.label, Literal(name)))
        self.graph.add((self.id, LRMoo.R33_has_string, Literal(name)))


class Person:
    def __init__(self, name: str) -> None:
        self.graph = spatrem_graph()
        self.id = PERSON[clean_name(name)]
        self.graph.add((self.id, RDF.type, CRM.E21_Person))
        self.graph.add((self.id, RDFS.label, Literal(name)))


class Translator:
    def __init__(self, data: dm.Translation) -> None:
        self.graph = spatrem_graph()
        if data.Translator and data.Translator != "NONE":
            names = [name for name in data.Translator.split(";")]
            for name in names:
                self.graph += Nomen(name).graph
                self.graph += Person(name).graph
        if data.Listed_Translator and data.Listed_Translator != "NONE":
            names: List[str] = [
                clean_name(name) for name in data.Listed_Translator.split(";")
            ]
            for name in names:
                self.graph += Nomen(name).graph


class Journal:
    def __init__(self, name: str) -> None:
        self.id = JOURNAL[name]
        self.graph: Graph = spatrem_graph()
        self.graph.add((self.id, RDF.type, LRMoo.F18_Serial_Work))

        expr_id = SPATREM[f"{name}_expr"]
        self.graph.add((expr_id, RDF.type, LRMoo.F2_Expression))
        self.graph.add((expr_id, LRMoo.R3_realises, self.id))
        self.graph.add((self.id, LRMoo.R3i_is_realised_by, expr_id))


class Issue:
    def __init__(self, data: dm.Translation) -> None:
        self.id: URIRef = ISSUE[f"{data.Journal}_{data.Issue_ID}"]
        journal = Journal(data.Journal)
        self.graph: Graph = spatrem_graph()
        self.graph.add((self.id, RDF.type, LRMoo.F1_Work))
        self.graph.add((journal.id, LRMoo.R67_has_part, self.id))

        # Add the expression Graph
        expr_id = SPATREM[f"{data.Journal}_{data.Issue_ID}_expr"]
        self.graph.add((expr_id, RDF.type, LRMoo.F2_Expression))
        self.graph.add((expr_id, LRMoo.R3_realises, self.id))
        self.graph.add((self.id, LRMoo.R3i_is_realised_by, expr_id))


class Translation:
    def __init__(self, data: dm.Translation) -> None:
        self.data: dm.Translation = data
        self.create_graph()

    def __repr__(self) -> str:
        return f"Translation({self.data.Title})"

    def create_graph(self) -> None:
        self.id: URIRef = TRANSLATION[clean_name(self.data.Title)]
        self.graph = spatrem_graph()
        journal = Journal(self.data.Journal)
        self.graph += journal.graph
        issue = Issue(self.data)
        self.graph += issue.graph

        self.graph += Translator(self.data).graph

        self.graph.add((self.id, RDF.type, LRMoo.F1_Work))
        self.graph.add(
            (self.id, RDFS.label, rdflib.Literal(clean_name(self.data.Title)))
        )
        self.graph.add((issue.id, LRMoo.R67_has_part, self.id))
        self.graph.add((self.id, LRMoo.R67i_is_part_of, issue.id))

        # add the expression statements

        expr_id: URIRef = SPATREM[f"{clean_name(self.data.Title)}_expr"]
        self.graph.add((expr_id, RDF.type, LRMoo.F2_Expression))
        self.graph.add((expr_id, LRMoo.R3_realises, self.id))
        self.graph.add((self.id, LRMoo.R3i_is_realised_by, expr_id))
        self.graph.add((expr_id, LRMoo.R23i_is_part_of, journal.id))
        self.graph.add((journal.id, LRMoo.R23_has_part, expr_id))


# with open('../data/KA_Translations.csv', mode='r', encoding='utf-8-sig') as csvfile:
#     reader: DictReader = DictReader(csvfile, delimiter=';')
#     translations: List[Translation] = []
#     for row in reader:
#         translations.append(Translation(dm.Translation(**row)))

# with open('../../data/KA_Translators.csv', mode='r', encoding='utf-8-sig') as csvfile:
#     reader: DictReader = DictReader(csvfile, delimiter=';')
#     translators: list = []
#     db: Translators = Translators()
#     for row in reader:
#         translator = Translator(dm.Translator(**row))
#         translators.append(translator)
#         db.add_translator(translator)

# with open('/tmp/translators.ttl', mode='w', encoding='utf-8') as f:
#     f.write(db.graph.serialize())

# g = spatrem_graph()
# for dm_translation in translations:
#     translation = Translation(dm_translation.data)
#     g += translation.graph

# with open('/tmp/translations.ttl', mode='w', encoding='utf-8') as f:
#     f.write(g.serialize())
