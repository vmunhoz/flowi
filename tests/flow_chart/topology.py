import pytest
from flowi.flow_chart.topology import Topology


@pytest.fixture()
def nodes():
    return ["1", "2", "3"]


def test_add_edge(nodes):
    topology = Topology(nodes=nodes)
    topology.add_edge(node_from="1", node_to="2")
    assert topology.graph["1"] == ["2"]

    topology.add_edge(node_from="1", node_to="3")
    assert topology.graph["1"] == ["2", "3"]


def test_sort(nodes):
    topology = Topology(nodes=nodes)
    topology.add_edge(node_from="1", node_to="2")
    topology.add_edge(node_from="1", node_to="3")

    ordered = topology.topological_sort()
    assert ordered == ["1", "3", "2"]

    topology = Topology(nodes=nodes)
    topology.add_edge(node_from="1", node_to="2")
    topology.add_edge(node_from="2", node_to="3")
    topology.add_edge(node_from="2", node_to="3")

    ordered = topology.topological_sort()
    assert ordered == ["1", "2", "3"]
