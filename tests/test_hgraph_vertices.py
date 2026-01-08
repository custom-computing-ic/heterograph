import pytest
from heterograph.hgraph import HGraph

@pytest.fixture
def empty_graph():
    """Fixture to create an empty HGraph."""
    return HGraph()

@pytest.fixture
def graph_with_vertices():
    """Fixture to create an HGraph with vertices."""
    graph = HGraph()
    graph.add_vx(3)
    return graph

def test_num_vx(empty_graph, graph_with_vertices):
    """Test the num_vx method."""
    assert empty_graph.num_vx == 0
    assert graph_with_vertices.num_vx == 3

def test_vertices(empty_graph, graph_with_vertices):
    """Test the vertices property."""
    assert list(empty_graph.vertices) == []
    assert list(graph_with_vertices.vertices) == [0, 1, 2]

def test_source(empty_graph, graph_with_vertices):
    """Test the source method."""
    # No vertices, source should be None
    assert empty_graph.source ==  []

    # Add an edge to have a source vertex
    graph_with_vertices.add_edge(0, [1, 2])
    assert graph_with_vertices.source == [0]

def test_sink(empty_graph, graph_with_vertices):
    """Test the sink method."""
    # No vertices, sink should be None
    assert empty_graph.sink == []

    graph_with_vertices.add_edge(0, [1, 2])
    assert graph_with_vertices.sink == [1, 2]

def test_num_in_vx(graph_with_vertices):
    """Test the num_in_vx method."""
    graph_with_vertices.add_edge(0, 1)
    assert graph_with_vertices.num_in_vx(0) == 0
    assert graph_with_vertices.num_in_vx(1) == 1

def test_num_out_vx(graph_with_vertices):
    """Test the num_out_vx method."""
    graph_with_vertices.add_edge(0, 1)
    assert graph_with_vertices.num_out_vx(0) == 1
    assert graph_with_vertices.num_out_vx(1) == 0

def test_add_vx(empty_graph):
    """Test the add_vx method."""
    empty_graph.add_vx(3)
    assert empty_graph.num_vx == 3
    assert empty_graph.vertices == [0, 1, 2]

def test_rm_vx(graph_with_vertices):
    """Test the rm_vx method."""
    graph_with_vertices.rm_vx(1)
    assert graph_with_vertices.num_vx == 2
    assert graph_with_vertices.vertices == [0, 2]

def test_check_vx(graph_with_vertices):
    """Test the check_vx method."""
    assert graph_with_vertices.check_vx(0) is True
    assert graph_with_vertices.check_vx(3) is False
    with pytest.raises(RuntimeError):
        graph_with_vertices.check_vx(3, verify=True)
