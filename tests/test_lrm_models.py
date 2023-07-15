from lrm_models import BaseGraph, LrmGraph


def test_base_graph():
    test_label = "foo"
    g = BaseGraph(test_label)
    assert g.label == test_label


def test_uri_ref():
    test_label = "foo"
    g = BaseGraph(test_label)
    assert g.ns == "spatrem"
    assert g.id == g.uri_ref(g.ns, test_label)


def test_lrm_graph():
    test_label = "bar"
    g = LrmGraph(test_label)
    assert g.label == "bar"
    assert g.id == g.uri_ref(g.ns, test_label)
