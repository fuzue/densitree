import numpy as np
import pytest
from densitree.steps.cluster import ClusterStep


def make_X_down():
    rng = np.random.default_rng(2)
    # 3 tight clusters in 2D
    c1 = rng.normal([0, 0], 0.1, (40, 2))
    c2 = rng.normal([5, 0], 0.1, (40, 2))
    c3 = rng.normal([2.5, 4], 0.1, (40, 2))
    return np.vstack([c1, c2, c3])


def test_cluster_labels_shape():
    X_down = make_X_down()
    step = ClusterStep(n_clusters=3)
    out = step.run(None, X_down=X_down)
    assert "cluster_labels_down" in out
    assert out["cluster_labels_down"].shape == (120,)


def test_cluster_labels_range():
    X_down = make_X_down()
    out = ClusterStep(n_clusters=3).run(None, X_down=X_down)
    labels = out["cluster_labels_down"]
    assert set(labels).issubset({0, 1, 2})


def test_cluster_centroids_shape():
    X_down = make_X_down()
    out = ClusterStep(n_clusters=3).run(None, X_down=X_down)
    assert "centroids" in out
    assert out["centroids"].shape == (3, 2)


def test_three_clusters_recovers_groups():
    X_down = make_X_down()
    out = ClusterStep(n_clusters=3).run(None, X_down=X_down)
    labels = out["cluster_labels_down"]
    # Each group of 40 should be in a single cluster
    for i in range(3):
        group_labels = labels[i*40:(i+1)*40]
        assert len(set(group_labels)) == 1
