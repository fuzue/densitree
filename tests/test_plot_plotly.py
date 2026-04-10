import numpy as np
import networkx as nx
import pytest
from densitree.result import SPADEResult
from densitree.plot.plotly import plot_tree


def make_result(n_clusters=4, n_cells=100, n_features=2):
    rng = np.random.default_rng(10)
    labels = rng.integers(0, n_clusters, size=n_cells)
    G = nx.path_graph(n_clusters)
    for node in G.nodes:
        G.nodes[node]["size"] = int((labels == node).sum())
        G.nodes[node]["median"] = rng.normal(size=n_features)
    for i, j in G.edges:
        G[i][j]["weight"] = float(rng.uniform(1, 5))
    return SPADEResult(
        labels_=labels, tree_=G,
        X_down=rng.normal(size=(10, n_features)),
        down_idx=rng.choice(n_cells, size=10, replace=False),
        n_features=n_features, feature_names=["F0", "F1"],
    )


def test_plot_tree_returns_figure():
    import plotly.graph_objects as go
    r = make_result()
    fig = plot_tree(r, color_by=None, size_by="count")
    assert isinstance(fig, go.Figure)


def test_plot_tree_color_by_index():
    import plotly.graph_objects as go
    r = make_result()
    fig = plot_tree(r, color_by=0, size_by="count")
    assert isinstance(fig, go.Figure)


def test_plot_tree_color_by_name():
    import plotly.graph_objects as go
    r = make_result()
    fig = plot_tree(r, color_by="F1", size_by="count")
    assert isinstance(fig, go.Figure)
