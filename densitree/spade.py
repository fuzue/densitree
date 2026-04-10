from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans, AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score as _inter_run_ari
from scipy.optimize import linear_sum_assignment

from .result import SPADEResult
from .steps.density import DensityEstimator
from .steps.downsample import DownsampleStep
from .steps.mst import MSTBuilder
from .steps.base import BaseStep


class SPADE:
    """SPADE clustering with scikit-learn-compatible API.

    Improved SPADE that combines density-dependent downsampling (for rare
    population preservation and tree construction) with consensus
    overclustering (for accurate cell assignment).

    The algorithm:

    1. **Density estimation** (k-NN) on all cells.
    2. **Consensus clustering** over multiple runs:
       a. Overcluster all cells into ``n_micro`` microclusters (MiniBatchKMeans).
       b. Merge microclusters into ``n_clusters`` metaclusters using both
          ward and average linkage agglomerative clustering.
       c. Align labels across runs (Hungarian algorithm) and take majority vote.
       d. Filter out low-agreement runs before voting.
    3. **Density-dependent downsampling** for tree construction.
    4. **MST construction** on metacluster centroids.

    Parameters
    ----------
    n_clusters : int
        Number of clusters (default 50).
    downsample_target : float
        Fraction of cells to retain for tree construction (default 0.1).
    knn : int
        k for k-NN density estimation (default 5).
    n_micro : int | None
        Number of microclusters. ``None`` uses ``min(10 * n_clusters, n_cells // 10)``.
    n_consensus : int
        Number of MiniBatchKMeans runs per linkage type for consensus.
        Total runs = 2 * n_consensus (ward + average). Default 10.
    transform : str | None
        ``'arcsinh'``, ``'log'``, or ``None``.
    cofactor : float
        Arcsinh cofactor (default 150.0).
    backend : str
        Default plotting backend.
    density_estimator : BaseStep | None
        Custom density estimator step.
    random_state : int | None
        Seed for reproducibility.
    """

    def __init__(
        self,
        n_clusters: int = 50,
        downsample_target: float = 0.1,
        knn: int = 5,
        n_micro: int | None = None,
        n_consensus: int = 10,
        transform: str | None = "arcsinh",
        cofactor: float = 150.0,
        backend: str = "matplotlib",
        density_estimator: BaseStep | None = None,
        random_state: int | None = None,
    ) -> None:
        if not 0 < downsample_target <= 1:
            raise ValueError(f"downsample_target must be in (0, 1], got {downsample_target}")
        self.n_clusters = n_clusters
        self.downsample_target = downsample_target
        self.knn = knn
        self.n_micro = n_micro
        self.n_consensus = n_consensus
        self.transform = transform
        self.cofactor = cofactor
        self.backend = backend
        self.random_state = random_state
        self._density_estimator = density_estimator or DensityEstimator(knn=knn)

        self.labels_: np.ndarray | None = None
        self.result_: SPADEResult | None = None

    def fit(self, X: np.ndarray | pd.DataFrame) -> "SPADE":
        """Fit SPADE to data."""
        feature_names: list[str] | None = None
        if isinstance(X, pd.DataFrame):
            feature_names = list(X.columns)
            X = X.values

        X = np.asarray(X, dtype=float)
        n_cells, n_features = X.shape

        if n_cells < self.n_clusters:
            raise ValueError(
                f"n_clusters ({self.n_clusters}) must be <= number of cells ({n_cells})."
            )

        X_t = self._apply_transform(X)
        seed = self.random_state or 0

        # Step 1: Density estimation
        density_ctx = self._density_estimator.run(X_t)
        density = density_ctx["density"]

        # Step 2: Consensus clustering
        n_micro = self.n_micro
        if n_micro is None:
            n_micro = min(10 * self.n_clusters, n_cells // 10)
            n_micro = max(n_micro, self.n_clusters + 1)

        if self.n_consensus <= 1:
            labels = self._single_run_cluster(X_t, n_micro, seed)
        else:
            labels = self._consensus_cluster(X_t, n_micro, n_cells, seed)

        # Step 3: Density-dependent downsampling (for tree construction)
        down_ctx = DownsampleStep(
            downsample_target=self.downsample_target,
            random_state=seed,
        ).run(X_t, density=density)

        # Step 4: MST on metacluster centroids (original space for medians)
        centroids = np.array([
            X_t[labels == c].mean(axis=0)
            if (labels == c).sum() > 0 else np.zeros(n_features)
            for c in range(self.n_clusters)
        ])
        mst_ctx = MSTBuilder().run(X, centroids=centroids, labels_=labels)

        self.labels_ = labels
        self.result_ = SPADEResult(
            labels_=labels,
            tree_=mst_ctx["tree_"],
            X_down=down_ctx["X_down"],
            down_idx=down_ctx["down_idx"],
            n_features=n_features,
            feature_names=feature_names,
        )
        return self

    def _single_run_cluster(
        self, X_t: np.ndarray, n_micro: int, seed: int,
    ) -> np.ndarray:
        """Single-run two-stage clustering."""
        micro = MiniBatchKMeans(
            n_clusters=n_micro, random_state=seed,
            batch_size=min(2048, len(X_t)), n_init=5,
        )
        micro_labels = micro.fit_predict(X_t)
        meta = AgglomerativeClustering(
            n_clusters=self.n_clusters, linkage="average",
        )
        meta_of_micro = meta.fit_predict(micro.cluster_centers_)
        return meta_of_micro[micro_labels]

    def _consensus_cluster(
        self, X_t: np.ndarray, n_micro: int, n_cells: int, base_seed: int,
    ) -> np.ndarray:
        """Consensus clustering: multiple overclustering runs with both
        ward and average linkage, aligned via Hungarian algorithm, filtered
        by inter-run agreement, and combined via majority vote.
        """
        # Generate candidate label arrays
        runs: list[np.ndarray] = []
        for r in range(self.n_consensus):
            micro = MiniBatchKMeans(
                n_clusters=n_micro, random_state=base_seed + r,
                batch_size=min(1024, n_cells), n_init=5,
            )
            micro_labels = micro.fit_predict(X_t)
            centroids = micro.cluster_centers_

            for linkage in ("ward", "average"):
                meta = AgglomerativeClustering(
                    n_clusters=self.n_clusters, linkage=linkage,
                )
                meta_of_micro = meta.fit_predict(centroids)
                runs.append(meta_of_micro[micro_labels])

        total_runs = len(runs)

        # Pairwise agreement (ARI between runs)
        ari_matrix = np.zeros((total_runs, total_runs))
        for i in range(total_runs):
            for j in range(i + 1, total_runs):
                a = _inter_run_ari(runs[i], runs[j])
                ari_matrix[i, j] = a
                ari_matrix[j, i] = a

        mean_agreement = ari_matrix.sum(axis=1) / (total_runs - 1)

        # Keep top 60% of runs by agreement
        threshold = np.percentile(mean_agreement, 40)
        good_idx = np.where(mean_agreement >= threshold)[0]

        # Use highest-agreement run as alignment reference
        ref_idx = good_idx[mean_agreement[good_idx].argmax()]
        ref = runs[ref_idx]

        # Align and vote
        aligned: list[np.ndarray] = []
        for r in good_idx:
            if r == ref_idx:
                aligned.append(runs[r])
                continue
            # Build confusion matrix and solve assignment
            conf = np.zeros((self.n_clusters, self.n_clusters), dtype=int)
            for i in range(n_cells):
                conf[ref[i], runs[r][i]] += 1
            _, col_idx = linear_sum_assignment(-conf)
            mapping = np.zeros(self.n_clusters, dtype=int)
            mapping[col_idx] = np.arange(self.n_clusters)
            aligned.append(mapping[runs[r]])

        # Majority vote
        votes = np.zeros((n_cells, self.n_clusters), dtype=np.int32)
        for labels_r in aligned:
            for c in range(self.n_clusters):
                votes[:, c] += (labels_r == c).astype(np.int32)

        return votes.argmax(axis=1)

    def fit_predict(self, X: np.ndarray | pd.DataFrame) -> np.ndarray:
        """Fit and return cluster labels for all cells."""
        self.fit(X)
        return self.labels_

    def _apply_transform(self, X: np.ndarray) -> np.ndarray:
        match self.transform:
            case "arcsinh":
                return np.arcsinh(X / self.cofactor)
            case "log":
                return np.log1p(np.clip(X, 0, None))
            case None:
                return X.copy()
            case _:
                raise ValueError(f"Unknown transform '{self.transform}'. Use 'arcsinh', 'log', or None.")
