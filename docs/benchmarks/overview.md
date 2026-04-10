# Benchmarks Overview

densitree includes a comprehensive benchmarking framework for comparing SPADE against other single-cell clustering methods on real and synthetic cytometry data.

## What we benchmark

We evaluate six clustering methods:

| Method | Implementation | Type |
|---|---|---|
| **densitree** | This library | Density-dependent downsampling + agglomerative + MST |
| **FlowSOM (official)** | `flowsom` Python package (saeyslab) | Self-organizing maps + consensus metaclustering |
| **FlowSOM-style** | MiniBatchKMeans + agglomerative | Fast reimplementation of the FlowSOM two-stage approach |
| **PhenoGraph-style** | k-NN graph + Leiden community detection | Graph-based community detection |
| **KMeans** | scikit-learn | Centroid-based flat clustering (baseline) |
| **Agglomerative** | scikit-learn (with subsampling for large data) | Ward's linkage hierarchical clustering (baseline) |

## Metrics

| Metric | What it measures | Range |
|---|---|---|
| **ARI** (Adjusted Rand Index) | Overall clustering agreement with ground truth, adjusted for chance | -1 to 1 (1 = perfect) |
| **NMI** (Normalized Mutual Information) | Information-theoretic cluster-label agreement | 0 to 1 (1 = perfect) |
| **Rare Population F1** | Precision/recall for populations comprising <3% of cells | 0 to 1 (1 = perfect) |
| **Runtime** | Wall-clock time in seconds | Lower is better |

## Datasets

- [**Levine_32dim**](datasets.md#levine_32dim): 104,184 cells (gated), 32 CyTOF markers, 14 populations
- [**Synthetic**](datasets.md#synthetic): 50,000 cells, 15 features, 12 populations (3 rare)

## Running benchmarks

```bash
cd benchmarks

# Synthetic dataset (no download needed)
python run_benchmark.py synthetic

# Real dataset (downloads automatically)
python run_benchmark.py Levine_32dim

# Specific methods only
python run_benchmark.py Levine_32dim "densitree,flowsom_official" 5
```

Results are saved to `benchmarks/results/` in JSON, CSV, and Markdown formats.
