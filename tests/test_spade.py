import numpy as np
import pandas as pd
import pytest
from densitree import SPADE, SPADEResult


def make_X(n_cells=500, n_features=4, n_clusters=5, seed=7):
    rng = np.random.default_rng(seed)
    centers = rng.normal(scale=5, size=(n_clusters, n_features))
    labels = rng.integers(0, n_clusters, size=n_cells)
    return centers[labels] + rng.normal(scale=0.5, size=(n_cells, n_features))


def test_fit_predict_returns_labels():
    X = make_X()
    spade = SPADE(n_clusters=5, downsample_target=0.2, random_state=0)
    labels = spade.fit_predict(X)
    assert labels.shape == (500,)


def test_labels_range():
    X = make_X()
    spade = SPADE(n_clusters=5, downsample_target=0.2, random_state=0)
    labels = spade.fit_predict(X)
    assert set(labels).issubset(set(range(5)))


def test_fit_returns_self():
    X = make_X()
    spade = SPADE(n_clusters=5, downsample_target=0.2, random_state=0)
    result = spade.fit(X)
    assert result is spade


def test_fit_populates_result():
    X = make_X()
    spade = SPADE(n_clusters=5, downsample_target=0.2, random_state=0)
    spade.fit(X)
    assert isinstance(spade.result_, SPADEResult)


def test_tree_has_correct_node_count():
    X = make_X()
    spade = SPADE(n_clusters=5, downsample_target=0.2, random_state=0)
    spade.fit(X)
    assert spade.result_.tree_.number_of_nodes() == 5


def test_cluster_stats_no_nans():
    X = make_X()
    spade = SPADE(n_clusters=5, downsample_target=0.2, random_state=0)
    spade.fit(X)
    assert not spade.result_.cluster_stats_.isna().any().any()


def test_dataframe_input_preserves_column_names():
    X = make_X(n_features=3)
    df = pd.DataFrame(X, columns=["FITC", "mCherry", "FSC"])
    spade = SPADE(n_clusters=5, downsample_target=0.2, random_state=0)
    spade.fit(df)
    assert "median_FITC" in spade.result_.cluster_stats_.columns
    assert "median_mCherry" in spade.result_.cluster_stats_.columns


def test_raises_if_too_few_cells():
    X = make_X(n_cells=3)
    spade = SPADE(n_clusters=5)
    with pytest.raises(ValueError, match="n_clusters"):
        spade.fit(X)


def test_raises_if_downsample_target_invalid():
    with pytest.raises(ValueError, match="downsample_target"):
        SPADE(downsample_target=1.5)


def test_transform_arcsinh_applied():
    # With large values, arcsinh should compress range before clustering
    rng = np.random.default_rng(8)
    X = rng.uniform(0, 1000, size=(300, 2))
    spade = SPADE(n_clusters=3, downsample_target=0.3, transform="arcsinh", cofactor=150.0, random_state=0)
    labels = spade.fit_predict(X)
    assert labels.shape == (300,)


def test_transform_none():
    X = make_X()
    spade = SPADE(n_clusters=5, downsample_target=0.2, transform=None, random_state=0)
    labels = spade.fit_predict(X)
    assert labels.shape == (500,)


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def test_full_pipeline_dataframe_matplotlib():
    rng = np.random.default_rng(99)
    n_cells, n_features = 800, 3
    X = pd.DataFrame(
        rng.normal(size=(n_cells, n_features)),
        columns=["FITC", "mCherry", "FSC"],
    )
    spade = SPADE(n_clusters=10, downsample_target=0.15, transform="arcsinh", random_state=0)
    spade.fit(X)

    assert spade.labels_.shape == (n_cells,)
    assert spade.result_.tree_.number_of_nodes() == 10
    assert not spade.result_.cluster_stats_.isna().any().any()
    assert "median_FITC" in spade.result_.cluster_stats_.columns

    fig = spade.result_.plot_tree(color_by="FITC", size_by="count", backend="matplotlib")
    assert isinstance(fig, plt.Figure)
    plt.close("all")
