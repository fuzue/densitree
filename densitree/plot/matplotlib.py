from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm

if TYPE_CHECKING:
    from densitree.result import SPADEResult


def plot_tree(
    result: "SPADEResult",
    color_by: int | str | None = None,
    size_by: str = "count",
) -> plt.Figure:
    """Draw the SPADE MST as a static matplotlib figure.

    Parameters
    ----------
    result : SPADEResult
    color_by : int | str | None
        Feature index or name to color nodes by median expression.
    size_by : str
        ``'count'`` scales node area by cell count; anything else → uniform.

    Returns
    -------
    matplotlib.figure.Figure
    """
    G = result.tree_
    pos = nx.spring_layout(G, seed=42, weight="weight")

    # Node sizes
    if size_by == "count":
        sizes = np.array([G.nodes[n].get("size", 1) for n in G.nodes])
        max_size = sizes.max() or 1
        node_sizes = (sizes / max_size * 800 + 100).tolist()
    else:
        node_sizes = [300] * G.number_of_nodes()

    # Node colors
    feature_idx = _resolve_feature(color_by, result.feature_names)
    if feature_idx is not None:
        values = np.array([
            G.nodes[n]["median"][feature_idx]
            for n in G.nodes
        ])
        norm = plt.Normalize(vmin=values.min(), vmax=values.max())
        node_colors = [cm.viridis(norm(v)) for v in values]
    else:
        node_colors = ["steelblue"] * G.number_of_nodes()

    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw_networkx(
        G, pos=pos, ax=ax,
        node_size=node_sizes,
        node_color=node_colors,
        edge_color="gray",
        with_labels=True,
        font_size=8,
    )

    if feature_idx is not None:
        sm = cm.ScalarMappable(cmap=cm.viridis, norm=norm)
        sm.set_array([])
        label = result.feature_names[feature_idx] if result.feature_names else str(feature_idx)
        fig.colorbar(sm, ax=ax, label=f"Median {label}")

    ax.set_title("SPADE Tree")
    ax.axis("off")
    return fig


def _resolve_feature(color_by: int | str | None, feature_names: list[str] | None) -> int | None:
    if color_by is None:
        return None
    if isinstance(color_by, int):
        return color_by
    if feature_names and color_by in feature_names:
        return feature_names.index(color_by)
    raise ValueError(f"Feature '{color_by}' not found in feature_names={feature_names}")
