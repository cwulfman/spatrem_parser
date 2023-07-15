from typing import Optional
from rdflib import Graph, Namespace
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._XSD import XSD
from rdflib.term import URIRef, Literal
import re
import uuid


# def duration_from_year(year: str) -> XSD.duration:
#     return f"P{year}Y"


def gen_id(string: str) -> str:
    return str(uuid.uuid3(uuid.NAMESPACE_X500, re.sub(r"\W", "", string)))


class BaseGraph:
    """Base class for Spatrem graphs.

    The base class contains all the namespaces and an __init__
    method that creates an rdflib graph and binds the namespaces
    to prefixes.  It also contains a common utility method for
    de-tainting strings so they can be used as identifiers.
    """

    spatrem_namespaces = {
        "lrm": "http://iflastandards.info/ns/lrm/lrmer/",
        "crm": "http://www.cidoc-crm.org/cidoc-crm/",
        "schema": "http://schema.org/",
        "nomen": "http://spacesoftranslation.org/ns/nomena/",
        "person": "http://spacesoftranslation.org/ns/people/",
        "journal": "http://spacesoftranslation.org/ns/journals/",
        "issue": "http://spacesoftranslation.org/ns/issues/",
        "work": "http://spacesoftranslation.org/ns/works/",
        "expression": "http://spacesoftranslation.org/ns/expressions/",
        "translation": "http://spacesoftranslation.org/ns/translations/",
        "spatrem": "http://spacesoftranslation.org/ns/spatrem/",
    }

    ns = "spatrem"

    def __init__(self, label: Optional[str] = None) -> None:
        self.graph = Graph()
        for k, v in self.spatrem_namespaces.items():
            self.graph.bind(k, v)

        if label is None:
            self.key = str(uuid.uuid4())
        else:
            self.label = label.strip()
            self.key = gen_id(self.label)

        self.id: URIRef = self.uri_ref(self.ns, self.key)

        if label:
            self.graph.add((self.id, RDFS.label, Literal(self.label)))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.label}>"

    def __str__(self) -> str:
        return self.graph.serialize()

    def clean(self, dirty_string: str) -> str:
        return re.sub(r"\W", "", dirty_string)

    def uri_ref(self, ns_name: str, token: str) -> URIRef:
        try:
            return Namespace(dict(self.graph.namespaces())[ns_name])[token]
        except KeyError:
            return URIRef(token)


class SpatremGraph(BaseGraph):
    ns = "spatrem"


class LrmGraph(BaseGraph):
    ns = "lrm"

    # def __init__(self, label: str) -> None:
    #     super().__init__(label.strip())

    #     self.graph.add((self.id, RDFS.label, Literal(self.label)))


class CrmGraph(BaseGraph):
    ns = "crm"


class Work(LrmGraph):
    ns = "work"

    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label.strip())
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F1_Work")))
        self.expression: Optional["Expression"] = None

    def is_realised_by(self, expr: "Expression") -> None:
        self.expression = expr
        self.graph.add((self.id, self.uri_ref("lrm", "R3i_is_realised_by"), expr.id))

    def has_part(self, work: "Work") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R67_has_part"), work.id))

    def is_part_of(self, work: "Work") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R67i_is_part_of"), work.id))

    def has_part(self, work: "Work") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R67_has_part"), work.id))

    def was_realised_through(self, expression_creation: "ExpressionCreation") -> None:
        self.graph.add(
            (
                self.id,
                self.uri_ref("lrm", "R19i_was_realised_through"),
                expression_creation.id,
            )
        )

    def has_derivative(self, work: "Work") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R2_has_derivative"), work.id))

    def is_derivative_of(self, work: "Work") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R2i_is_derivative_of"), work.id))


class Expression(LrmGraph):
    ns = "expression"

    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label.strip())
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F2_Expression")))

    def realises(self, work: Work) -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R3_realises"), work.id))

    def incorporates(self, expr: "Expression") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R75_incorporates"), expr.id))

    def is_incorporated_in(self, expr: "Expression") -> None:
        self.graph.add(
            (self.id, self.uri_ref("lrm", "R75i_is_incorporated_in"), expr.id)
        )

    def has_component(self, expr: "Expression") -> None:
        self.graph.add((self.id, self.lrm.R5_has_component, expr.id))

    def is_component_of(self, expr: "Expression") -> None:
        self.graph.add((self.id, self.lrm.R5i_is_component_of, expr.id))

    def has_derivative(self, expr: "Expression") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R76_has_derivative"), expr.id))

    def is_derivative_of(self, expr: "Expression") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R76i_is_derivative_of"), expr.id))

    def aggregates(self, expr: "Expression") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R25_aggregates"), expr.id))

    def was_aggregated_by(self, expr: "Expression") -> None:
        self.graph.add(
            (self.id, self.uri_ref("lrm", "R24i_was_aggregated_by"), expr.id)
        )

    def was_created_by(self, expression_creation: "ExpressionCreation") -> None:
        self.graph.add(
            (
                self.id,
                self.uri_ref("lrm", "R17i_was_created_by"),
                expression_creation.id,
            )
        )

    def was_used_for(self, expression_creation: "ExpressionCreation") -> None:
        self.graph.add(
            (self.id, self.uri_ref("lrm", "P16i_was_used_for"), expression_creation.id)
        )

    def has_language(self, language: "Language") -> None:
        self.graph.add((self.id, self.uri_ref("crm", "P72_has_language"), language.id))

    def is_embodied_in(self, manifestation: "Manifestion") -> None:
        self.graph.add(
            (self.id, self.uri_ref("lrm", "R4i_is_embodied_in"), manifestation.id)
        )


