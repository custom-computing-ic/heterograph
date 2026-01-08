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
    graph.add_vx(4)
    graph.add_edge(0, 1)
    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(0, 3)
    return graph

def test_in_vx(empty_graph, graph_with_edges):
    """Test the in_vx method."""
    with pytest.raises(RuntimeError):
        empty_graph.in_vx(0)

    # Test in_vx on a graph with edges
    assert graph_with_edges.in_vx(0) == []
    assert set(graph_with_edges.in_vx(1)) == {0}
    assert set(graph_with_edges.in_vx(2)) == {1}
    assert set(graph_with_edges.in_vx(3)) == {0, 2}

def test_out_vx(empty_graph, graph_with_edges):
    """Test the out_vx method."""
    with pytest.raises(RuntimeError):
        empty_graph.out_vx(0)

    # Test out_vx on a graph with edges
    assert set(graph_with_edges.out_vx(0)) == {1, 3}
    assert set(graph_with_edges.out_vx(1)) == {2}
    assert set(graph_with_edges.out_vx(2)) == {3}
    assert graph_with_edges.out_vx(3) == []

def test_in_vx_with_order(graph_with_edges):
    """Test the in_vx method with order parameter."""
    assert set(graph_with_edges.in_vx(3, order=[0, 2])) == {0, 2}
    assert set(graph_with_edges.in_vx(3, order=[2, 0])) == {2, 0}

    with pytest.raises(RuntimeError):
        graph_with_edges.in_vx(3, order=[0, 4])  # 4 is not a neighbor

def test_out_vx_with_order(graph_with_edges):
    """Test the out_vx method with order parameter."""
    assert set(graph_with_edges.out_vx(0, order=[3, 1])) == {3, 1}
    assert set(graph_with_edges.out_vx(0, order=[1, 3])) == {1, 3}

    with pytest.raises(RuntimeError):
        graph_with_edges.out_vx(0, order=[1, 4])  # 4 is not a neighbor

def test_in_vx_with_anchor(graph_with_edges):
    """Test the in_vx method with anchor parameter."""
    assert set(graph_with_edges.in_vx(3, order=[2], anchor=0)) == {0, 2}
    assert set(graph_with_edges.in_vx(3, order=[0], anchor=2, after=False)) == {0, 2}

    with pytest.raises(RuntimeError):
        graph_with_edges.in_vx(3, anchor=4) # order is not specified

    with pytest.raises(RuntimeError):
        graph_with_edges.in_vx(3, order=[0], anchor=4) # 4 is not a neighbor


def test_out_vx_with_anchor(graph_with_edges):
    """Test the out_vx method with anchor parameter."""
    assert set(graph_with_edges.out_vx(0, order=[1], anchor=3)) == {1, 3}
    assert set(graph_with_edges.out_vx(0, order=[3], anchor=1, after=False)) == {3, 1}

    with pytest.raises(RuntimeError):
        graph_with_edges.out_vx(0, anchor=4)  # order is not specified

    with pytest.raises(RuntimeError):
        graph_with_edges.out_vx(0, order=[3], anchor=4)  # 4 is not a neighbor
