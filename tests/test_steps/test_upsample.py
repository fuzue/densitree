import numpy as np
import pytest
from densitree.steps.upsample import UpsampleStep


def make_context():
    rng = np.random.default_rng(3)
    # 3 centroids
    centroids = np.array([[0.0, 0.0], [5.0, 0.0], [2.5, 4.0]])
    n = 300
    # All 300 original cells
    data = rng.normal(size=(n, 2))
    # 30 downsampled cells (indices)
    down_idx = rng.choice(n, size=30, replace=False)
    # Labels for downsampled cells (10 per centroid)
    labels_down = np.repeat([0, 1, 2], 10)
    return data, centroids, down_idx, labels_down


def test_upsample_labels_shape():
    data, centroids, down_idx, labels_down = make_context()
    step = UpsampleStep()
    out = step.run(data, centroids=centroids, down_idx=down_idx, cluster_labels_down=labels_down)
    assert "labels_" in out
    assert out["labels_"].shape == (300,)


def test_upsample_labels_range():
    data, centroids, down_idx, labels_down = make_context()
    out = UpsampleStep().run(data, centroids=centroids, down_idx=down_idx, cluster_labels_down=labels_down)
    assert set(out["labels_"]).issubset({0, 1, 2})


def test_upsample_downsampled_cells_keep_label():
    data, centroids, down_idx, labels_down = make_context()
    # Put cells exactly on centroids to make nearest assignment deterministic
    data_exact = np.zeros((300, 2))
    for i, idx in enumerate(down_idx):
        data_exact[idx] = centroids[labels_down[i]]
    out = UpsampleStep().run(data_exact, centroids=centroids, down_idx=down_idx, cluster_labels_down=labels_down)
    for i, idx in enumerate(down_idx):
        assert out["labels_"][idx] == labels_down[i]