class Person(SpatremGraph):
    ns = "person"

    def __init__(self, persName: str) -> None:
        super().__init__(persName.strip())
        self.graph.add((self.id, RDF.type, self.uri_ref("crm", "E21_Person")))

    def performed(self, expression_creation: "ExpressionCreation") -> None:
        self.graph.add(
            (self.id, self.uri_ref("crm", "P14i_performed"), expression_creation.id)
        )

    def has_birthdate(self, date: str) -> None:
        self.graph.add((self.id, self.uri_ref("schema", "birthDate"), Literal(date)))

    def has_deathdate(self, date: str) -> None:
        self.graph.add((self.id, self.uri_ref("schema", "deathDate"), Literal(date)))

    def has_gender(self, gender: str) -> None:
        self.graph.add((self.id, self.uri_ref("schema", "gender"), Literal(gender)))

    def has_nationality(self, nationality: str) -> None:
        self.graph.add(
            (self.id, self.uri_ref("schema", "nationality"), Literal(nationality))
        )


class Nomen(SpatremGraph):
    def __init__(self, persName: str) -> None:
        super().__init__(persName.strip())

        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F12_Nomen")))
        self.graph.add((self.id, RDFS.label, Literal(self.label)))
        self.graph.add(
            (self.id, self.uri_ref("lrm", "R33_has_string"), Literal(persName))
        )

    def is_appellation_of(self, person: Person) -> None:
        self.graph.add(
            (self.id, self.uri_ref("lrm", "R13i_is_appellation_of"), person.id)
        )


class ExpressionCreation(LrmGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add(
            (self.id, RDF.type, self.uri_ref("lrm", "F28_Expression_Creation"))
        )
        if label:
            self.graph.add((self.id, RDFS.label, Literal(label)))

    def created(self, expr: Expression) -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R17_created"), expr.id))

    def used(self, expr: Expression) -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "P16_used"), expr.id))

    def created_a_realisation_of(self, work: Work) -> None:
        self.graph.add(
            (self.id, self.uri_ref("lrm", "R19_created_a_realisation_of"), work.id)
        )

    def carried_out_by(self, agent: Person) -> None:
        """This property describes the active participation of an instance of E39 Actor in an instance of E7 Activity."""
        self.graph.add((self.id, self.uri_ref("crm", "P14_carried_out_by"), agent.id))

    def has_type(self, type_str: str) -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "P2_has_type"), Literal(type_str)))


class Language(CrmGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, self.uri_ref("crm", "E56_Language")))
        if label:
            self.graph.add((self.id, RDFS.label, Literal(label)))


class Manifestion(LrmGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F3_Manifestation")))

    def was_created_by(self, mc: "ManifestationCreation") -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R24i_was_created_by"), mc.id))

    def embodies(self, expr: Expression) -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R4_embodies"), expr.id))


# class Manifestion(LrmGraph):
#     def __init__(
#         self, label: Optional[str] = None, time_span: Optional["TimeSpan"] = None
#     ) -> None:
#         super().__init__(label)
#         self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F3_Manifestation")))
#         if time_span:
#             m_creation: "ManifestationCreation" = ManifestationCreation(time_span)
#             self.was_created_by(m_creation)
#             self.graph += m_creation.graph

#     def was_created_by(self, mc: "ManifestationCreation") -> None:
#         self.graph.add((self.id, self.uri_ref("lrm", "R24i_was_created_by"), mc.id))

#     def embodies(self, expr: Expression) -> None:
#         self.graph.add((self.id, self.uri_ref("lrm", "R4_embodies"), expr.id))


class ManifestationCreation(LrmGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add(
            (self.id, RDF.type, self.uri_ref("lrm", "F30_Manifestation_Creation"))
        )
        if label:
            self.graph.add((self.id, RDFS.label, Literal(label)))

    def embodies(self, expr: Expression) -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R4_embodies"), expr.id))

    def created(self, manifestation: Manifestion) -> None:
        self.graph.add((self.id, self.uri_ref("lrm", "R24_created"), manifestation.id))

    def has_time_span(self, time_span: "TimeSpan") -> None:
        self.graph.add((self.id, self.uri_ref("crm", "P4_has_time_span"), time_span.id))


# class ManifestationCreation(LrmGraph):
#     def __init__(self, time_span: Optional["TimeSpan"] = None) -> None:
#         # if time_span:
#         #     label = f"{label}_{time_span.label}"
#         super().__init__()
#         self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F30_Manifestation_Creation")))
#         if time_span:
#             self.has_time_span(time_span)

#     def embodies(self, expr: Expression) -> None:
#         self.graph.add((self.id, self.uri_ref("lrm", "R4_embodies"), expr.id))

#     def created(self, manifestation: Manifestion) -> None:
#         self.graph.add((self.id, self.uri_ref("lrm", "R24_created"), manifestation.id))

#     def has_time_span(self, time_span: "TimeSpan") -> None:
#         self.graph.add((self.id, self.uri_ref("crm", "P4_has_time_span"), time_span.id))


class TimeSpan(CrmGraph):
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
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "E52_Time_Span")))
        self.graph.add(
            (
                self.id,
                self.uri_ref("lrm", "P82_at_some_time_within"),
                Literal(duration, datatype=XSD.duration),
            )
        )


class SerialWork(Work):
    """A class representing FRBRoo F18 Serial Work.

    F18 Serial Work has been removed from the LRMoo, at least in its
    current form; however, its meaning -- "works that are, or have
    been, planned to result in sequences of Expressions or
    Manifestations with common features" -- is so apt and useful when
    talking about periodicals that we are adding it back in our
    project ontology.

    """

    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.remove((self.id, RDF.type, self.uri_ref("lrm", "F1_Work")))
        self.graph.add((self.id, RDF.type, self.uri_ref("lrm", "F18_Serial_Work")))
        self.expression: Expression | None = None
