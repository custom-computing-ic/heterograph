import pytest
import graph_tool.all as gt
from heterograph.hgraph import HGraph, HGraphProps

def test_hgraph_init_default():
    """Test initialization of HGraph with default parameters."""
    graph = HGraph()

    assert graph.read_only == False
    assert graph._HGraph__vx_counter == 0
    assert graph._HGraph__ivx == {}
    assert graph._HGraph__vx == {}
    assert graph._HGraph__in == {}
    assert graph._HGraph__out == {}
    assert graph._HGraph__ginit is None
    assert graph._HGraph__vinit is None
    assert graph._HGraph__einit is None
    assert isinstance(graph._HGraph__g, gt.Graph)
    assert graph._HGraph__g.is_directed()
    assert isinstance(graph._HGraph__properties, HGraphProps)

def test_init_ginit_vinit_einit():
    def ginit(hgraph): pass
    def vinit(hgraph, vid): pass
    def einit(hgraph, etuple): pass

    hgraph = HGraph(ginit=ginit, vinit=vinit, einit=einit)
    assert hgraph._HGraph__ginit == ginit
    assert hgraph._HGraph__vinit == vinit
    assert hgraph._HGraph__einit == einit

def test_init_ginit_vinit_einit_none():
    hgraph = HGraph()
    assert hgraph._HGraph__ginit is None
    assert hgraph._HGraph__vinit is None
    assert hgraph._HGraph__einit is None

def test_init_calls_reset(mocker):
    mocker.patch.object(HGraph, '_HGraph__reset')
    hgraph = HGraph()
    hgraph._HGraph__reset.assert_called_once()