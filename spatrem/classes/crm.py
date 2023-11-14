from typing import Optional
from rdflib.term import Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._XSD import XSD
from spatrem.classes.base_graph import BaseGraph
from spatrem.classes import LRM, CRM, SCHEMA, DCTERMS

class Type(BaseGraph):
    def __init__(self, label: str, namespace: str = "type") -> None:
        super().__init__(label, namespace)
        self.graph.add((self.id, RDF.type, CRM.E55_Type))

class Person(BaseGraph):
    ns = "person"

    def __init__(self, key: str, persName: Optional[str] = None) -> None:
        super().__init__(label=None, namespace="person")
        self.graph.add((self.id, RDF.type, CRM.E21_Person))
        self.graph.add((self.id, DCTERMS.identifier, Literal(key)))        
        if persName:
            self.label = persName.strip()
            self.graph.add((self.id, RDFS.label, Literal(persName.strip())))


    def performed(self, activity) -> None:
        self.graph.add((self.id, CRM.P14i_performed, activity.id))


    def is_identified_by(self, nomen: "Nomen") -> None:
        self.graph.add((self.id, CRM.P1_is_identified_by, nomen.id))


    def has_birthdate(self, date: str) -> None:
        self.graph.add((self.id, SCHEMA.birthDate, Literal(date)))

    def has_deathdate(self, date: str) -> None:
        self.graph.add((self.id, SCHEMA.deathDate, Literal(date)))

    def has_gender(self, gender: str) -> None:
        self.graph.add((self.id, SCHEMA.gender, Literal(gender)))

    def has_nationality(self, nationality: str) -> None:
        self.graph.add((self.id, SCHEMA.nationality, Literal(nationality)))


class Nomen(BaseGraph):
    def __init__(self, name: str) -> None:
        super().__init__(name.strip(), 'name')

        self.graph.add((self.id, RDF.type, LRM.F12_Nomen))
        self.graph.add((self.id, LRM.R33_has_string, Literal(name)))

    def identifies(self, res) -> None:
        self.graph.add((self.id, CRM.P1_identifies, res.id))

                        
class Language(Type):
    def __init__(self, label: str) -> None:
        super().__init__(label, namespace="language")
        self.graph.add((self.id, RDF.type, CRM.E56_Language))


    


class TimeSpan(BaseGraph):
    """A class representing the CRM E52 Time Span class.

    A TimeSpan is an abstract temporal extent, with a beginning, an
    end, and a duration.  In the Spatrem records, publication dates
    are recorded as 4-digit strings (e.g., 1946).  We represent these
    as time spans, indicating that the issue was published some time
    in 1946.

    """

    def __init__(self, time_span_str: str) -> None:
        super().__init__(time_span_str)
        # The time_span parameter must be converted into an
        # XSD.duration
        duration: XSD.duration = f"P{time_span_str}Y"
        self.graph.add((self.id, RDF.type, CRM.E52_Time_Span))
        self.graph.add((self.id, CRM.P82_at_some_time_within,
                Literal(duration, datatype=XSD.duration)))


        
