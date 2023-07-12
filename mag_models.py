from typing import Optional
from rdflib import Graph
import lrm_models as lrm


class Journal(lrm.SerialWork):
    def __init__(self, name: str) -> None:
        self.label: str = name
        super().__init__(self.label)
        self.expression: lrm.Expression = lrm.Expression(f"{self.label}_expr")
        self.is_realised_by(self.expression)
        self.expression.realises(self)
        self.graph += self.expression.graph


class Issue(lrm.Work):
    """An Issue is the publisher's work, whose expression
    incorporates the editor's work."""

    def __init__(self, journal: lrm.SerialWork, issue_id: str) -> None:
        self.label: str = f"{journal.label}_{issue_id}"
        super().__init__(self.label)

        self.pub_expr: lrm.Expression = lrm.Expression(f"{self.label}_pubexpr")
        self.is_realised_by(self.pub_expr)
        self.pub_expr.realises(self)

        if journal:
            self.is_member_of(journal)
            journal.has_member(self)
            self.graph += journal.graph
            self.pub_expr.is_component_of(journal.expression)
            journal.expression.has_component(self.pub_expr)

        self.editor_work: lrm.Work = lrm.Work(f"{journal.label}_{issue_id}_edw")
        self.editor_expr: lrm.Expression = lrm.Expression(f"{self.label}_edexpr")
        self.editor_work.is_realised_by(self.editor_expr)
        self.editor_expr.realises(self.editor_work)

        self.pub_expr.aggregates(self.editor_expr)

        for entity in [
            journal,
            self.pub_expr,
            journal.expression,
            self.editor_work,
            self.editor_expr,
        ]:
            self.graph += entity.graph

    @property
    def publication_work(self) -> lrm.Work:
        return self


class Constituent_old(lrm.Work):
    def __init__(self, issue: Issue, item: lrm.Work) -> None:
        self.label: str = f"{issue.label}_{item.label}"
        super().__init__(self.label)
        self.is_part_of(issue)
        issue.has_part(self)

        self.is_derivative_of(item)
        item.has_derivative(self)

        self.expression: lrm.Expression = lrm.Expression(f"{self.label}_expr")
        self.is_realised_by(self.expression)
        self.expression.realises(self)

        if item.expression:
            self.expression.incorporates(item.expression)
            item.expression.is_incorporated_in(self.expression)

        issue.editor_expr.incorporates(self.expression)
        self.expression.is_incorporated_in(issue.editor_expr)

        self.graph += issue.graph
        self.graph += issue.editor_expr.graph
        self.graph += self.expression.graph
        self.graph += item.graph
        if item.expression:
            self.graph += item.expression.graph


class PublicationWork(lrm.Work):
    def __init__(self, journal: lrm.SerialWork, issue_id: str) -> None:
        self.label: str = f"{journal.label}_{issue_id}"
        super().__init__(self.label)
        self.is_part_of(journal)
        expr: lrm.Expression = lrm.Expression(f"{self.label}_expr")
        self.expression: lrm.Expression = expr
        self.is_realised_by(expr)
        expr.realises(self)
        self.graph += expr.graph


class AuthorOld(lrm.Person):
    def __init__(self, persName: Optional[str] = None) -> None:
        super().__init__(persName)
        if persName:
            nomen: lrm.Nomen = lrm.Nomen(persName)
            self.has_appellation(nomen)
            nomen.is_appellation_of(self)
            self.graph += nomen.graph

    def has_appellation(self, nomen: lrm.Nomen) -> Graph:
        self.graph.add((self.id, self.uri_ref("lrm", "R13_has_appellation"), nomen.id))
        return self.graph

class Author(lrm.Person):
    def __init__(self, persName: str) -> None:
        super().__init__(persName)

        nomen: lrm.Nomen = lrm.Nomen(persName)
        self.has_appellation(nomen)
        nomen.is_appellation_of(self)
        self.graph += nomen.graph

    def has_appellation(self, nomen: lrm.Nomen) -> Graph:
        self.graph.add((self.id, self.uri_ref("lrm", "R13_has_appellation"), nomen.id))
        return self.graph