from typing import Optional
from rdflib import Namespace, Graph
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF
from rdflib.term import URIRef, Literal
from spatrem_parser.spatrem import SpatremClass
from spatrem_parser.lrm_classes import Expression, SerialWork, Work


class Journal(SpatremClass):
    def __init__(self, journal_id: str, **kwargs) -> None:
        super().__init__()
        self.id: URIRef = self.uri_ref("journal", journal_id)
        serial_work = SerialWork(self.id)
        self.graph += serial_work.graph

        if "Journal" in kwargs:
            name = kwargs['Journal']
        else:
            name = "Unnamed"

        self.graph.add((self.id, RDFS.label, Literal(name)))
        expr = Expression(
            self.uri_ref("spatrem", f"{name}_expr"),
            label=f"expression of {name}",
        )
        self.graph += expr.graph
        self.graph.add((expr.id, RDF.type, self.uri_ref("lmr", "F2_Expression")))
        self.graph.add((expr.id, self.uri_ref("lmr", "R3_realises"), self.id))
        self.graph.add((self.id, self.uri_ref("lmr", "R3i_is_realised_by"), expr.id))


class Issue(SpatremClass):
    def __init__(self, journal_id: str, issue_id: str) -> None:
        super().__init__()
        self.id: URIRef = self.uri_ref("issue", f"{journal_id}_{issue_id}")
        self.graph += Work(self.id).graph

        journal: Journal = Journal(journal_id)
        self.graph += journal.graph

        self.graph.add((journal.id, self.uri_ref("lmr", "R67_has_part"), self.id))
        self.graph.add((self.id, self.uri_ref("lmr", "R67i_is_part_of"), journal.id))

        # Add the expression Graph
        spatrem = self.NAMESPACES['spatrem']
        expr_id = self.uri_ref("spatrem", f"{journal_id}_{issue_id}_expr")
        expr = Expression(expr_id, labeel=f"expression of {journal_id}_{issue_id}")
        self.graph += expr.graph

        self.graph.add((expr.id, self.uri_ref("lmr", "R3_realises"), self.id))
        self.graph.add((self.id, self.uri_ref("lmr", "R3i_is_realised_by"), expr.id))
