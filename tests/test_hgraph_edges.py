import pytest
from heterograph.hgraph import HGraph

@pytest.fixture
def empty_graph():
    """Fixture to create an empty HGraph."""
    return HGraph()

@pytest.fixture
def graph_with_edges():
    """Fixture to create an HGraph with vertices and edges."""
    graph = HGraph()
    graph.add_vx(3)
    graph.add_edge(0, 1)
    graph.add_edge(1, 2)
    return graph

def test_num_edges(empty_graph, graph_with_edges):
    """Test the num_edges method."""
    assert empty_graph.num_edges == 0
    assert graph_with_edges.num_edges == 2

def test_edges(empty_graph, graph_with_edges):
    """Test the edges property."""
    assert empty_graph.edges == []
    assert set(graph_with_edges.edges) == {(0, 1), (1, 2)}

def test_add_edge(empty_graph):
    """Test the add_edge method."""
    empty_graph.add_vx(3)
    empty_graph.add_edge(0, 1)
    empty_graph.add_edge(1, 2)
    assert empty_graph.num_edges == 2
    assert set(empty_graph.edges) == {(0, 1), (1, 2)}

def test_check_edge(graph_with_edges):
    """Test the check_edge method."""
    assert graph_with_edges.check_edge((0, 1)) is True
    assert graph_with_edges.check_edge((2, 0)) is False
    with pytest.raises(RuntimeError):
        graph_with_edges.check_edge((2, 0), verify=True)

def test_rm_edge(graph_with_edges):
    """Test the rm_edge method."""
    graph_with_edges.rm_edge((0, 1))
    assert graph_with_edges.num_edges == 1
    assert set(graph_with_edges.edges) == {(1, 2)}
    with pytest.raises(RuntimeError):
        graph_with_edges.rm_edge((0, 1), verify=True)

