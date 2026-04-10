"""Download standard cytometry benchmark datasets.

Datasets:
- Levine_32dim: ~265k cells, 32 markers, 14 populations (Levine et al. 2015)
- Samusik_01: ~86k cells, 39 markers, 24 populations (Samusik et al. 2016)

Source: Weber & Robinson's curated benchmark FCS files on GitHub.
"""
from __future__ import annotations

import os
import urllib.request
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# FCS files from lmweber's curated benchmark repos
DATASETS = {
    "Levine_32dim": {
        "url": "https://github.com/lmweber/benchmark-data-Levine-32-dim/raw/master/data/Levine_32dim.fcs",
        "filename": "Levine_32dim.fcs",
        "description": "Human bone marrow CyTOF, 32 surface markers, 14 manually gated populations",
        "reference": "Levine et al. (2015) Cell 162(1):184-197",
        "label_column": "label",
    },
    "Levine_13dim": {
        "url": "https://github.com/lmweber/benchmark-data-Levine-13-dim/raw/master/data/Levine_13dim.fcs",
        "filename": "Levine_13dim.fcs",
        "description": "Human bone marrow CyTOF, 13 markers, 24 manually gated populations",
        "reference": "Levine et al. (2015) Cell 162(1):184-197",
        "label_column": "label",
    },
}


def download_dataset(name: str, force: bool = False) -> Path:
    """Download a benchmark dataset if not already present."""
    if name not in DATASETS:
        raise ValueError(f"Unknown dataset '{name}'. Available: {list(DATASETS.keys())}")

    info = DATASETS[name]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / info["filename"]

    if filepath.exists() and not force:
        print(f"[OK] {name} already downloaded: {filepath}")
        return filepath

    print(f"Downloading {name} from {info['url']}...")
    urllib.request.urlretrieve(info["url"], filepath)
    print(f"[OK] Saved to {filepath} ({filepath.stat().st_size / 1e6:.1f} MB)")
    return filepath


def load_dataset(name: str) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Load a benchmark dataset, downloading if needed.

    Returns
    -------
    X : ndarray, shape (n_cells, n_markers)
        Expression matrix (raw, not transformed).
    labels : ndarray, shape (n_cells,)
        Ground truth population labels (integer-encoded).
        Cells with label 0 are typically ungated/unassigned.
    marker_names : list[str]
        Marker column names.
    """
    filepath = download_dataset(name)

    try:
        import readfcs
        adata = readfcs.read(filepath)
        df = adata.to_df()
    except ImportError:
        raise ImportError(
            "readfcs is required to load FCS files. Install with: pip install readfcs"
        )

    # Metadata columns to exclude from marker matrix
    META_COLS = {
        "Time", "Cell_length", "DNA1", "DNA2", "Viability",
        "file_number", "event_number", "label", "individual",
        "population_id", "population", "cluster", "sample_id",
        "beadDist", "barcode",
    }

    # Find the label column
    label_col = None
    for candidate in ["label", "population_id", "population"]:
        if candidate in df.columns:
            label_col = candidate
            break

    if label_col is None:
        raise ValueError(f"No label column found in {filepath}. Columns: {list(df.columns)}")

    labels_raw = df[label_col].values

    # Marker columns = everything except metadata
    marker_cols = [c for c in df.columns if c not in META_COLS]

    X = df[marker_cols].values.astype(float)
    marker_names = marker_cols

    # Handle NaN labels (ungated cells) -- encode as -1
    labels_raw = np.asarray(labels_raw, dtype=float)
    nan_mask = np.isnan(labels_raw)
    labels_raw = np.where(nan_mask, -1, labels_raw).astype(int)

    unique_labels = sorted(set(labels_raw))
    label_map = {v: i for i, v in enumerate(unique_labels)}
    labels = np.array([label_map[v] for v in labels_raw])

    print(f"Loaded {name}: {X.shape[0]} cells, {X.shape[1]} markers, "
          f"{len(unique_labels)} populations")

    return X, labels, marker_names


def generate_synthetic_benchmark(
    n_cells: int = 50000,
    n_features: int = 15,
    n_populations: int = 12,
    rare_fraction: float = 0.01,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Generate a realistic synthetic cytometry-like dataset with known ground truth.

    Designed to be challenging: overlapping populations, variable spread,
    genuinely rare subsets, and hierarchical structure (some populations are
    sub-types of broader groups, placed close in feature space).
    """
    rng = np.random.default_rng(seed)

    # Create hierarchical centers: 4 "lineages" with 3 sub-populations each
    n_lineages = n_populations // 3
    lineage_centers = rng.normal(scale=4.0, size=(n_lineages, n_features))
    centers = []
    for lc in lineage_centers:
        for _ in range(3):
            offset = rng.normal(scale=1.0, size=n_features)
            centers.append(lc + offset)
    centers = np.array(centers[:n_populations])

    # Variable population sizes: 3 rare, rest abundant
    n_rare = 3
    pop_sizes = []
    rare_total = int(n_cells * rare_fraction * n_rare)
    abundant_total = n_cells - rare_total

    for i in range(n_populations):
        if i < n_rare:
            pop_sizes.append(max(20, int(n_cells * rare_fraction)))
        else:
            weight = 1.0 + rng.uniform(0, 1.5)
            pop_sizes.append(int(weight * abundant_total / (n_populations - n_rare)))

    total = sum(pop_sizes)
    pop_sizes = [max(20, int(s * n_cells / total)) for s in pop_sizes]
    pop_sizes[-1] = n_cells - sum(pop_sizes[:-1])

    X_parts = []
    label_parts = []
    for i, size in enumerate(pop_sizes):
        if i < n_rare:
            spread = rng.uniform(0.5, 1.0)
        else:
            spread = rng.uniform(1.0, 2.5)
        per_feat_spread = spread * (0.5 + rng.uniform(size=n_features))
        X_parts.append(
            rng.normal(loc=centers[i], scale=per_feat_spread, size=(size, n_features))
        )
        label_parts.append(np.full(size, i))

    X = np.vstack(X_parts)
    labels = np.concatenate(label_parts)
    X += rng.normal(scale=0.2, size=X.shape)

    idx = rng.permutation(len(X))
    X = X[idx]
    labels = labels[idx]

    marker_names = [f"marker_{i}" for i in range(n_features)]
    return X, labels, marker_names


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            if name == "synthetic":
                X, labels, markers = generate_synthetic_benchmark()
                print(f"Synthetic: {X.shape[0]} cells, {X.shape[1]} markers, "
                      f"{len(np.unique(labels))} populations")
            else:
                X, labels, markers = load_dataset(name)
    else:
        print("Available datasets:")
        for name, info in DATASETS.items():
            print(f"  {name}: {info['description']}")
        print("  synthetic: Generated challenging benchmark data")
        print("\nUsage: python download_data.py Levine_32dim")
