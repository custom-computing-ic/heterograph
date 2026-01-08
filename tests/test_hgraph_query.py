import pytest
from heterograph.query.qgraph import QGraph

def test_empty_pattern():
    qg = QGraph(pattern='')
    assert qg.num_vx == 0
    qg = QGraph(pattern='0')
    assert qg.num_vx == 0
    qg = QGraph(pattern='0=>0')
    assert qg.num_vx == 0
    qg = QGraph(pattern='0=>(0|0)')
    assert qg.num_vx == 0

def test_single_node_pattern():
    try:
        qg = QGraph(pattern='A')
        assert qg.num_vx == 1
    except Exception as e:
        pytest.fail(f"Single node pattern test failed: {e}")

def test_simple_directed_edge_pattern():
    try:
        qg = QGraph(pattern='A => B')
        assert qg is not None
    except Exception as e:
        pytest.fail(f"Simple directed edge pattern test failed: {e}")

def test_pattern_with_alternation():
    try:
        qg = QGraph(pattern='(A | B) => C')
        assert qg is not None
    except Exception as e:
        pytest.fail(f"Pattern with alternation test failed: {e}")

def test_complex_pattern_with_multiple_alternations():
    try:
        qg = QGraph(pattern='X=>(A|B)=>(C|D)=>E')
        assert qg is not None
    except Exception as e:
        pytest.fail(f"Complex pattern with multiple alternations test failed: {e}")

def test_pattern_with_attributes():
    try:
        qg = QGraph(pattern='a{name:"A"} ={d:True}>b{name:"B"}')
        assert qg is not None
    except Exception as e:
        pytest.fail(f"Pattern with attributes test failed: {e}")

def test_pattern_with_multiple_attributes1():
    try:
        qg = QGraph(pattern='a{name:"A", type:"circle"} => b{name:"B", type:"rect"}')
        assert qg is not None
    except Exception as e:
        pytest.fail(f"Pattern with multiple attributes test failed: {e}")


def test_pattern_with_multiple_attributes2():
    try:
        qg = QGraph(pattern='a{name:"A", type:"circle"} => b{name:"B", type:"rect", "test", 4, 2.3}')
        assert qg is not None
    except Exception as e:
        pytest.fail(f"Pattern with multiple attributes test failed: {e}")

def test_invalid_pattern_syntax():
    with pytest.raises(SyntaxError):
        QGraph(pattern='A =>')

    with pytest.raises(SyntaxError):
        QGraph(pattern='0A')

    with pytest.raises(SyntaxError):
        QGraph(pattern='A =()> B')
