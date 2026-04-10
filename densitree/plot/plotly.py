from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import networkx as nx

if TYPE_CHECKING:
    from densitree.result import SPADEResult


def plot_tree(
    result: "SPADEResult",
    color_by: int | str | None = None,
    size_by: str = "count",
):
    """Draw the SPADE MST as an interactive plotly figure.

    Parameters
    ----------
    result : SPADEResult
    color_by : int | str | None
        Feature index or name to color nodes by median expression.
    size_by : str
        ``'count'`` scales node size by cell count; anything else → uniform.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    import plotly.graph_objects as go

    G = result.tree_
    pos = nx.spring_layout(G, seed=42, weight="weight")

    feature_idx = _resolve_feature(color_by, result.feature_names)

    # Edge traces
    edge_x, edge_y = [], []
    for u, v in G.edges:
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="lightgray"),
        hoverinfo="none",
    )

    # Node traces
    node_x = [pos[n][0] for n in G.nodes]
    node_y = [pos[n][1] for n in G.nodes]

    if size_by == "count":
        counts = np.array([G.nodes[n].get("size", 1) for n in G.nodes], dtype=float)
        max_count = counts.max() or 1
        node_sizes = (counts / max_count * 40 + 10).tolist()
    else:
        node_sizes = [20] * G.number_of_nodes()

    if feature_idx is not None:
        node_colors = [G.nodes[n]["median"][feature_idx] for n in G.nodes]
        colorscale = "Viridis"
        label = result.feature_names[feature_idx] if result.feature_names else str(feature_idx)
        colorbar = dict(title=f"Median {label}")
    else:
        node_colors = ["steelblue"] * G.number_of_nodes()
        colorscale = None
        colorbar = None

    hover_text = [
        f"Cluster {n}<br>Size: {G.nodes[n].get('size', '?')}"
        for n in G.nodes
    ]

    marker_kwargs: dict = dict(
        size=node_sizes,
        color=node_colors,
        line=dict(width=1, color="white"),
    )
    if colorscale:
        marker_kwargs["colorscale"] = colorscale
        marker_kwargs["showscale"] = True
        marker_kwargs["colorbar"] = colorbar

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=[str(n) for n in G.nodes],
        textposition="top center",
        hovertext=hover_text,
        hoverinfo="text",
        marker=marker_kwargs,
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="SPADE Tree",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
        ),
    )
    return fig


def _resolve_feature(color_by: int | str | None, feature_names: list[str] | None) -> int | None:
    if color_by is None:
        return None
    if isinstance(color_by, int):
        return color_by
    if feature_names and color_by in feature_names:
        return feature_names.index(color_by)
    raise ValueError(f"Feature '{color_by}' not found in feature_names={feature_names}")
