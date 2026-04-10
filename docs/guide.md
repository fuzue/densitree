# densitree User Guide

A Python implementation of the **SPADE** (Spanning-tree Progression Analysis of Density-normalized Events) algorithm for high-dimensional cytometry and single-cell data analysis.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [API Reference](#api-reference)
5. [Examples](#examples)
6. [Method Background & Literature](#method-background--literature)
7. [Comparison with Other Tools](#comparison-with-other-tools)

---

## Installation

```bash
pip install -e ".[dev]"
```

Dependencies: numpy, scipy, scikit-learn, networkx, matplotlib, plotly, pandas.

---

## Quick Start

```python
import numpy as np
from densitree import SPADE

# Generate synthetic data: 1000 cells, 5 markers
rng = np.random.default_rng(42)
X = np.vstack([
    rng.normal(loc=[0, 0, 5, 3, 1], scale=0.5, size=(300, 5)),
    rng.normal(loc=[4, 4, 1, 1, 6], scale=0.5, size=(400, 5)),
    rng.normal(loc=[8, 2, 3, 7, 2], scale=0.5, size=(300, 5)),
])

spade = SPADE(n_clusters=10, downsample_target=0.2, random_state=0)
spade.fit(X)

print(spade.labels_[:20])              # cluster labels for every cell
print(spade.result_.cluster_stats_)    # per-cluster summary table

spade.result_.plot_tree(color_by=0, backend="matplotlib")
```

---

## Core Concepts

SPADE works in five sequential steps:

1. **Density estimation** -- For each cell, compute local density via k-nearest-neighbor distances. Cells in crowded regions get high density scores.

2. **Density-dependent downsampling** -- Cells in dense regions are sampled with lower probability, while rare populations are preserved. This prevents abundant cell types from dominating the clustering.

3. **Agglomerative clustering** -- The downsampled cells are clustered into `n_clusters` groups using Ward's linkage hierarchical clustering.

4. **Upsampling** -- Every original cell (not just the downsampled ones) is assigned to the cluster whose centroid is nearest.

5. **Minimum spanning tree (MST)** -- Cluster centroids are connected into a tree where edge weights are Euclidean distances. This tree captures the progression/hierarchy structure of the data.

### Data transforms

Before any step runs, an optional transform is applied to all features:

| `transform` | Formula | Typical use |
|---|---|---|
| `"arcsinh"` (default) | `arcsinh(x / cofactor)` | CyTOF data (cofactor=5) or flow cytometry (cofactor=150) |
| `"log"` | `log(1 + x)` | Count data, scRNA-seq |
| `None` | Identity | Already-transformed data |

---

## API Reference

### `SPADE`

```python
SPADE(
    n_clusters=50,          # number of clusters in the tree
    downsample_target=0.05, # fraction of cells to retain
    knn=5,                  # k for density estimation
    transform="arcsinh",    # "arcsinh", "log", or None
    cofactor=150.0,         # arcsinh cofactor
    random_state=None,      # seed for reproducibility
)
```

**Methods:**

| Method | Returns | Description |
|---|---|---|
| `fit(X)` | `self` | Run the full SPADE pipeline |
| `fit_predict(X)` | `ndarray` | Run pipeline and return cluster labels |

**Attributes (after `fit`):**

| Attribute | Type | Description |
|---|---|---|
| `labels_` | `ndarray[int]` | Cluster assignment for every cell |
| `result_` | `SPADEResult` | Rich output object (see below) |

Input `X` can be a numpy array or a pandas DataFrame. If a DataFrame is passed, column names are preserved in the result.

### `SPADEResult`

| Attribute | Type | Description |
|---|---|---|
| `labels_` | `ndarray[int]` | Cluster labels (same as `SPADE.labels_`) |
| `tree_` | `networkx.Graph` | MST with node attributes `size` and `median` |
| `X_down` | `ndarray` | Downsampled cell matrix |
| `down_idx` | `ndarray[int]` | Indices of downsampled cells in the original array |
| `cluster_stats_` | `pd.DataFrame` | One row per cluster: `size`, `median_<feature>` columns |

**Methods:**

```python
result.plot_tree(
    color_by=None,          # feature index (int) or name (str) to color nodes
    size_by="count",        # "count" scales nodes by cell count
    backend="matplotlib",   # "matplotlib" or "plotly"
)
```

### `BaseStep`

Abstract base class for pipeline steps. Subclass it to create custom steps:

```python
from densitree import BaseStep
import numpy as np

class MyDensityEstimator(BaseStep):
    def run(self, data: np.ndarray, **ctx) -> dict:
        # your custom density logic
        return {"density": my_density_values}

spade = SPADE(density_estimator=MyDensityEstimator())
```

---

## Examples

### Example 1: Basic flow cytometry analysis

```python
import pandas as pd
from densitree import SPADE

# Load a CSV exported from FlowJo or similar
df = pd.read_csv("flow_data.csv")
markers = ["CD3", "CD4", "CD8", "CD19", "CD56"]
X = df[markers]

spade = SPADE(
    n_clusters=30,
    downsample_target=0.1,
    transform="arcsinh",
    cofactor=150.0,    # standard for fluorescence flow cytometry
    random_state=42,
)
spade.fit(X)

# Explore clusters
print(spade.result_.cluster_stats_)

# Color tree by CD4 expression
fig = spade.result_.plot_tree(color_by="CD4", backend="matplotlib")
fig.savefig("spade_tree_cd4.png", dpi=150, bbox_inches="tight")
```

### Example 2: CyTOF / mass cytometry data

```python
from densitree import SPADE

# CyTOF uses cofactor=5 for arcsinh transform
spade = SPADE(
    n_clusters=50,
    downsample_target=0.05,
    transform="arcsinh",
    cofactor=5.0,
    random_state=0,
)
spade.fit(X_cytof)  # numpy array, shape (n_cells, n_markers)

# Interactive plotly visualization
fig = spade.result_.plot_tree(color_by=0, backend="plotly")
fig.show()
```

### Example 3: Comparing conditions

```python
import numpy as np
from densitree import SPADE

# Fit on combined data from two conditions
X_combined = np.vstack([X_healthy, X_disease])
condition = np.array(
    ["healthy"] * len(X_healthy) + ["disease"] * len(X_disease)
)

spade = SPADE(n_clusters=20, downsample_target=0.1, random_state=0)
spade.fit(X_combined)

# Count cells per cluster per condition
labels = spade.labels_
for cluster_id in range(20):
    mask = labels == cluster_id
    n_healthy = (condition[mask] == "healthy").sum()
    n_disease = (condition[mask] == "disease").sum()
    print(f"Cluster {cluster_id}: healthy={n_healthy}, disease={n_disease}")
```

### Example 4: Working with the tree directly (networkx)

```python
import networkx as nx
from densitree import SPADE

spade = SPADE(n_clusters=15, downsample_target=0.1, random_state=0)
spade.fit(X)

tree = spade.result_.tree_

# Find the two most connected clusters (highest degree)
degrees = sorted(tree.degree, key=lambda x: x[1], reverse=True)
print(f"Hub clusters: {degrees[:3]}")

# Shortest path between two clusters
path = nx.shortest_path(tree, source=0, target=10, weight="weight")
print(f"Path from cluster 0 to 10: {path}")

# Export tree for use in other tools
nx.write_graphml(tree, "spade_tree.graphml")
```

### Example 5: Custom density estimator

```python
import numpy as np
from densitree import SPADE, BaseStep

class KDEDensityEstimator(BaseStep):
    """Use scipy KDE instead of k-NN for density estimation."""

    def __init__(self, bandwidth: float = 1.0):
        self.bandwidth = bandwidth

    def run(self, data: np.ndarray, **ctx) -> dict:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(data.T, bw_method=self.bandwidth)
        density = kde(data.T)
        return {"density": density}

spade = SPADE(
    n_clusters=10,
    downsample_target=0.1,
    density_estimator=KDEDensityEstimator(bandwidth=0.5),
    random_state=0,
)
spade.fit(X)
```

### Example 6: Exporting results to a DataFrame

```python
import pandas as pd
from densitree import SPADE

spade = SPADE(n_clusters=20, downsample_target=0.1, random_state=0)
spade.fit(X)

# Add cluster labels back to original data
df_annotated = pd.DataFrame(X, columns=marker_names)
df_annotated["spade_cluster"] = spade.labels_
df_annotated.to_csv("annotated_cells.csv", index=False)

# Export cluster statistics
spade.result_.cluster_stats_.to_csv("cluster_stats.csv")
```

---

## Method Background & Literature

### The SPADE algorithm

SPADE was introduced to address a fundamental challenge in cytometry: how to organize high-dimensional single-cell data into an interpretable hierarchy that reflects biological structure (e.g., hematopoietic differentiation).

The key insight is **density-dependent downsampling**. Traditional clustering on cytometry data is dominated by abundant cell types (e.g., mature lymphocytes), causing rare populations (e.g., progenitors, transitional cells) to be absorbed into larger clusters. By downsampling proportionally to the inverse of local density, SPADE ensures rare populations are represented in the clustering step.

After clustering the downsampled cells, a **minimum spanning tree** is constructed over the cluster centroids. This tree naturally captures gradual transitions between cell phenotypes -- branches in the tree correspond to differentiation trajectories.

### Key references

1. **Qiu, P., Simonds, E.F., Bendall, S.C., et al.** (2011). "Extracting a cellular hierarchy from high-dimensional cytometry data with SPADE." *Nature Biotechnology*, 29(10), 886-891. doi:[10.1038/nbt.1991](https://doi.org/10.1038/nbt.1991)
   - The original SPADE paper. Introduces the algorithm and demonstrates it on mouse and human bone marrow CyTOF data.

2. **Bendall, S.C., Simonds, E.F., Qiu, P., et al.** (2011). "Single-cell mass cytometry of differential immune and drug responses across a human hematopoietic continuum." *Science*, 332(6030), 687-696. doi:[10.1126/science.1198704](https://doi.org/10.1126/science.1198704)
   - High-profile application of CyTOF + SPADE for mapping the human hematopoietic system.

3. **Qiu, P.** (2017). "Toward deterministic and semiautomated SPADE analysis." *Cytometry Part A*, 91(7), 714-727. doi:[10.1002/cyto.a.23068](https://doi.org/10.1002/cyto.a.23068)
   - Addresses the stochastic nature of the original algorithm and proposes improvements for reproducibility.

4. **Samusik, N., Good, Z., Spitzer, M.H., Davis, K.L., & Nolan, G.P.** (2016). "Automated mapping of phenotype space with single-cell data." *Nature Methods*, 13(6), 493-496. doi:[10.1038/nmeth.3863](https://doi.org/10.1038/nmeth.3863)
   - Systematic comparison of SPADE, FlowSOM, PhenoGraph, and other clustering methods on benchmark datasets.

5. **Levine, J.H., Simonds, E.F., Bendall, S.C., et al.** (2015). "Data-Driven Phenotypic Dissection of AML Reveals Progenitor-like Cells that Correlate with Prognosis." *Cell*, 162(1), 184-197. doi:[10.1016/j.cell.2015.05.047](https://doi.org/10.1016/j.cell.2015.05.047)
   - Introduces PhenoGraph; includes SPADE comparisons.

---

## Comparison with Other Tools

### SPADE implementations

| Feature | **densitree** | **R spade** (Bioconductor) | **Cytobank** | **FlowJo plugin** |
|---|---|---|---|---|
| Language | Python | R / C++ | Cloud (web UI) | Java (desktop) |
| Input formats | numpy, pandas | FCS files | FCS upload | FCS via FlowJo |
| scikit-learn compatible | Yes | No | No | No |
| Custom steps / extensible | Yes (BaseStep ABC) | Limited | No | No |
| Interactive visualization | plotly | No (static only) | Yes (built-in) | Yes (built-in) |
| FCS file parsing | No (bring your own) | Yes (built-in) | Yes | Yes |
| Maintained | Active | Archived | Active | Active |
| Cost | Free / open source | Free / open source | Commercial subscription | Commercial license |
| Reproducibility (seed) | Yes | Partial (improved in spade2) | Limited | Limited |

### densitree vs. R spade (Bioconductor)

The original R implementation (`spade`, now archived) was the reference. It includes FCS parsing, C++-accelerated density estimation, and direct integration with the Bioconductor/flowCore ecosystem. **densitree** trades FCS parsing for Python ecosystem integration: it works natively with numpy arrays, pandas DataFrames, and scikit-learn conventions (`fit`/`fit_predict`). If you're already working in Python (e.g., with scanpy, anndata, or general ML pipelines), densitree avoids the R interop overhead.

### densitree vs. Cytobank / FlowJo

Cytobank and FlowJo offer SPADE as part of larger GUI-driven analysis platforms. They are ideal for bench scientists who want point-and-click workflows with built-in gating, compensation, and visualization. **densitree** is for programmatic use: batch processing, reproducible pipelines, parameter sweeps, and integration with custom downstream analysis. You trade the GUI for full scripting control.

### SPADE vs. other single-cell clustering methods

| Method | Key idea | Output | Best for |
|---|---|---|---|
| **SPADE** | Density-normalized downsampling + MST | Tree of clusters | Hierarchy/trajectory visualization, rare population preservation |
| **FlowSOM** | Self-organizing maps + consensus clustering | Grid/tree of clusters | Fast, scalable, good default for most panels |
| **PhenoGraph** | k-NN graph + Louvain community detection | Flat clusters | Discovering phenotypically distinct populations |
| **UMAP + Leiden** | Dimension reduction + graph clustering | Flat clusters + 2D embedding | Exploratory visualization, scRNA-seq |

**When to use SPADE over alternatives:**

- You care about **tree structure** -- SPADE's MST explicitly models gradual transitions between cell types, which is valuable for differentiation studies.
- You need to **preserve rare populations** -- the density-dependent downsampling is SPADE's signature feature.
- You want an **interpretable number of clusters** -- SPADE's `n_clusters` parameter gives direct control, unlike graph-based methods where cluster count emerges from resolution parameters.

**When to consider alternatives:**

- For very large datasets (>1M cells), FlowSOM is typically faster.
- If you don't need tree structure and just want the best cluster assignments, PhenoGraph or Leiden clustering may give better separation.
- For scRNA-seq data, the scanpy/Leiden ecosystem is more mature and better integrated with downstream tools (DEG analysis, trajectory inference with PAGA, etc.).
