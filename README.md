# densitree

**Density-normalized clustering with minimum spanning tree construction for high-dimensional data.**

densitree implements an improved [SPADE](https://doi.org/10.1038/nbt.1991) algorithm that combines density-dependent downsampling with consensus overclustering to produce accurate cluster assignments and interpretable tree structures. It works on any high-dimensional dataset with imbalanced density -- cytometry, single-cell RNA-seq, proteomics, or general point-cloud data.

## Benchmark results

On the standard [Levine_32dim](https://doi.org/10.1016/j.cell.2015.05.047) CyTOF benchmark (104k cells, 32 markers, 14 populations):

| Method | ARI | NMI | Runtime |
|---|---|---|---|
| **densitree** | **0.942** | **0.930** | 4.0s |
| FlowSOM | 0.934 | 0.920 | 0.1s |
| FlowSOM (official Python) | 0.914 | 0.914 | 3.6s |
| PhenoGraph-style | 0.908 | 0.906 | 88.0s |
| KMeans | 0.569 | 0.802 | 1.3s |

## Installation

```bash
pip install densitree
```

From source:

```bash
git clone https://github.com/fuzue/densitree.git
cd densitree
pip install -e ".[dev]"
```

## Quick start

```python
from densitree import SPADE

# X is any (n_samples, n_features) array or DataFrame
spade = SPADE(n_clusters=20, downsample_target=0.1, random_state=42)
spade.fit(X)

# Cluster labels for every sample
print(spade.labels_)

# Per-cluster statistics
print(spade.result_.cluster_stats_)

# Visualize the spanning tree
spade.result_.plot_tree(color_by=0, backend="matplotlib")
```

With a pandas DataFrame, column names are preserved:

```python
import pandas as pd

df = pd.read_csv("data.csv")
spade = SPADE(n_clusters=30, random_state=42)
spade.fit(df[["feature_a", "feature_b", "feature_c"]])

# Stats include median_feature_a, median_feature_b, etc.
print(spade.result_.cluster_stats_)
```

## Key features

- **State-of-the-art accuracy** -- consensus overclustering with mixed-linkage ensemble beats FlowSOM and PhenoGraph on standard benchmarks
- **scikit-learn compatible** -- `fit()` / `fit_predict()` API, works with numpy arrays and pandas DataFrames
- **Tree output** -- minimum spanning tree reveals hierarchical relationships between clusters
- **Rare population preservation** -- density-dependent downsampling ensures small subgroups are not lost
- **Extensible** -- swap any pipeline step (density estimation, clustering) via the `BaseStep` interface
- **Dual visualization** -- static matplotlib and interactive plotly backends
- **Reproducible** -- deterministic with `random_state`

## How it works

1. **Density estimation** -- k-NN local density for every sample
2. **Consensus clustering** -- multiple MiniBatchKMeans overclustering runs with ward and average linkage metaclustering, aligned via the Hungarian algorithm and combined by majority vote
3. **Density-dependent downsampling** -- rare regions are preserved for tree construction
4. **MST construction** -- cluster centroids connected into a minimum spanning tree

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `n_clusters` | 50 | Number of output clusters |
| `downsample_target` | 0.1 | Fraction of samples retained for tree construction |
| `knn` | 5 | Neighbors for density estimation |
| `n_consensus` | 10 | Overclustering runs per linkage (total = 2x). Higher = more stable. |
| `transform` | `"arcsinh"` | `"arcsinh"`, `"log"`, or `None` |
| `cofactor` | 150.0 | Arcsinh denominator (5.0 for CyTOF, 150.0 for flow cytometry) |
| `random_state` | `None` | Seed for reproducibility |

## Documentation

Full documentation with API reference, tutorials, and benchmark details:

```bash
pip install densitree[docs]
mkdocs serve
```

## Running benchmarks

```bash
pip install densitree[bench]
cd benchmarks

# Synthetic dataset
python run_benchmark.py synthetic

# Real CyTOF data (downloads Levine_32dim automatically)
python run_benchmark.py Levine_32dim
```

## License

MIT

## References

- Qiu, P. et al. (2011). "Extracting a cellular hierarchy from high-dimensional cytometry data with SPADE." *Nature Biotechnology*, 29(10), 886-891. [doi:10.1038/nbt.1991](https://doi.org/10.1038/nbt.1991)
- Levine, J.H. et al. (2015). "Data-Driven Phenotypic Dissection of AML." *Cell*, 162(1), 184-197. [doi:10.1016/j.cell.2015.05.047](https://doi.org/10.1016/j.cell.2015.05.047)
- Samusik, N. et al. (2016). "Automated mapping of phenotype space with single-cell data." *Nature Methods*, 13(6), 493-496. [doi:10.1038/nmeth.3863](https://doi.org/10.1038/nmeth.3863)
