import numpy as np
import networkx as nx
import pandas as pd
import pytest
from densitree.result import SPADEResult


def make_result():
    rng = np.random.default_rng(5)
    n_cells, n_features, n_clusters = 200, 3, 5
    labels = rng.integers(0, n_clusters, size=n_cells)
    G = nx.path_graph(n_clusters)
    for node in G.nodes:
        G.nodes[node]["size"] = int((labels == node).sum())
        G.nodes[node]["median"] = rng.normal(size=n_features)
    X_down = rng.normal(size=(20, n_features))
    down_idx = rng.choice(n_cells, size=20, replace=False)
    return SPADEResult(
        labels_=labels,
        tree_=G,
        X_down=X_down,
        down_idx=down_idx,
        n_features=n_features,
        feature_names=None,
    )


def test_result_has_labels():
    r = make_result()
    assert r.labels_.shape == (200,)


def test_result_has_tree():
    r = make_result()
    assert isinstance(r.tree_, nx.Graph)


def test_cluster_stats_is_dataframe():
    r = make_result()
    assert isinstance(r.cluster_stats_, pd.DataFrame)


def test_cluster_stats_row_count():
    r = make_result()
    assert len(r.cluster_stats_) == 5


def test_cluster_stats_has_size_column():
    r = make_result()
    assert "size" in r.cluster_stats_.columns


def test_feature_names_default_to_indices():
    r = make_result()
    # columns should include feature_0, feature_1, feature_2 medians
    assert "median_feature_0" in r.cluster_stats_.columns


def test_result_with_named_features():
    rng = np.random.default_rng(6)
    n_cells, n_features, n_clusters = 100, 2, 3
    labels = rng.integers(0, n_clusters, size=n_cells)
    G = nx.path_graph(n_clusters)
    for node in G.nodes:
        G.nodes[node]["size"] = int((labels == node).sum())
        G.nodes[node]["median"] = rng.normal(size=n_features)
    r = SPADEResult(
        labels_=labels,
        tree_=G,
        X_down=rng.normal(size=(10, n_features)),
        down_idx=rng.choice(n_cells, size=10, replace=False),
        n_features=n_features,
        feature_names=["FITC", "mCherry"],
    )
    assert "median_FITC" in r.cluster_stats_.columns
    assert "median_mCherry" in r.cluster_stats_.columns
