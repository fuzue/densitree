"""Benchmark densitree against other clustering methods on standard cytometry datasets.

Comparisons:
- densitree (this library)
- scikit-learn AgglomerativeClustering (no downsampling baseline)
- scikit-learn KMeans (fast baseline)
- PhenoGraph-style (k-NN graph + Leiden community detection)
- FlowSOM-style (MiniBatchKMeans + agglomerative metaclustering)

Metrics:
- Adjusted Rand Index (ARI) vs ground truth
- Normalized Mutual Information (NMI) vs ground truth
- Rare population F1 score
- Runtime (seconds)

Each method is run 5 times (where stochastic) and we report mean +/- std.
"""
from __future__ import annotations

import json
import time
import warnings
from dataclasses import dataclass, field, asdict
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score, f1_score
from sklearn.cluster import AgglomerativeClustering, KMeans, MiniBatchKMeans
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

# Suppress convergence warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)

RESULTS_DIR = Path(__file__).parent / "results"


@dataclass
class BenchmarkResult:
    method: str
    dataset: str
    n_clusters: int
    ari: float
    ari_std: float
    nmi: float
    nmi_std: float
    rare_f1: float
    rare_f1_std: float
    runtime_s: float
    runtime_std: float
    n_runs: int = 5


def arcsinh_transform(X: np.ndarray, cofactor: float = 5.0) -> np.ndarray:
    return np.arcsinh(X / cofactor)


def compute_rare_f1(
    labels_true: np.ndarray,
    labels_pred: np.ndarray,
    rare_threshold: float = 0.03,
) -> float:
    """Compute F1 score specifically for rare populations.

    A population is 'rare' if it comprises < rare_threshold of total cells.
    We compute macro-averaged F1 across only these rare populations.
    """
    unique, counts = np.unique(labels_true, return_counts=True)
    total = len(labels_true)
    rare_pops = unique[counts / total < rare_threshold]

    if len(rare_pops) == 0:
        return float("nan")

    # For each rare population, find which predicted cluster best matches it
    # (maximum overlap), then compute precision/recall for that pair
    f1s = []
    for pop in rare_pops:
        true_mask = labels_true == pop
        # Find the predicted cluster with highest overlap
        pred_labels_in_pop = labels_pred[true_mask]
        if len(pred_labels_in_pop) == 0:
            f1s.append(0.0)
            continue

        best_cluster = np.bincount(pred_labels_in_pop).argmax()
        pred_mask = labels_pred == best_cluster

        tp = (true_mask & pred_mask).sum()
        fp = pred_mask.sum() - tp
        fn = true_mask.sum() - tp

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        f1s.append(f1)

    return float(np.mean(f1s))


# ---------- Method implementations ----------


def run_densitree(X: np.ndarray, n_clusters: int, seed: int) -> np.ndarray:
    from densitree import SPADE
    spade = SPADE(
        n_clusters=n_clusters,
        downsample_target=0.1,
        knn=5,
        transform=None,  # data is already transformed
        random_state=seed,
    )
    return spade.fit_predict(X)


def run_agglomerative(X: np.ndarray, n_clusters: int, seed: int) -> np.ndarray:
    """Agglomerative clustering without downsampling (baseline)."""
    # For large datasets, subsample first (agglomerative is O(n^2))
    if len(X) > 20000:
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(X), 20000, replace=False)
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
        sub_labels = model.fit_predict(X[idx])
        # Assign remaining cells to nearest cluster centroid
        centroids = np.array([X[idx][sub_labels == i].mean(axis=0) for i in range(n_clusters)])
        nn = NearestNeighbors(n_neighbors=1).fit(centroids)
        _, indices = nn.kneighbors(X)
        return indices[:, 0]
    else:
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
        return model.fit_predict(X)


def run_kmeans(X: np.ndarray, n_clusters: int, seed: int) -> np.ndarray:
    """KMeans clustering (fast baseline)."""
    model = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    return model.fit_predict(X)


