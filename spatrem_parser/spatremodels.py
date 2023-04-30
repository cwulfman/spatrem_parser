from logging import _nameToLevel
from typing import Optional

from pydantic import config, conset
import spatrem_parser.datamodels as dm


class SpatremGraph(dm.BaseGraph):
    def __init__(self, label: Optional[str] = None) -> None:
        super().__init__(label)


class Journal(dm.SerialWork):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        expr: dm.Expression = dm.Expression(f"{name}_expr")
        self.is_realised_by(expr)
        expr.realises(self)
        self.graph += expr.graph

class Issue(dm.Work):
    def __init__(self,
                 journal: dm.SerialWork,
                 issue_id: str
                 ) -> None:
        label = f"{journal.label}_{issue_id}"
        super().__init__(label)
        self.is_part_of(journal)
        expr: dm.Expression = dm.Expression(f"{label}_expr")
        self.is_realised_by(expr)
        expr.realises(self)
        self.graph += expr.graph


class Constituent(dm.Work):
    def __init__(self,
                 issue: Issue,
                 constituent: dm.Expression,
                 ) -> None:
        label = f"{issue.label}_{constituent.label}"
        super().__init__(label)
        self.is_part_of(issue)
        self.is_realised_by(constituent)
        constituent.realises(self)
        self.graph += constituent.graph
