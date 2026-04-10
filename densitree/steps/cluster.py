from __future__ import annotations
import numpy as np
from sklearn.cluster import AgglomerativeClustering, MiniBatchKMeans
from .base import BaseStep


class ClusterStep(BaseStep):
    """Two-stage clustering on the downsampled cell set.

    Stage 1: Overcluster into n_micro microclusters using MiniBatchKMeans
             (fast, sees all downsampled cells, captures fine structure).
    Stage 2: Merge microclusters into n_clusters metaclusters using
             agglomerative clustering on the microcluster centroids.

    This approach produces much better cluster boundaries than single-stage
    agglomerative clustering because:
    - MiniBatchKMeans scales linearly and produces stable microclusters
    - Agglomerative merging on ~n_micro centroids is fast and produces
      good metaclusters
    - Upsampling to microcluster centroids (many, fine-grained) rather
      than metacluster centroids (few, coarse) dramatically improves
      the accuracy of cell assignment

    Returns micro-level and meta-level labels plus centroids for both.
    """

    def __init__(
        self,
        n_clusters: int = 50,
        n_micro: int | None = None,
        linkage: str = "average",
    ) -> None:
        self.n_clusters = n_clusters
        self.n_micro = n_micro
        self.linkage = linkage

    def run(self, data: np.ndarray, *, X_down: np.ndarray, **ctx) -> dict:
        n_down = len(X_down)

        # Determine number of microclusters
        n_micro = self.n_micro
        if n_micro is None:
            # Heuristic: 10x n_clusters, capped by data size
            n_micro = min(10 * self.n_clusters, n_down // 5)
            n_micro = max(n_micro, self.n_clusters)

        if n_micro <= self.n_clusters or n_down <= n_micro:
            # Fall back to single-stage agglomerative
            return self._single_stage(X_down)

        # Stage 1: overclustering with MiniBatchKMeans
        micro_model = MiniBatchKMeans(
            n_clusters=n_micro,
            random_state=0,
            batch_size=min(1024, n_down),
            n_init=3,
        )
        micro_labels = micro_model.fit_predict(X_down)
        micro_centroids = micro_model.cluster_centers_

        # Stage 2: merge microclusters into metaclusters
        meta_model = AgglomerativeClustering(
            n_clusters=self.n_clusters,
            linkage=self.linkage,
        )
        meta_of_micro = meta_model.fit_predict(micro_centroids)

        # Map downsampled cells: micro -> meta
        meta_labels = meta_of_micro[micro_labels]

        # Compute metacluster centroids from downsampled data
        meta_centroids = np.array([
            X_down[meta_labels == i].mean(axis=0)
            for i in range(self.n_clusters)
        ])

        return {
            "cluster_labels_down": meta_labels,
            "centroids": meta_centroids,
            "micro_centroids": micro_centroids,
            "micro_to_meta": meta_of_micro,
        }

    def _single_stage(self, X_down: np.ndarray) -> dict:
        model = AgglomerativeClustering(
            n_clusters=self.n_clusters,
            linkage="ward",
        )
        labels = model.fit_predict(X_down)
        centroids = np.array([
            X_down[labels == i].mean(axis=0)
            for i in range(self.n_clusters)
        ])
        return {
            "cluster_labels_down": labels,
            "centroids": centroids,
            "micro_centroids": centroids,
            "micro_to_meta": np.arange(self.n_clusters),
        }