def run_phenograph_style(X: np.ndarray, n_clusters: int, seed: int) -> np.ndarray:
    """PhenoGraph-style: k-NN graph + Leiden community detection.

    Note: n_clusters is not directly controllable -- Leiden finds its own
    number of communities. We adjust resolution to approximate n_clusters.
    """
    try:
        import igraph as ig
        import leidenalg
    except ImportError:
        raise ImportError("leidenalg and igraph required. pip install leidenalg igraph")

    k = 30
    nn = NearestNeighbors(n_neighbors=k + 1)
    nn.fit(X)
    distances, indices = nn.kneighbors(X)

    # Build k-NN graph (Jaccard-weighted)
    n = len(X)
    edges = []
    weights = []
    neighbor_sets = [set(indices[i, 1:]) for i in range(n)]

    for i in range(n):
        for j_idx in range(1, k + 1):
            j = indices[i, j_idx]
            if j > i:
                # Jaccard similarity
                intersection = len(neighbor_sets[i] & neighbor_sets[j])
                union = len(neighbor_sets[i] | neighbor_sets[j])
                w = intersection / union if union > 0 else 0
                if w > 0:
                    edges.append((i, j))
                    weights.append(w)

    g = ig.Graph(n=n, edges=edges)
    g.es["weight"] = weights

    # Adjust resolution to approximate target n_clusters
    resolution = 0.5
    for _ in range(10):
        partition = leidenalg.find_partition(
            g, leidenalg.RBConfigurationVertexPartition,
            weights="weight", resolution_parameter=resolution,
            seed=seed,
        )
        n_found = len(set(partition.membership))
        if abs(n_found - n_clusters) <= 5:
            break
        if n_found < n_clusters:
            resolution *= 1.5
        else:
            resolution *= 0.7

    return np.array(partition.membership)


