from logging import _nameToLevel
from typing import Optional
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
