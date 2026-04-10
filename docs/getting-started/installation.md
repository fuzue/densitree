# Installation

## From PyPI

```bash
pip install densitree
```

## From source (development)

```bash
git clone https://github.com/fuzue/densitree.git
cd densitree
pip install -e ".[dev]"
```

## Dependencies

densitree requires Python 3.10+ and the following packages (installed automatically):

| Package | Minimum version | Purpose |
|---|---|---|
| numpy | 1.24 | Array operations |
| scipy | 1.10 | MST computation, distance metrics |
| scikit-learn | 1.3 | k-NN, agglomerative clustering |
| networkx | 3.0 | Tree data structure |
| matplotlib | 3.7 | Static visualization |
| plotly | 5.15 | Interactive visualization |
| pandas | 2.0 | DataFrame support, cluster statistics |

### Optional dependencies

For running benchmarks:

```bash
pip install densitree[bench]
```

This adds `flowio` (FCS file reading), `leidenalg` and `igraph` (PhenoGraph-style clustering for comparisons).

For building documentation:

```bash
pip install densitree[docs]
```
