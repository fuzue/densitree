import numpy as np
import pytest
from densitree.steps.density import DensityEstimator


def make_data():
    rng = np.random.default_rng(0)
    # Two clusters: dense at origin, sparse at (10, 10)
    dense = rng.normal(loc=[0, 0], scale=0.5, size=(180, 2))
    sparse = rng.normal(loc=[10, 10], scale=2.0, size=(20, 2))
    return np.vstack([dense, sparse])


def test_density_shape():
    X = make_data()
    step = DensityEstimator(knn=5)
    out = step.run(X)
    assert "density" in out
    assert out["density"].shape == (200,)


def test_density_values_positive():
    X = make_data()
    out = DensityEstimator(knn=5).run(X)
    assert np.all(out["density"] > 0)


def test_dense_region_has_higher_density():
    X = make_data()
    out = DensityEstimator(knn=5).run(X)
    density = out["density"]
    mean_dense = density[:180].mean()
    mean_sparse = density[180:].mean()
    assert mean_dense > mean_sparse
