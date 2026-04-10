import numpy as np
import pytest
from densitree.steps.downsample import DownsampleStep


def make_data_and_density():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(1000, 3))
    # Simulate: first 800 cells dense, last 200 sparse
    density = np.concatenate([np.full(800, 10.0), np.full(200, 1.0)])
    return X, density


def test_downsample_returns_subset():
    X, density = make_data_and_density()
    step = DownsampleStep(downsample_target=0.1, random_state=42)
    out = step.run(X, density=density)
    assert "X_down" in out
    assert "down_idx" in out
    assert len(out["X_down"]) == len(out["down_idx"])
    assert len(out["X_down"]) < len(X)


def test_downsample_target_respected_approximately():
    X, density = make_data_and_density()
    step = DownsampleStep(downsample_target=0.1, random_state=42)
    out = step.run(X, density=density)
    # Allow 50% slack — downsampling is stochastic
    assert 50 <= len(out["X_down"]) <= 150


def test_sparse_cells_more_likely_kept():
    X, density = make_data_and_density()
    step = DownsampleStep(downsample_target=0.2, random_state=42)
    out = step.run(X, density=density)
    idx = out["down_idx"]
    n_sparse_kept = (idx >= 800).sum()
    n_dense_kept = (idx < 800).sum()
    # Sparse region (200 cells) should retain a higher fraction than dense (800 cells)
    frac_sparse = n_sparse_kept / 200
    frac_dense = n_dense_kept / 800
    assert frac_sparse > frac_dense


def test_down_idx_valid_range():
    X, density = make_data_and_density()
    out = DownsampleStep(downsample_target=0.1, random_state=0).run(X, density=density)
    assert out["down_idx"].min() >= 0
    assert out["down_idx"].max() < len(X)
