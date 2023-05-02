from logging import _nameToLevel
from typing import Optional

from pydantic import config, conset
import spatrem_parser.datamodels as dm


class SpatremGraph(dm.BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)


class Journal(dm.SerialWork):
    def __init__(self, name: str) -> None:
        self.label: str = name
        super().__init__(self.label)
        self.expression: dm.Expression = dm.Expression(f"{self.label}_expr")
        self.is_realised_by(self.expression)
        self.expression.realises(self)
        self.graph += self.expression.graph


class Issue(dm.Work):
    """An Issue is the publisher's work, whose expression
    incorporates the editor's work."""

    def __init__(self, journal: dm.SerialWork, issue_id: str) -> None:
        self.label: str = f"{journal.label}_{issue_id}"
        super().__init__(self.label)

        self.is_member_of(journal)
        journal.has_member(self)
        self.graph += journal.graph

        self.pub_expr: dm.Expression = dm.Expression(f"{self.label}_pubexpr")
        self.is_realised_by(self.pub_expr)
        self.pub_expr.realises(self)
        self.pub_expr.is_component_of(journal.expression)
        journal.expression.has_component(self.pub_expr)

        self.editor_work: dm.Work = dm.Work(f"{journal.label}_{issue_id}_edw")
        self.editor_expr: dm.Expression = dm.Expression(f"{self.label}_edexpr")
        self.editor_work.is_realised_by(self.editor_expr)
        self.editor_expr.realises(self.editor_work)

        self.pub_expr.aggregates(self.editor_expr)

        self.graph += journal.graph
        self.graph += journal.expression.graph
        self.graph += self.pub_expr.graph
        self.graph += self.editor_work.graph
        self.graph += self.editor_expr.graph

    @property
    def publication_work(self) -> dm.Work:
        return self


class Constituent(dm.Work):
    def __init__(self, issue: Issue, item: dm.Work) -> None:
        self.label: str = f"{issue.label}_{item.label}"
        super().__init__(self.label)
        self.is_part_of(issue)
        issue.has_part(self)

        self.is_derivative_of(item)
        item.has_derivative(self)

        self.expression: dm.Expression = dm.Expression(f"{self.label}_expr")
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


class PublicationWork(dm.Work):
    def __init__(self, journal: dm.SerialWork, issue_id: str) -> None:
        self.label: str = f"{journal.label}_{issue_id}"
        super().__init__(self.label)
        self.is_part_of(journal)
        expr: dm.Expression = dm.Expression(f"{self.label}_expr")
        self.expression: dm.Expression = expr
        self.is_realised_by(expr)
        expr.realises(self)
        self.graph += expr.graph


class Author(dm.Person):
    def __init__(self, persName: Optional[str] = None) -> None:
        super().__init__(persName)
        if persName:
            nomen: dm.Nomen = dm.Nomen(persName)
            self.has_appellation(nomen)
            nomen.is_appellation_of(self)
            self.graph += nomen.graph

    def has_appellation(self, nomen: "Nomen") -> None:
        self.graph.add((self.id, self.lrm.R13_has_Appellation, nomen.id))
