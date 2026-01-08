import pytest
from heterograph.algorithm.dfs import get_paths, dfs_visitor, dfs_traversal
from heterograph import *

#############    get_paths    #############
def test_get_paths():
    g = HGraph()
    g.add_vx(5)
    g.add_edge(0, 1)
    g.add_edge(1, [2, 3])
    g.add_edge([2, 3], 4)
    paths = get_paths(g, vs=[0, 2])
    assert paths == [[0, 1, 2, 4], [0, 1, 3, 4], [2, 4]]

def test_get_paths_empty_graph():
    g = HGraph()
    with pytest.raises(RuntimeError):
        paths = get_paths(g, vs=[0, 2])


def test_get_paths_single_vertex():
    g = HGraph()
    g.add_vx(1)
    paths = get_paths(g, vs=[0])
    assert paths == [[0]]

#############    dfs_visitor    #############
def test_dfs_visitor():
    g = HGraph()
    g.add_vx(5)
    g.add_edge(0, 1)
    g.add_edge(1, [2, 3])
    g.add_edge([2, 3], 4)
    visited = []
    def pre(g, vx, path, data):
        visited.append(vx)
    dfs_visitor(g, [0], pre=pre)
    assert visited == [0, 1, 2, 4, 3, 4]

def test_dfs_visitor_empty_graph():
    g = HGraph()
    visited = []
    def pre(g, vx, path, data):
        visited.append(vx)
    with pytest.raises(RuntimeError):
        dfs_visitor(g, [0], pre=pre)

def test_dfs_visitor_single_vertex():
    g = HGraph()
    g.add_vx(1)
    visited = []
    def pre(g, vx, path, data):
        visited.append(vx)
    dfs_visitor(g, [0], pre=pre)
    assert visited == [0]

def test_dfs_visitor_no_pre_post_function():
    g = HGraph()
    g.add_vx(5)
    g.add_edge(0, 1)
    g.add_edge(1, [2, 3])
    g.add_edge([2, 3], 4)
    with pytest.raises(RuntimeError):
        dfs_visitor(g, [0])

def test_dfs_visitor_nonexistent_vertex():
    g = HGraph()
    g.add_vx(5)
    g.add_edge(0, 1)
    g.add_edge(1, [2, 3])
    g.add_edge([2, 3], 4)
    visited = []
    def pre(g, vx, path, data):
        visited.append(vx)
    with pytest.raises(RuntimeError):
        dfs_visitor(g, [5], pre=pre)

#############    dfs_traversal    #############
def test_dfs_traversal_no_pre_post():
    g = HGraph()
    g.add_vx(2)

    with pytest.raises(RuntimeError):
        dfs_traversal(g=g, vx=0)

def test_dfs_traversal_pre_post_actions():
    g = HGraph()
    visited_pre = []
    visited_post = []

    def pre(g, vx, inh):
        visited_pre.append(vx)

    def post(g, vx, synth):
        visited_post.append(vx)

    g.add_vx(5)
    for i in range(1, 5):
        g.add_edge(i-1, i)

    dfs_traversal(g=g, vx=0, pre=pre, post=post)

    assert visited_pre == [0, 1, 2, 3, 4], "Pre-visit order should match DFS order"
    assert visited_post == [4, 3, 2, 1, 0], "Post-visit order should reflect that children are processed before the parent"

