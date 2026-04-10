"""Generate example plots for documentation."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import networkx as nx
import pandas as pd
from pathlib import Path

from densitree import SPADE

OUT = Path(__file__).parent.parent / "docs" / "assets" / "images"
OUT.mkdir(parents=True, exist_ok=True)


def make_cytometry_like_data():
    """Simulate a cytometry-like dataset with 6 populations including 1 rare."""
    rng = np.random.default_rng(42)
    pops = {
        "T cells": (rng.normal([5, 1, 0, 2, 8], 0.6, (800, 5)), "abundant"),
        "B cells": (rng.normal([1, 6, 0, 7, 1], 0.6, (600, 5)), "abundant"),
        "Monocytes": (rng.normal([0, 0, 7, 5, 0], 0.7, (500, 5)), "abundant"),
        "NK cells": (rng.normal([7, 0, 3, 0, 5], 0.5, (400, 5)), "abundant"),
        "Progenitors": (rng.normal([3, 3, 3, 3, 3], 0.4, (50, 5)), "rare"),
        "pDC": (rng.normal([2, 5, 5, 1, 3], 0.4, (30, 5)), "rare"),
    }
    parts = []
    labels = []
    for name, (data, _) in pops.items():
        parts.append(data)
        labels.extend([name] * len(data))
    X = np.vstack(parts)
    idx = rng.permutation(len(X))
    X = X[idx]
    labels = np.array(labels)[idx]
    markers = ["CD3", "CD19", "CD14", "CD56", "CD8"]
    return pd.DataFrame(X, columns=markers), labels


# ---------- Plot 1: Basic SPADE tree (no coloring) ----------

print("Generating basic tree plot...")
df, true_labels = make_cytometry_like_data()

spade = SPADE(
    n_clusters=15,
    downsample_target=0.1,
    transform=None,
    n_consensus=5,
    random_state=42,
)
spade.fit(df)

fig = spade.result_.plot_tree(color_by=None, size_by="count", backend="matplotlib")
fig.savefig(OUT / "tree_basic.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close("all")
print(f"  Saved {OUT / 'tree_basic.png'}")


# ---------- Plot 2: Tree colored by CD3 ----------

print("Generating CD3-colored tree...")
fig = spade.result_.plot_tree(color_by="CD3", size_by="count", backend="matplotlib")
fig.savefig(OUT / "tree_cd3.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close("all")
print(f"  Saved {OUT / 'tree_cd3.png'}")


# ---------- Plot 3: Tree colored by CD19 ----------

print("Generating CD19-colored tree...")
fig = spade.result_.plot_tree(color_by="CD19", size_by="count", backend="matplotlib")
fig.savefig(OUT / "tree_cd19.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close("all")
print(f"  Saved {OUT / 'tree_cd19.png'}")


# ---------- Plot 4: Interactive plotly tree (saved as HTML) ----------

print("Generating interactive plotly tree...")
fig_plotly = spade.result_.plot_tree(color_by="CD3", size_by="count", backend="plotly")
fig_plotly.write_html(
    str(OUT / "tree_interactive.html"),
    include_plotlyjs="cdn",
    full_html=False,
)
print(f"  Saved {OUT / 'tree_interactive.html'}")


# ---------- Plot 5: Condition comparison ----------

print("Generating condition comparison plot...")
rng = np.random.default_rng(0)

common_a = rng.normal(loc=[0, 0, 5, 3], scale=0.5, size=(1500, 4))
common_b = rng.normal(loc=[4, 4, 1, 6], scale=0.5, size=(1500, 4))
rare_healthy = rng.normal(loc=[2, 8, 2, 2], scale=0.3, size=(20, 4))
rare_disease = rng.normal(loc=[2, 8, 2, 2], scale=0.3, size=(200, 4))

X_healthy = np.vstack([common_a, common_b, rare_healthy])
X_disease = np.vstack([common_a, common_b, rare_disease])
X_combined = np.vstack([X_healthy, X_disease])
condition = np.array(
    ["healthy"] * len(X_healthy) + ["disease"] * len(X_disease)
)

spade_cond = SPADE(n_clusters=10, downsample_target=0.15, transform=None, n_consensus=5, random_state=42)
spade_cond.fit(X_combined)

labels_cond = spade_cond.labels_
tree = spade_cond.result_.tree_
pos = nx.spring_layout(tree, seed=42, weight="weight")

# Compute fold change per cluster
fold_changes = []
for c in range(10):
    mask = labels_cond == c
    n_h = ((condition == "healthy") & mask).sum()
    n_d = ((condition == "disease") & mask).sum()
    frac_h = n_h / (condition == "healthy").sum() if (condition == "healthy").sum() > 0 else 0
    frac_d = n_d / (condition == "disease").sum() if (condition == "disease").sum() > 0 else 0
    if frac_h > 0:
        fc = frac_d / frac_h
    else:
        fc = 10.0
    fold_changes.append(fc)

log_fc = np.log2(np.clip(fold_changes, 0.1, 10))
norm = plt.Normalize(vmin=-2, vmax=2)
colors = [cm.RdBu_r(norm(v)) for v in log_fc]

sizes = [tree.nodes[n].get("size", 1) for n in tree.nodes]
max_size = max(sizes) or 1
node_sizes = [s / max_size * 800 + 100 for s in sizes]

fig, ax = plt.subplots(figsize=(9, 7))
nx.draw_networkx(
    tree, pos=pos, ax=ax,
    node_size=node_sizes,
    node_color=colors,
    edge_color="gray",
    with_labels=True,
    font_size=9,
)
sm = cm.ScalarMappable(cmap=cm.RdBu_r, norm=norm)
sm.set_array([])
fig.colorbar(sm, ax=ax, label="log2(fold change disease / healthy)")
ax.set_title("Condition Comparison: Disease vs Healthy")
ax.axis("off")
fig.savefig(OUT / "condition_comparison.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close("all")
print(f"  Saved {OUT / 'condition_comparison.png'}")


# ---------- Plot 6: Cluster stats heatmap ----------

print("Generating cluster stats heatmap...")
spade_heat = SPADE(n_clusters=12, downsample_target=0.1, transform=None, n_consensus=5, random_state=42)
spade_heat.fit(df)

stats = spade_heat.result_.cluster_stats_
median_cols = [c for c in stats.columns if c.startswith("median_")]
heatmap_data = stats[median_cols].copy()
heatmap_data.columns = [c.replace("median_", "") for c in median_cols]

fig, ax = plt.subplots(figsize=(8, 5))
im = ax.imshow(heatmap_data.values, aspect="auto", cmap="viridis")
ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns, rotation=45, ha="right")
ax.set_yticks(range(len(heatmap_data)))
ax.set_yticklabels([f"Cluster {i}" for i in heatmap_data.index])
ax.set_title("Median Marker Expression per Cluster")
fig.colorbar(im, ax=ax, label="Median expression")
fig.tight_layout()
fig.savefig(OUT / "cluster_heatmap.png", dpi=150, bbox_inches="tight", facecolor="white")
plt.close("all")
print(f"  Saved {OUT / 'cluster_heatmap.png'}")

print("\nDone! All plots saved to docs/assets/images/")
