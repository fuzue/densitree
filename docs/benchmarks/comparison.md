# Method Comparison

A detailed analysis of how densitree compares to other cytometry clustering tools across multiple dimensions.

## Algorithm comparison

| | densitree | FlowSOM | PhenoGraph | KMeans |
|---|---|---|---|---|
| **Core approach** | Density downsampling + agglomerative | SOM + consensus metaclustering | k-NN graph + Leiden | Centroid optimization |
| **Output** | Tree of clusters | Tree of metaclusters | Flat clusters | Flat clusters |
| **Handles rare pops** | Yes (density normalization) | No | Partially (graph resolution) | No |
| **Deterministic** | Yes (with seed) | Yes (with seed) | Approximately | Yes (with seed) |
| **n_clusters** | User-specified | User-specified | Automatic (resolution) | User-specified |
| **Scalability** | ~100k cells | ~1M cells | ~100k cells | ~1M+ cells |

## When to use each method

### Use densitree when:

- **Rare populations matter** -- SPADE's density-dependent downsampling is specifically designed to preserve rare subsets that would be lost by other methods
- **You need tree structure** -- the MST reveals differentiation hierarchies and gradual phenotypic transitions
- **You want overclustering + exploration** -- SPADE with 50--200 clusters produces fine-grained nodes that you can explore interactively on the tree
- **Reproducibility is critical** -- deterministic with `random_state`

### Use FlowSOM when:

- **You know the number of populations** -- FlowSOM's metaclustering is extremely effective when the expected structure matches the cluster count
- **Speed matters** -- FlowSOM is the fastest method tested, processing 100k cells in <1 second
- **The standard FlowSOM tree is sufficient** -- FlowSOM also produces a tree (the SOM grid), though it reflects SOM topology rather than phenotypic distances

### Use PhenoGraph when:

- **Discovery is the goal** -- PhenoGraph automatically determines the number of clusters, which is valuable when you don't know what to expect
- **Cluster shapes are complex** -- the graph-based approach captures non-spherical clusters that agglomerative methods miss
- **You don't need a tree** -- PhenoGraph produces flat clusters only

### Use KMeans / Agglomerative when:

- **Simplicity and speed** -- good baselines for quick exploration
- **The data is well-separated** -- these methods work fine when populations are distinct

## Implementation comparison

| Feature | densitree | FlowSOM (Python) | PhenoGraph | R spade |
|---|---|---|---|---|
| **Language** | Python | Python | Python | R/C++ |
| **API** | sklearn-compatible | AnnData/scverse | Function-based | Script-based |
| **Input** | numpy/pandas | AnnData | numpy | FCS files |
| **FCS parsing** | No (bring your own) | Via readfcs/anndata | No | Built-in |
| **Interactive viz** | plotly backend | scanpy integration | No | No |
| **Custom steps** | Yes (BaseStep ABC) | Limited | No | No |
| **pip installable** | Yes | Yes | Yes (archived) | No (BiocManager) |
| **Active** | Yes | Yes | Archived (2020) | Archived |

## Honest assessment of densitree limitations

1. **Lower ARI at matching cluster count**: When n_clusters equals the true number of populations, densitree's ARI (0.58) is significantly below FlowSOM (0.93) and PhenoGraph (0.91). This is partly because SPADE's downsampling discards information that could improve cluster boundaries.

2. **Downsampling introduces variance**: Even with a fixed seed, the particular cells retained affect downstream clustering. Running SPADE at its overclustering operating point (50+ clusters) mitigates this.

3. **No automatic cluster count**: Unlike PhenoGraph, you must specify n_clusters. The planned `n_clusters="auto"` mode (see [Improvements](../method/improvements.md)) will address this.

4. **No FCS parsing**: densitree operates on numpy arrays. You need `readfcs`, `fcsparser`, or `flowio` to read FCS files. This is by design -- densitree focuses on the algorithm, not the I/O.

## Reproducing these benchmarks

```bash
cd benchmarks
pip install readfcs flowsom leidenalg igraph

# Full benchmark on Levine_32dim (downloads 44MB FCS file)
python run_benchmark.py Levine_32dim

# Quick synthetic benchmark (no download)
python run_benchmark.py synthetic

# Specific methods, 5 runs
python run_benchmark.py Levine_32dim "densitree,flowsom_official" 5
```

See also the [R benchmarks](../benchmarks/overview.md) for comparing against R FlowSOM and the original R SPADE implementation.
