from __future__ import annotations
import numpy as np
from sklearn.neighbors import NearestNeighbors
from .base import BaseStep


class UpsampleStep(BaseStep):
    """Assign every original cell to its nearest cluster.

    Uses microcluster centroids (fine-grained) for assignment, then maps
    each microcluster to its metacluster. This is far more accurate than
    assigning to the few metacluster centroids directly, because
    microclusters capture local structure that coarse centroids miss.
    """

    def run(
        self,
        data: np.ndarray,
        *,
        centroids: np.ndarray,
        micro_centroids: np.ndarray | None = None,
        micro_to_meta: np.ndarray | None = None,
        down_idx: np.ndarray,
        cluster_labels_down: np.ndarray,
        **ctx,
    ) -> dict:
        if micro_centroids is not None and micro_to_meta is not None:
            # Assign each cell to nearest microcluster, then map to metacluster
            nn = NearestNeighbors(n_neighbors=1)
            nn.fit(micro_centroids)
            _, indices = nn.kneighbors(data)
            micro_labels = indices[:, 0]
            labels = micro_to_meta[micro_labels]
        else:
            # Fallback: assign to nearest metacluster centroid
            nn = NearestNeighbors(n_neighbors=1)
            nn.fit(centroids)
            _, indices = nn.kneighbors(data)
            labels = indices[:, 0]

        return {"labels_": labels}
