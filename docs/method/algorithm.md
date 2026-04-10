# The SPADE Algorithm

SPADE (Spanning-tree Progression Analysis of Density-normalized Events) was introduced by [Qiu et al. (2011)](https://doi.org/10.1038/nbt.1991) to extract cellular hierarchies from high-dimensional cytometry data.

## Motivation

In cytometry experiments, cells are measured across many markers simultaneously (10--50+ parameters). The resulting data has millions of cells in high-dimensional space. Two key challenges arise:

1. **Abundant populations dominate**: Mature cell types (e.g., T cells, B cells) vastly outnumber rare progenitors. Standard clustering algorithms allocate most clusters to these abundant types, losing resolution on rare but biologically important populations.

2. **Hierarchy matters**: Cells don't just form isolated clusters -- they form a developmental continuum. A flat clustering misses the progression from stem cells through progenitors to mature cells.

SPADE addresses both problems.

## Algorithm steps

### Step 1: Density estimation

For each cell $i$, compute local density $\rho_i$ using $k$-nearest neighbor distances:

$$\rho_i = \frac{1}{d_k(i) + \epsilon}$$

where $d_k(i)$ is the distance to the $k$-th nearest neighbor and $\epsilon$ is a small constant to avoid division by zero.

Cells in crowded regions (abundant populations) get high density; cells in sparse regions (rare populations) get low density.

**densitree default**: $k = 5$, implemented in `DensityEstimator`.

### Step 2: Density-dependent downsampling

Each cell is included in the downsampled set with probability:

$$p_i = \min\left(1, \; \frac{T \cdot w_i}{\sum_j w_j}\right), \qquad w_i = \frac{1}{\rho_i}$$

where $T$ is the target number of cells to retain. Cells in dense regions have high $\rho_i$, therefore low $w_i$ and low inclusion probability. Rare populations (low $\rho_i$, high $w_i$) are preferentially retained.

This is the signature innovation of SPADE. After downsampling, the cell distribution is approximately uniform across phenotypic space, giving rare populations equal representation.

**densitree default**: `downsample_target=0.05` (retain 5% of cells).

### Step 3: Agglomerative clustering

The downsampled cells are clustered using Ward's linkage hierarchical agglomerative clustering into $k$ clusters. Ward's linkage minimizes within-cluster variance at each merge step, producing compact, spherical clusters in marker space.

**densitree default**: `n_clusters=50`, `linkage="ward"`.

### Step 4: Upsampling

Every original cell (not just the downsampled ones) is assigned to the nearest cluster centroid in the transformed feature space. This restores the full dataset's cluster assignments without re-running the expensive clustering.

### Step 5: Minimum spanning tree

A complete graph is constructed over the $k$ cluster centroids, with edge weights equal to the Euclidean distance between centroids. The minimum spanning tree (MST) of this graph is extracted using Kruskal's or Prim's algorithm (via scipy).

The MST captures the shortest-path connectivity between clusters. In biological data, branches in the tree correspond to differentiation trajectories -- a path from a stem cell cluster through intermediate progenitors to a mature cell type.

Each node in the tree is annotated with:

- **size**: number of cells assigned to that cluster
- **median**: per-marker median expression of cells in that cluster

## Data transforms

Raw cytometry data spans several orders of magnitude. Before running SPADE, markers are typically transformed:

| Transform | Formula | Use case |
|---|---|---|
| arcsinh | $\text{arcsinh}(x / c)$ | CyTOF ($c=5$), flow cytometry ($c=150$) |
| log | $\log(1 + x)$ | Count data |
| None | $x$ | Pre-transformed data |

The arcsinh transform is approximately linear near zero and logarithmic for large values, handling the dynamic range of fluorescence/mass signals well.

## Complexity

| Step | Time complexity | Space complexity |
|---|---|---|
| Density estimation (k-NN) | $O(n \log n)$ | $O(n)$ |
| Downsampling | $O(n)$ | $O(n)$ |
| Agglomerative clustering | $O(m^2 \log m)$ where $m = T$ | $O(m^2)$ |
| Upsampling (1-NN) | $O(n \log k)$ | $O(n)$ |
| MST construction | $O(k^2)$ | $O(k^2)$ |

The bottleneck is typically the density estimation step for very large datasets ($n > 10^6$).
