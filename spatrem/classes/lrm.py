from typing import Optional
from rdflib.term import Literal
from rdflib.namespace._RDF import RDF
from rdflib.namespace._RDFS import RDFS
from spatrem.classes.base_graph import BaseGraph
from spatrem.classes import LRM, CRM, SCHEMA, DCTERMS, SPATREM
from spatrem.classes.crm import TimeSpan, Language, Person, Nomen

class Work(BaseGraph):
    def __init__(self, label: str) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, LRM.F1_Work))
        self.expression = Expression()
        self.is_realised_by(self.expression)

    def is_realised_by(self, expr: "Expression") -> None:
        self.expression = expr
        self.graph.add((self.id, LRM.R3i_is_realised_by, expr.id))
        self.graph += expr.graph


    def was_realised_through(self, expression_creation: "ExpressionCreation") -> None:
        self.graph.add((self.id, LRM.R19i_was_realised_through, expression_creation.id))


    def is_part_of(self, work: "Work") -> None:
        self.graph.add((self.id, LRM.R67i_is_part_of, work.id))


    def has_part(self, work: "Work") -> None:
        self.graph.add((self.id, LRM.R67_has_part, work.id))


    def has_derivative(self, work: "Work") -> None:
        self.graph.add((self.id, LRM.R2_has_derivative, work.id))


    def is_derivative_of(self, work: "Work") -> None:
        self.graph.add((self.id, LRM.R2i_is_derivative_of, work.id))


    def is_identified_by(self, nomen: Nomen) -> None:
        self.graph.add((self.id, CRM.P1_is_identified_by, nomen.id))

        

    def was_created_by(self, work_creation: "WorkCreation") -> None:
        self.graph.add((self.id, LRM.R16i_was_created_by, work_creation.id))

    def has_language(self, language: Language) -> None:
        self.expression.has_language(language)
        self.graph += self.expression.graph
        


class SerialWork(Work):
    def __init__(self, label: str) -> None:
        super().__init__(label)

        self.graph.remove((self.id, RDF.type, LRM.F1_Work))
        self.graph.add((self.id, RDF.type, LRM.F18_Serial_Work))

    
        


class Expression(BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, LRM.F2_Expression))

    def realises(self, work: Work) -> None:
        self.graph.add((self.id, LRM.R3_realises, work.id))

    def incorporates(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R75_incorporates, expr.id))

    def is_incorporated_in(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R75i_is_incorporated_in, expr.id))

    def has_component(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R5_has_component, expr.id))

    def is_component_of(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R5i_is_component_of, expr.id))

    def has_derivative(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R76_has_derivative, expr.id))

    def is_derivative_of(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R76i_is_derivative_of, expr.id))

    def aggregates(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R25_aggregates, expr.id))

    def was_aggregated_by(self, expr: "Expression") -> None:
        self.graph.add((self.id, LRM.R24i_was_aggregated_by, expr.id))

    def was_created_by(self, expression_creation: "ExpressionCreation") -> None:
        self.graph.add((self.id, LRM.R17i_was_created_by, expression_creation.id))

    def was_used_for(self, expression_creation: "ExpressionCreation") -> None:
        self.graph.add((self.id, LRM.P16i_was_used_for, expression_creation.id))

    def has_language(self, language: "Language") -> None:
        self.graph.add((self.id, CRM.P72_has_language, language.id))

    def is_embodied_in(self, manifestation: "Manifestation") -> None:
        self.graph.add((self.id, LRM.R4i_is_embodied_in, manifestation.id))


class ExpressionCreation(BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add( (self.id, RDF.type, LRM.F28_Expression_Creation))

    def created(self, expr: Expression) -> None:
        self.graph.add((self.id, LRM.R17_created, expr.id))

    def used(self, expr: Expression) -> None:
        self.graph.add((self.id, LRM.P16_used, expr.id))

    def created_a_realisation_of(self, work: Work) -> None:
        self.graph.add((self.id, LRM.R19_created_a_realisation_of, work.id))

    def carried_out_by(self, agent: "Person") -> None:
        """This property describes the active participation of
        an instance of E39 Actor in an instance of E7 Activity."""

        self.graph.add((self.id, CRM.P14_carried_out_by, agent.id))


class WorkCreation(BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add( (self.id, RDF.type, LRM.F27_Work_Creation))

    def created(self, work:Work) -> None:
        self.graph.add((self.id, LRM.R16_created, work.id))

    def carried_out_by(self, agent:Person) -> None:
        self.graph.add((self.id, CRM.P14_carried_out_by, agent.id))



class Manifestation(BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add((self.id, RDF.type, LRM.F3_Manifestation))

    def was_created_by(self, mc: "ManifestationCreation") -> None:
        self.graph.add((self.id, LRM.R24i_was_created_by, mc.id))

    def embodies(self, expr: Expression) -> None:
        self.graph.add((self.id, LRM.R4_embodies, expr.id))


class ManifestationCreation(BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)
        self.graph.add(
            (self.id, RDF.type, LRM.F30_Manifestation_Creation)
        )
        if label:
            self.graph.add((self.id, RDFS.label, Literal(label)))

    def embodies(self, expr: Expression) -> None:
        self.graph.add((self.id, LRM.R4_embodies, expr.id))

    def created(self, manifestation: Manifestation) -> None:
        self.graph.add((self.id, LRM.R24_created, manifestation.id))

    def has_time_span(self, time_span: "TimeSpan") -> None:
        self.graph.add((self.id, CRM.P4_has_time_span, time_span.id))
        
