# Benchmark Datasets

## Levine_32dim

The standard benchmark dataset for cytometry clustering methods.

| Property | Value |
|---|---|
| **Source** | [Levine et al. (2015) Cell 162(1):184-197](https://doi.org/10.1016/j.cell.2015.05.047) |
| **Total cells** | 265,627 |
| **Gated cells** | 104,184 (39.2%) |
| **Markers** | 32 surface CyTOF markers |
| **Populations** | 14 manually gated immune populations |
| **Rare populations (<3%)** | 7 |
| **Technology** | CyTOF (mass cytometry) |
| **Tissue** | Human bone marrow |

### Population distribution

| Population | Cells | Fraction |
|---|---|---|
| Large (>5%) | 4 populations | ~32% of gated cells each |
| Medium (1-5%) | 3 populations | ~2% each |
| Rare (<1%) | 7 populations | 0.1--0.5% each |

The high number of rare populations (half of all populations) makes this dataset particularly challenging for methods that don't account for density imbalance.

### Download

The dataset is automatically downloaded from [lmweber/benchmark-data-Levine-32-dim](https://github.com/lmweber/benchmark-data-Levine-32-dim) when first used:

```python
from benchmarks.download_data import load_dataset
X, labels, markers = load_dataset("Levine_32dim")
```

### Preprocessing

- Ungated cells (60.8% of total) are removed for evaluation
- Data is arcsinh-transformed with cofactor 5 (standard for CyTOF) before clustering
- All 32 surface markers are used for clustering

---

## Synthetic

A challenging synthetic dataset designed to stress-test clustering methods with overlapping populations, hierarchical structure, and rare subsets.

| Property | Value |
|---|---|
| **Cells** | 50,000 |
| **Features** | 15 |
| **Populations** | 12 |
| **Rare populations (<3%)** | 3 |
| **Seed** | 42 (deterministic) |

### Design

- **4 lineages** of 3 sub-populations each -- sub-populations within a lineage are close in feature space (harder to separate)
- **Per-feature variable spread** -- some markers are more discriminative than others
- **3 rare populations** (~1% each, tighter clusters)
- **Global measurement noise** added

```python
from benchmarks.download_data import generate_synthetic_benchmark
X, labels, markers = generate_synthetic_benchmark()
```
