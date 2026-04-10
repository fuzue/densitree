from __future__ import annotations
import numpy as np
import networkx as nx
from scipy.spatial.distance import cdist
from scipy.sparse.csgraph import minimum_spanning_tree
from scipy.sparse import csr_matrix
from .base import BaseStep


class MSTBuilder(BaseStep):
    """Build a minimum spanning tree connecting cluster centroids.

    Each node in the resulting networkx.Graph represents one cluster.
    Node attributes:
    - ``size``: number of cells assigned to that cluster
    - ``median``: per-feature median of cells in that cluster (ndarray)

    Edge weights are Euclidean distances between centroids.
    """

    def run(
        self,
        data: np.ndarray,
        *,
        centroids: np.ndarray,
        labels_: np.ndarray,
        **ctx,
    ) -> dict:
        n_clusters = len(centroids)

        # Pairwise distances between centroids
        dist_matrix = cdist(centroids, centroids, metric="euclidean")

        # Compute MST on the full distance graph
        sparse = csr_matrix(dist_matrix)
        mst_sparse = minimum_spanning_tree(sparse)
        mst_array = mst_sparse.toarray()

        # Build networkx graph
        G = nx.Graph()
        G.add_nodes_from(range(n_clusters))

        for i in range(n_clusters):
            for j in range(i + 1, n_clusters):
                w = mst_array[i, j] or mst_array[j, i]
                if w > 0:
                    G.add_edge(i, j, weight=float(w))

        # Add node attributes
        for cluster_id in range(n_clusters):
            mask = labels_ == cluster_id
            G.nodes[cluster_id]["size"] = int(mask.sum())
            if mask.sum() > 0 and data is not None:
                G.nodes[cluster_id]["median"] = np.median(data[mask], axis=0)
            else:
                G.nodes[cluster_id]["median"] = centroids[cluster_id]

        return {"tree_": G}
