from spatrem.classes.base_graph import BaseGraph

def test_base_graph():
    base_graph = BaseGraph()
    assert base_graph.__class__ == BaseGraph
