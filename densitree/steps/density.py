from __future__ import annotations
import numpy as np
from sklearn.neighbors import NearestNeighbors
from .base import BaseStep


class DensityEstimator(BaseStep):
    """Estimate local density for each cell using k-NN.

    Density is defined as 1 / (distance to k-th nearest neighbor + eps),
    so cells in dense regions get high density values.
    """

    def __init__(self, knn: int = 5, eps: float = 1e-8) -> None:
        self.knn = knn
        self.eps = eps

    def run(self, data: np.ndarray, **ctx) -> dict:
        nn = NearestNeighbors(n_neighbors=self.knn + 1)  # +1 because cell is its own neighbor
        nn.fit(data)
        distances, _ = nn.kneighbors(data)
        kth_dist = distances[:, self.knn]  # distance to k-th neighbor (excluding self)
        density = 1.0 / (kth_dist + self.eps)
        return {"density": density}