def run_flowsom_style(X: np.ndarray, n_clusters: int, seed: int) -> np.ndarray:
    """FlowSOM-style: MiniBatchKMeans overclustering + agglomerative metaclustering.

    This mimics FlowSOM's two-stage approach:
    1. Overcluster into 10*n_clusters microclusters using MiniBatchKMeans (fast SOM proxy)
    2. Merge microclusters into n_clusters metaclusters using agglomerative clustering
    """
    n_micro = min(10 * n_clusters, len(X) // 10)

    # Stage 1: overclustering
    micro = MiniBatchKMeans(n_clusters=n_micro, random_state=seed, batch_size=1024)
    micro_labels = micro.fit_predict(X)
    centroids = micro.cluster_centers_

    # Stage 2: metaclustering
    meta = AgglomerativeClustering(n_clusters=n_clusters, linkage="average")
    meta_labels = meta.fit_predict(centroids)

    # Map micro -> meta
    return meta_labels[micro_labels]


def run_flowsom_official(X: np.ndarray, n_clusters: int, seed: int) -> np.ndarray:
    """Official FlowSOM Python port (saeyslab/FlowSOM_Python).

    Uses the actual FlowSOM algorithm: SOM + consensus metaclustering.
    """
    try:
        import flowsom as fs
        import anndata as ad
    except ImportError:
        raise ImportError("flowsom required. pip install flowsom")

    adata = ad.AnnData(X)
    fsom = fs.FlowSOM(
        adata,
        cols_to_use=list(range(X.shape[1])),
        xdim=10, ydim=10,  # 10x10 SOM grid = 100 microclusters
        n_clusters=n_clusters,
        seed=seed,
    )
    return fsom.get_cell_data().obs["metaclustering"].astype(int).values


# ---------- Benchmark runner ----------

METHODS = {
    "densitree": run_densitree,
    "agglomerative": run_agglomerative,
    "kmeans": run_kmeans,
    "phenograph_style": run_phenograph_style,
    "flowsom_style": run_flowsom_style,
    "flowsom_official": run_flowsom_official,
}


def benchmark_method(
    method_name: str,
    method_fn,
    X: np.ndarray,
    labels_true: np.ndarray,
    n_clusters: int,
    n_runs: int = 5,
) -> BenchmarkResult:
    """Run a method multiple times and collect metrics."""
    aris, nmis, f1s, times = [], [], [], []

    for run_idx in range(n_runs):
        seed = 42 + run_idx
        t0 = time.perf_counter()
        try:
            labels_pred = method_fn(X, n_clusters, seed)
        except Exception as e:
            print(f"  [ERROR] {method_name} run {run_idx}: {e}")
            continue
        elapsed = time.perf_counter() - t0

        ari = adjusted_rand_score(labels_true, labels_pred)
        nmi = normalized_mutual_info_score(labels_true, labels_pred)
        rf1 = compute_rare_f1(labels_true, labels_pred)

        aris.append(ari)
        nmis.append(nmi)
        f1s.append(rf1)
        times.append(elapsed)

        print(f"  {method_name} run {run_idx}: ARI={ari:.3f} NMI={nmi:.3f} F1_rare={rf1:.3f} time={elapsed:.1f}s")

    if not aris:
        return BenchmarkResult(
            method=method_name, dataset="", n_clusters=n_clusters,
            ari=0, ari_std=0, nmi=0, nmi_std=0,
            rare_f1=0, rare_f1_std=0, runtime_s=0, runtime_std=0, n_runs=0,
        )

    return BenchmarkResult(
        method=method_name,
        dataset="",
        n_clusters=n_clusters,
        ari=float(np.mean(aris)),
        ari_std=float(np.std(aris)),
        nmi=float(np.mean(nmis)),
        nmi_std=float(np.std(nmis)),
        rare_f1=float(np.nanmean(f1s)),
        rare_f1_std=float(np.nanstd(f1s)),
        runtime_s=float(np.mean(times)),
        runtime_std=float(np.std(times)),
        n_runs=len(aris),
    )


def run_benchmark(
    dataset_name: str,
    X: np.ndarray,
    labels_true: np.ndarray,
    n_clusters: int | None = None,
    methods: list[str] | None = None,
    n_runs: int = 5,
) -> list[BenchmarkResult]:
    """Run all methods on a dataset and return results."""
    if n_clusters is None:
        n_clusters = len(np.unique(labels_true))

    if methods is None:
        methods = list(METHODS.keys())

    # Pre-transform data (arcsinh with cofactor=5 for CyTOF)
    X_t = arcsinh_transform(X, cofactor=5.0)

    results = []
    for method_name in methods:
        if method_name not in METHODS:
            print(f"Unknown method: {method_name}, skipping")
            continue

        print(f"\n--- {method_name} on {dataset_name} (n_clusters={n_clusters}) ---")
        result = benchmark_method(
            method_name, METHODS[method_name], X_t, labels_true,
            n_clusters=n_clusters, n_runs=n_runs,
        )
        result.dataset = dataset_name
        results.append(result)

    return results


def results_to_dataframe(results: list[BenchmarkResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append({
            "Dataset": r.dataset,
            "Method": r.method,
            "n_clusters": r.n_clusters,
            "ARI": f"{r.ari:.3f} +/- {r.ari_std:.3f}",
            "NMI": f"{r.nmi:.3f} +/- {r.nmi_std:.3f}",
            "Rare F1": f"{r.rare_f1:.3f} +/- {r.rare_f1_std:.3f}",
            "Runtime (s)": f"{r.runtime_s:.1f} +/- {r.runtime_std:.1f}",
            "ARI_mean": r.ari,
            "NMI_mean": r.nmi,
            "Rare_F1_mean": r.rare_f1,
            "Runtime_mean": r.runtime_s,
        })
    return pd.DataFrame(rows)


def save_results(results: list[BenchmarkResult], tag: str = "benchmark") -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = RESULTS_DIR / f"{tag}.json"
    with open(json_path, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    print(f"\nSaved JSON: {json_path}")

    # Save markdown table
    df = results_to_dataframe(results)
    display_cols = ["Dataset", "Method", "n_clusters", "ARI", "NMI", "Rare F1", "Runtime (s)"]
    md_path = RESULTS_DIR / f"{tag}.md"
    with open(md_path, "w") as f:
        f.write(f"# Benchmark Results: {tag}\n\n")
        f.write(df[display_cols].to_markdown(index=False))
        f.write("\n")
    print(f"Saved Markdown: {md_path}")

    # Save CSV
    csv_path = RESULTS_DIR / f"{tag}.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved CSV: {csv_path}")


if __name__ == "__main__":
    import sys
    from download_data import load_dataset, generate_synthetic_benchmark

    dataset_name = sys.argv[1] if len(sys.argv) > 1 else "synthetic"
    methods = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    n_runs = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    if dataset_name == "synthetic":
        print("Using synthetic benchmark dataset...")
        X, labels, markers = generate_synthetic_benchmark()
    else:
        print(f"Loading {dataset_name}...")
        X, labels, markers = load_dataset(dataset_name)

    # For real datasets: remove ungated cells (label 0 = unassigned in lmweber data)
    # Population 0 in Levine/Samusik is the ungated/unassigned class
    if dataset_name != "synthetic":
        gated_mask = labels > 0
        n_ungated = (~gated_mask).sum()
        if n_ungated > 0:
            print(f"  Removing {n_ungated} ungated cells ({100*n_ungated/len(labels):.1f}%)")
            X = X[gated_mask]
            labels = labels[gated_mask]
            # Re-encode labels to be 0-indexed
            unique = np.unique(labels)
            label_map = {v: i for i, v in enumerate(unique)}
            labels = np.array([label_map[v] for v in labels])

    print(f"Dataset: {dataset_name}")
    print(f"  Cells: {X.shape[0]}, Markers: {X.shape[1]}")
    print(f"  Populations: {len(np.unique(labels))}")

    unique, counts = np.unique(labels, return_counts=True)
    rare = unique[counts / len(labels) < 0.03]
    print(f"  Rare populations (<3%): {len(rare)}")

    results = run_benchmark(dataset_name, X, labels, methods=methods, n_runs=n_runs)
    save_results(results, tag=dataset_name)

    # Print summary
    df = results_to_dataframe(results)
    print("\n" + "=" * 80)
    print(df[["Dataset", "Method", "ARI", "NMI", "Rare F1", "Runtime (s)"]].to_string(index=False))
