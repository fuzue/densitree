# Improvements over Standard SPADE

densitree implements the core SPADE algorithm faithfully but also introduces several improvements and extension points that address known limitations of the original method.

## 1. Deterministic mode

**Problem**: The original SPADE produces different results on each run due to stochastic downsampling. This was identified as a major reproducibility concern by [Qiu (2017)](https://doi.org/10.1002/cyto.a.23068).

**densitree solution**: The `random_state` parameter seeds all stochastic operations (downsampling, spring layout for visualization). With a fixed seed, results are fully deterministic:

```python
spade = SPADE(n_clusters=30, random_state=42)
labels_a = spade.fit_predict(X)
labels_b = spade.fit_predict(X)
assert np.array_equal(labels_a, labels_b)  # always True
```

## 2. Pluggable density estimation

**Problem**: The standard k-NN density estimator can be sensitive to the choice of $k$ and performs poorly on data with highly variable local density scales.

**densitree solution**: The `density_estimator` parameter accepts any `BaseStep` subclass, enabling drop-in replacement with alternative density methods:

```python
from densitree import SPADE, BaseStep
import numpy as np
from scipy.stats import gaussian_kde

class KDEDensity(BaseStep):
    def __init__(self, bandwidth="scott"):
        self.bandwidth = bandwidth

    def run(self, data, **ctx):
        kde = gaussian_kde(data.T, bw_method=self.bandwidth)
        return {"density": kde(data.T)}

spade = SPADE(density_estimator=KDEDensity(), n_clusters=30)
```

Other candidates worth exploring:

- **Local outlier factor (LOF)** density from scikit-learn
- **KDE with adaptive bandwidth** for multi-scale density
- **Shared nearest neighbor (SNN)** density, which is more robust to dimensionality

## 3. Flexible transforms

**Problem**: The original SPADE used a fixed arcsinh transform. Different data types (CyTOF, fluorescence flow, spectral flow, scRNA-seq) benefit from different transforms.

**densitree solution**: Built-in `"arcsinh"`, `"log"`, and `None` transforms with configurable cofactor. The transform is applied before all pipeline steps, so clustering and density estimation operate in the transformed space while medians in the result are computed in the original space.

## 4. scikit-learn compatible API

**Problem**: The original R implementation uses a bespoke, script-oriented API that doesn't integrate well with modern ML workflows.

**densitree solution**: Standard `fit()` / `fit_predict()` interface. This enables:

- Pipeline composition with `sklearn.pipeline.Pipeline`
- Hyperparameter search with `GridSearchCV` (over `n_clusters`, `downsample_target`, `knn`)
- Drop-in comparison with any sklearn-compatible clusterer

## 5. Rich result object

**Problem**: Extracting cluster statistics, tree structure, and visualization from the R implementation requires multiple separate function calls and manual bookkeeping.

**densitree solution**: `SPADEResult` bundles everything -- labels, tree, downsampled data, cluster statistics DataFrame -- in a single object with a `plot_tree()` method.

---

## Planned improvements

### Adaptive cluster count

Instead of requiring a fixed `n_clusters`, automatically select the number of clusters using the gap statistic or silhouette score on the downsampled data:

$$k^* = \arg\max_k \text{Silhouette}(X_\text{down}, \text{labels}_k)$$

This would add an `n_clusters="auto"` mode.

### Multi-run consensus

Run SPADE multiple times with different random seeds and build a consensus tree. This addresses the stochasticity concern more robustly than a single deterministic run by capturing the stable structure across runs. The consensus approach was suggested by [Qiu (2017)](https://doi.org/10.1002/cyto.a.23068).

### Approximate k-NN for large datasets

For datasets with $n > 10^6$ cells, exact k-NN becomes a bottleneck. Using approximate nearest neighbor libraries (PyNNDescent, FAISS, Annoy) for density estimation would provide near-linear scaling.

### Edge significance testing

Not all edges in the MST are equally meaningful. Adding a permutation-based significance test for edge weights would help distinguish biologically meaningful connections from noise-driven ones.

### Marker-specific downsampling

The current approach uses a single density estimate across all markers. For panels with functionally distinct marker groups (e.g., surface markers vs. intracellular signaling), computing density on a subset of markers (typically surface/lineage markers) while clustering on all markers may produce better trees.
