import numpy as np
import networkx as nx
import pytest
from densitree.steps.mst import MSTBuilder


def make_context(n_clusters=5, n_cells=100, n_features=2):
    rng = np.random.default_rng(4)
    centroids = rng.normal(size=(n_clusters, n_features))
    labels = rng.integers(0, n_clusters, size=n_cells)
    data = rng.normal(size=(n_cells, n_features))
    return data, centroids, labels


def test_mst_returns_graph():
    data, centroids, labels = make_context(n_clusters=5)
    step = MSTBuilder()
    out = step.run(data, centroids=centroids, labels_=labels)
    assert "tree_" in out
    assert isinstance(out["tree_"], nx.Graph)


def test_mst_node_count():
    data, centroids, labels = make_context(n_clusters=5)
    out = MSTBuilder().run(data, centroids=centroids, labels_=labels)
    assert out["tree_"].number_of_nodes() == 5


def test_mst_edge_count():
    # MST of n nodes has exactly n-1 edges
    data, centroids, labels = make_context(n_clusters=5)
    out = MSTBuilder().run(data, centroids=centroids, labels_=labels)
    assert out["tree_"].number_of_edges() == 4


def test_mst_node_has_size_attribute():
    data, centroids, labels = make_context(n_clusters=5, n_cells=100)
    out = MSTBuilder().run(data, centroids=centroids, labels_=labels)
    for node in out["tree_"].nodes:
        assert "size" in out["tree_"].nodes[node]


def test_mst_node_has_median_attribute():
    data, centroids, labels = make_context(n_clusters=5, n_cells=100, n_features=3)
    out = MSTBuilder().run(data, centroids=centroids, labels_=labels)
    for node in out["tree_"].nodes:
        assert "median" in out["tree_"].nodes[node]
        assert len(out["tree_"].nodes[node]["median"]) == 3
