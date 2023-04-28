from typing import Optional
from rdflib.namespace import Namespace, NamespaceManager
from rdflib import Graph
from rdflib.term import URIRef

spatrem_namespaces = {
    "lrm": "http://iflastandards.info/ns/lrm/lrmer/",
    "crm": "http://www.cidoc-crm.org/cidoc-crm/",
    "nomen": "http://spacesoftranslation.org/ns/nomena/",
    "person": "http://spacesoftranslation.org/ns/people/",
    "journal": "http://spacesoftranslation.org/ns/journals/",
    "issue": "http://spacesoftranslation.org/ns/issues/",
    "work": "http://spacesoftranslation.org/ns/works/",
    "translation": "http://spacesoftranslation.org/ns/translations/",
    "spatrem": "http://spacesoftranslation.org/ns/spatrem/",
}

def spatrem_graph() -> Graph:
    g = Graph()
    for k, v in spatrem_namespaces.items():
        g.bind(k, v)
    return g


class SpatremGraph:
    def __init__(self, **namespaces) -> None:
        self.graph = Graph()
        self.nsm = NamespaceManager(self.graph)
        for k, v in spatrem_namespaces.items():
            self.nsm.bind(k, v)




class SpatremClass:
    NAMESPACES = {
        "lrm": Namespace("http://iflastandards.info/ns/lrm/lrmer/"),
        "crm": Namespace("http://www.cidoc-crm.org/cidoc-crm/"),
        "nomen": Namespace("http://spacesoftranslation.org/ns/nomena/"),
        "person": Namespace("http://spacesoftranslation.org/ns/people/"),
        "journal": Namespace("http://spacesoftranslation.org/ns/journals/"),
        "issue": Namespace("http://spacesoftranslation.org/ns/issues/"),
        "work": Namespace("http://spacesoftranslation.org/ns/works/"),
        "translation": Namespace("http://spacesoftranslation.org/ns/translations/"),
        "spatrem": Namespace("http://spacesoftranslation.org/ns/spatrem/"),
    }

    def __init__(self) -> None:
        self.graph: Graph = spatrem_graph()

    def __repr__(self) -> str:
        if self.id:
            return f"<{self.id}>"
        else:
            return f"<{self.__class__.__name__}>"

    def uri_ref(self, ns_name, token) -> URIRef:
        try:
            return Namespace(dict(self.graph.namespaces())[ns_name])[token]
        except KeyError:
            return URIRef(token)



    def clean_name(self, name: str) -> str:
        new_name: str = name.replace(' ', '_')
        new_name = new_name.replace(',', '')
        new_name = new_name.replace('.', '')
        return new_name
