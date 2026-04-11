from __future__ import annotations
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import networkx as nx


@dataclass
class SPADEResult:
    """Rich output object from a SPADE run.

    Parameters
    ----------
    labels_ : ndarray[int], shape (n_cells,)
        Cluster assignment for every original cell.
    tree_ : networkx.Graph
        MST connecting cluster centroids. Each node has ``size`` (int)
        and ``median`` (ndarray) attributes.
    X_down : ndarray, shape (n_down, n_features)
        Downsampled cells used for clustering.
    down_idx : ndarray[int], shape (n_down,)
        Indices into the original array for the downsampled cells.
    n_features : int
        Number of features in the input data.
    feature_names : list[str] or None
        Feature names. Auto-generated if ``None``.
    """

    labels_: np.ndarray
    tree_: nx.Graph
    X_down: np.ndarray
    down_idx: np.ndarray
    n_features: int
    feature_names: list[str] | None = None
    _cluster_stats: pd.DataFrame | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.feature_names is None:
            self.feature_names = [f"feature_{i}" for i in range(self.n_features)]

    @property
    def cluster_stats_(self) -> pd.DataFrame:
        if self._cluster_stats is None:
            self._cluster_stats = self._build_stats()
        return self._cluster_stats

    def _build_stats(self) -> pd.DataFrame:
        rows = []
        for node in sorted(self.tree_.nodes):
            attrs = self.tree_.nodes[node]
            row: dict = {"cluster": node, "size": attrs.get("size", 0)}
            median = attrs.get("median", np.full(self.n_features, np.nan))
            for fname, val in zip(self.feature_names, median):
                row[f"median_{fname}"] = float(val)
            rows.append(row)
        return pd.DataFrame(rows).set_index("cluster")

    def plot_tree(
        self,
        color_by: int | str | None = None,
        size_by: str = "count",
        backend: str = "matplotlib",
    ):
        """Visualize the SPADE tree.

        Parameters
        ----------
        color_by:
            Feature index (int) or name (str) to color nodes by median expression.
            ``None`` colors all nodes the same.
        size_by:
            ``'count'`` scales node size by cell count. Any other value uses uniform size.
        backend:
            ``'matplotlib'`` for static plots, ``'plotly'`` for interactive.
        """
        if backend == "matplotlib":
            from densitree.plot.matplotlib import plot_tree as _plot
        elif backend == "plotly":
            try:
                from densitree.plot.plotly import plot_tree as _plot
            except ImportError as e:
                raise ImportError(
                    "plotly is required for backend='plotly'. "
                    "Install it with: pip install plotly"
                ) from e
        else:
            raise ValueError(f"Unknown backend '{backend}'. Use 'matplotlib' or 'plotly'.")

        return _plot(self, color_by=color_by, size_by=size_by)
