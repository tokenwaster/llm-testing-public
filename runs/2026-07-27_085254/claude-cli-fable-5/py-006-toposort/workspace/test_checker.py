from solution import topo_sort


def test_example():
    assert topo_sort([("b", "c"), ("a", "c")]) == ["a", "b", "c"]


def test_lexicographic_choice():
    assert topo_sort([("z", "a")], nodes=["m"]) == ["m", "z", "a"]


def test_chain():
    assert topo_sort([("c", "b"), ("b", "a")]) == ["c", "b", "a"]


def test_diamond():
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    assert topo_sort(edges) == ["a", "b", "c", "d"]


def test_isolated_nodes():
    assert topo_sort([], nodes=["b", "a"]) == ["a", "b"]


def test_duplicate_edges():
    assert topo_sort([("a", "b"), ("a", "b"), ("a", "b")]) == ["a", "b"]


def test_cycle_returns_none():
    assert topo_sort([("a", "b"), ("b", "a")]) is None


def test_self_loop_is_cycle():
    assert topo_sort([("a", "a")]) is None


def test_larger_deterministic():
    edges = [("t1", "t3"), ("t2", "t3"), ("t3", "t5"), ("t4", "t5"), ("t0", "t1")]
    assert topo_sort(edges) == ["t0", "t1", "t2", "t3", "t4", "t5"]


def test_cycle_in_larger_graph():
    edges = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "b")]
    assert topo_sort(edges) is None
