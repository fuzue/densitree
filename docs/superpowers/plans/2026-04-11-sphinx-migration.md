# Sphinx Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate densitree documentation from MkDocs Material to Sphinx with PyData theme, hosting on GitHub Pages at densitree.fuzue.tech.

**Architecture:** Replace `mkdocs.yml` and all `.md` docs with a `conf.py` + `.rst` Sphinx setup. Use `sphinx.ext.autodoc` + `sphinx.ext.napoleon` for API reference (NumPy-style docstrings). Deploy via `sphinx-build` → `peaceiris/actions-gh-pages` in CI.

**Tech Stack:** Sphinx ≥7.0, pydata-sphinx-theme ≥0.15, sphinx-copybutton ≥0.5, sphinx.ext.autodoc, sphinx.ext.napoleon, sphinx.ext.intersphinx, sphinx.ext.mathjax, sphinx.ext.viewcode.

---

### Task 1: Sphinx scaffold — conf.py, _templates, _static

**Files:**
- Create: `docs/conf.py`
- Create: `docs/_templates/layout.html`
- Create: `docs/_static/.gitkeep`

- [ ] **Step 1: Install docs dependencies for local testing**

```bash
cd /home/aivuk/densitree
uv sync --extra docs
```

Expected: installs current mkdocs deps. We will update pyproject.toml later; for now install sphinx manually into the venv so we can test:

```bash
uv pip install "sphinx>=7.0" "pydata-sphinx-theme>=0.15" "sphinx-copybutton>=0.5"
```

- [ ] **Step 2: Create `docs/conf.py`**

```python
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'densitree'
copyright = '2025, Edgar Zanella Alvarenga'
author = 'Edgar Zanella Alvarenga'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
    'sphinx_copybutton',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'superpowers']

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_extra_path = ['CNAME']

html_theme_options = {
    "github_url": "https://github.com/fuzue/densitree",
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/densitree/",
            "icon": "fa-brands fa-python",
        },
    ],
    "og_image": "https://densitree.fuzue.tech/assets/images/social-card.png",
    "show_toc_level": 2,
    "navigation_with_keys": True,
}

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_param = False
napoleon_use_rtype = False

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable', None),
    'scipy': ('https://docs.scipy.org/doc/scipy', None),
    'sklearn': ('https://scikit-learn.org/stable', None),
    'pandas': ('https://pandas.pydata.org/docs', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'networkx': ('https://networkx.org/documentation/stable', None),
}

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
```

- [ ] **Step 3: Create `docs/_templates/layout.html`** (Open Graph + Twitter meta tags)

```html
{% extends "pydata_sphinx_theme/layout.html" %}

{% block extrahead %}
{{ super() }}
<meta property="og:type" content="website">
<meta property="og:title" content="{{ docstitle }} — densitree">
<meta property="og:description" content="Density-normalized clustering with spanning tree construction for high-dimensional data. State-of-the-art SPADE implementation in Python.">
<meta property="og:image" content="https://densitree.fuzue.tech/assets/images/social-card.png">
<meta property="og:site_name" content="densitree">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://densitree.fuzue.tech/assets/images/social-card.png">
<meta name="author" content="Fuzue Tech">
{% endblock %}
```

- [ ] **Step 4: Create `docs/_static/.gitkeep`**

Create an empty file at `docs/_static/.gitkeep` so the directory is tracked by git.

- [ ] **Step 5: Commit**

```bash
git add docs/conf.py docs/_templates/layout.html docs/_static/.gitkeep
git commit -m "docs: add Sphinx conf.py and theme templates"
```

---

### Task 2: Root index and getting-started pages

**Files:**
- Create: `docs/index.rst`
- Create: `docs/getting-started/installation.rst`
- Create: `docs/getting-started/quickstart.rst`

- [ ] **Step 1: Create `docs/index.rst`**

```rst
densitree
=========

**A reference Python implementation of the SPADE algorithm for high-dimensional cytometry and single-cell data.**

SPADE (Spanning-tree Progression Analysis of Density-normalized Events) extracts cellular hierarchies from
high-dimensional single-cell data by combining density-dependent downsampling, agglomerative clustering,
and minimum spanning tree construction.

----

Why densitree?
--------------

- **scikit-learn compatible** — ``fit()`` / ``fit_predict()`` API, works with numpy arrays and pandas DataFrames
- **Extensible pipeline** — swap any step (density estimation, clustering, etc.) via the ``BaseStep`` interface
- **Dual visualization** — static matplotlib and interactive plotly backends
- **Reproducible** — deterministic results with ``random_state`` parameter
- **Well-tested** — comprehensive unit and integration test suite
- **Pure Python** — no R or MATLAB dependency

Quick Example
-------------

.. code-block:: python

   import numpy as np
   from densitree import SPADE

   X = np.random.default_rng(0).normal(size=(1000, 10))

   spade = SPADE(n_clusters=20, downsample_target=0.1, random_state=42)
   spade.fit(X)

   # Cluster labels for all 1000 cells
   print(spade.labels_)

   # Per-cluster statistics
   print(spade.result_.cluster_stats_)

   # Visualize the SPADE tree
   spade.result_.plot_tree(color_by=0, backend="matplotlib")

Example outputs
---------------

Tree colored by marker expression
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nodes are sized by cell count. Color shows median CD3 expression — high (yellow) in T cell clusters, low (purple) elsewhere.

.. image:: assets/images/tree_cd3.png
   :alt: SPADE tree colored by CD3

Condition comparison
~~~~~~~~~~~~~~~~~~~~

Red nodes are enriched in the disease condition, blue in healthy. Cluster 5 (dark red) contains a rare population expanded in disease.

.. image:: assets/images/condition_comparison.png
   :alt: Condition comparison

Cluster heatmap
~~~~~~~~~~~~~~~

Median marker expression per cluster reveals distinct cell populations.

.. image:: assets/images/cluster_heatmap.png
   :alt: Cluster heatmap

Interactive visualization
~~~~~~~~~~~~~~~~~~~~~~~~~

densitree also supports interactive plotly trees — hover for cluster details, zoom and pan.

.. raw:: html

   <iframe src="_images/tree_interactive.html" width="100%" height="500" frameborder="0"></iframe>

Installation
------------

.. code-block:: bash

   pip install densitree

Or from source:

.. code-block:: bash

   git clone https://github.com/fuzue/densitree.git
   cd densitree
   pip install -e ".[dev]"

----

.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   getting-started/installation
   getting-started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :hidden:

   guide

.. toctree::
   :maxdepth: 2
   :caption: Tutorials
   :hidden:

   tutorials/flow_cytometry
   tutorials/comparing_conditions

.. toctree::
   :maxdepth: 2
   :caption: API Reference
   :hidden:

   api/spade
   api/result
   api/steps
   api/plotting

.. toctree::
   :maxdepth: 2
   :caption: Benchmarks
   :hidden:

   benchmarks/overview
   benchmarks/datasets
   benchmarks/results
   benchmarks/comparison

.. toctree::
   :maxdepth: 2
   :caption: Method
   :hidden:

   method/algorithm
   method/improvements
   method/references
```

Note on the interactive HTML: MkDocs served `assets/images/` directly. In Sphinx, static files go through `html_static_path` or `html_extra_path`. Add `"assets"` to `html_extra_path` in `conf.py` so the images directory is copied as-is. Update `conf.py`:

```python
html_extra_path = ['CNAME', 'assets']
```

Then iframe paths use `_extra/assets/images/tree_interactive.html`... actually it's simpler to add `assets/images` to `html_static_path`. However since `_static` is the output path that would put them at `_static/`. The cleanest approach: add `assets` to `html_extra_path` so the directory is copied to the root of the output, same as before. The iframe path in RST becomes just `assets/images/tree_interactive.html`. Update the index.rst iframe src accordingly:

```html
<iframe src="assets/images/tree_interactive.html" width="100%" height="500" frameborder="0"></iframe>
```

And update `conf.py` line:
```python
html_extra_path = ['CNAME', 'assets']
```

- [ ] **Step 2: Create `docs/getting-started/installation.rst`**

```rst
Installation
============

From PyPI
---------

.. code-block:: bash

   pip install densitree

From source (development)
--------------------------

.. code-block:: bash

   git clone https://github.com/fuzue/densitree.git
   cd densitree
   pip install -e ".[dev]"

Dependencies
------------

densitree requires Python 3.10+ and the following packages (installed automatically):

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Package
     - Minimum version
     - Purpose
   * - numpy
     - 1.24
     - Array operations
   * - scipy
     - 1.10
     - MST computation, distance metrics
   * - scikit-learn
     - 1.3
     - k-NN, agglomerative clustering
   * - networkx
     - 3.0
     - Tree data structure
   * - matplotlib
     - 3.7
     - Static visualization
   * - plotly
     - 5.15
     - Interactive visualization
   * - pandas
     - 2.0
     - DataFrame support, cluster statistics

Optional dependencies
~~~~~~~~~~~~~~~~~~~~~

For running benchmarks:

.. code-block:: bash

   pip install densitree[bench]

This adds ``flowio`` (FCS file reading), ``leidenalg`` and ``igraph`` (PhenoGraph-style clustering for comparisons).

For building documentation:

.. code-block:: bash

   pip install densitree[docs]
```

- [ ] **Step 3: Create `docs/getting-started/quickstart.rst`**

```rst
Quick Start
===========

Basic usage
-----------

.. code-block:: python

   from densitree import SPADE

   # X is any (n_cells, n_features) array
   spade = SPADE(n_clusters=30, downsample_target=0.1, random_state=42)
   labels = spade.fit_predict(X)

With a pandas DataFrame
-----------------------

Column names are automatically preserved in the result:

.. code-block:: python

   import pandas as pd
   from densitree import SPADE

   df = pd.read_csv("cytometry_data.csv")
   markers = ["CD3", "CD4", "CD8", "CD19", "CD56"]

   spade = SPADE(n_clusters=30, downsample_target=0.1, random_state=42)
   spade.fit(df[markers])

   # Cluster stats include median_CD3, median_CD4, etc.
   print(spade.result_.cluster_stats_)

Visualization
-------------

.. code-block:: python

   # Static matplotlib plot
   fig = spade.result_.plot_tree(color_by="CD3", backend="matplotlib")
   fig.savefig("tree.png", dpi=150)

   # Interactive plotly plot
   fig = spade.result_.plot_tree(color_by="CD3", backend="plotly")
   fig.show()

.. image:: ../assets/images/tree_cd3.png
   :alt: Example SPADE tree

Choosing parameters
-------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Parameter
     - Default
     - Guidance
   * - ``n_clusters``
     - 50
     - 20--100 depending on expected complexity. More clusters = finer resolution but noisier tree.
   * - ``downsample_target``
     - 0.05
     - Fraction of cells retained. Lower = faster but may lose structure. 0.05--0.2 typical.
   * - ``knn``
     - 5
     - Neighborhood size for density estimation. 5--10 for most datasets.
   * - ``transform``
     - ``"arcsinh"``
     - Use ``"arcsinh"`` for cytometry (cofactor=5 for CyTOF, 150 for flow), ``"log"`` for counts, ``None`` if pre-transformed.
   * - ``cofactor``
     - 150.0
     - Arcsinh denominator. 5.0 for CyTOF, 150.0 for fluorescence.
```

- [ ] **Step 4: Verify partial build**

```bash
cd /home/aivuk/densitree
uv run sphinx-build -b html docs/ _build/html 2>&1 | grep -E "^(ERROR|SEVERE)"
```

Expected: errors about missing RST files referenced in toctrees. No Python errors or theme errors.

- [ ] **Step 5: Commit**

```bash
git add docs/index.rst docs/getting-started/installation.rst docs/getting-started/quickstart.rst
git commit -m "docs: add Sphinx index and getting-started pages"
```

---

### Task 3: User guide

**Files:**
- Create: `docs/guide.rst`

- [ ] **Step 1: Create `docs/guide.rst`**

```rst
densitree User Guide
====================

A Python implementation of the **SPADE** (Spanning-tree Progression Analysis of Density-normalized Events)
algorithm for high-dimensional cytometry and single-cell data analysis.

----

Installation
------------

.. code-block:: bash

   pip install -e ".[dev]"

Dependencies: numpy, scipy, scikit-learn, networkx, matplotlib, plotly, pandas.

----

Quick Start
-----------

.. code-block:: python

   import numpy as np
   from densitree import SPADE

   # Generate synthetic data: 1000 cells, 5 markers
   rng = np.random.default_rng(42)
   X = np.vstack([
       rng.normal(loc=[0, 0, 5, 3, 1], scale=0.5, size=(300, 5)),
       rng.normal(loc=[4, 4, 1, 1, 6], scale=0.5, size=(400, 5)),
       rng.normal(loc=[8, 2, 3, 7, 2], scale=0.5, size=(300, 5)),
   ])

   spade = SPADE(n_clusters=10, downsample_target=0.2, random_state=0)
   spade.fit(X)

   print(spade.labels_[:20])              # cluster labels for every cell
   print(spade.result_.cluster_stats_)    # per-cluster summary table

   spade.result_.plot_tree(color_by=0, backend="matplotlib")

----

Core Concepts
-------------

SPADE works in five sequential steps:

1. **Density estimation** — For each cell, compute local density via k-nearest-neighbor distances. Cells in crowded regions get high density scores.

2. **Density-dependent downsampling** — Cells in dense regions are sampled with lower probability, while rare populations are preserved. This prevents abundant cell types from dominating the clustering.

3. **Agglomerative clustering** — The downsampled cells are clustered into ``n_clusters`` groups using Ward's linkage hierarchical clustering.

4. **Upsampling** — Every original cell (not just the downsampled ones) is assigned to the cluster whose centroid is nearest.

5. **Minimum spanning tree (MST)** — Cluster centroids are connected into a tree where edge weights are Euclidean distances. This tree captures the progression/hierarchy structure of the data.

Data transforms
~~~~~~~~~~~~~~~

Before any step runs, an optional transform is applied to all features:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - ``transform``
     - Formula
     - Typical use
   * - ``"arcsinh"`` (default)
     - ``arcsinh(x / cofactor)``
     - CyTOF data (cofactor=5) or flow cytometry (cofactor=150)
   * - ``"log"``
     - ``log(1 + x)``
     - Count data, scRNA-seq
   * - ``None``
     - Identity
     - Already-transformed data

----

API Reference
-------------

SPADE
~~~~~

.. code-block:: python

   SPADE(
       n_clusters=50,          # number of clusters in the tree
       downsample_target=0.05, # fraction of cells to retain
       knn=5,                  # k for density estimation
       transform="arcsinh",    # "arcsinh", "log", or None
       cofactor=150.0,         # arcsinh cofactor
       random_state=None,      # seed for reproducibility
   )

**Methods:**

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Method
     - Returns
     - Description
   * - ``fit(X)``
     - ``self``
     - Run the full SPADE pipeline
   * - ``fit_predict(X)``
     - ``ndarray``
     - Run pipeline and return cluster labels

**Attributes (after** ``fit`` **):**

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Attribute
     - Type
     - Description
   * - ``labels_``
     - ``ndarray[int]``
     - Cluster assignment for every cell
   * - ``result_``
     - ``SPADEResult``
     - Rich output object (see below)

Input ``X`` can be a numpy array or a pandas DataFrame. If a DataFrame is passed, column names are preserved in the result.

SPADEResult
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Attribute
     - Type
     - Description
   * - ``labels_``
     - ``ndarray[int]``
     - Cluster labels (same as ``SPADE.labels_``)
   * - ``tree_``
     - ``networkx.Graph``
     - MST with node attributes ``size`` and ``median``
   * - ``X_down``
     - ``ndarray``
     - Downsampled cell matrix
   * - ``down_idx``
     - ``ndarray[int]``
     - Indices of downsampled cells in the original array
   * - ``cluster_stats_``
     - ``pd.DataFrame``
     - One row per cluster: ``size``, ``median_<feature>`` columns

**Methods:**

.. code-block:: python

   result.plot_tree(
       color_by=None,          # feature index (int) or name (str) to color nodes
       size_by="count",        # "count" scales nodes by cell count
       backend="matplotlib",   # "matplotlib" or "plotly"
   )

BaseStep
~~~~~~~~

Abstract base class for pipeline steps. Subclass it to create custom steps:

.. code-block:: python

   from densitree import BaseStep
   import numpy as np

   class MyDensityEstimator(BaseStep):
       def run(self, data: np.ndarray, **ctx) -> dict:
           # your custom density logic
           return {"density": my_density_values}

   spade = SPADE(density_estimator=MyDensityEstimator())

----

Examples
--------

Example 1: Basic flow cytometry analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from densitree import SPADE

   # Load a CSV exported from FlowJo or similar
   df = pd.read_csv("flow_data.csv")
   markers = ["CD3", "CD4", "CD8", "CD19", "CD56"]
   X = df[markers]

   spade = SPADE(
       n_clusters=30,
       downsample_target=0.1,
       transform="arcsinh",
       cofactor=150.0,    # standard for fluorescence flow cytometry
       random_state=42,
   )
   spade.fit(X)

   # Explore clusters
   print(spade.result_.cluster_stats_)

   # Color tree by CD4 expression
   fig = spade.result_.plot_tree(color_by="CD4", backend="matplotlib")
   fig.savefig("spade_tree_cd4.png", dpi=150, bbox_inches="tight")

Example 2: CyTOF / mass cytometry data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from densitree import SPADE

   # CyTOF uses cofactor=5 for arcsinh transform
   spade = SPADE(
       n_clusters=50,
       downsample_target=0.05,
       transform="arcsinh",
       cofactor=5.0,
       random_state=0,
   )
   spade.fit(X_cytof)  # numpy array, shape (n_cells, n_markers)

   # Interactive plotly visualization
   fig = spade.result_.plot_tree(color_by=0, backend="plotly")
   fig.show()

Example 3: Comparing conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import numpy as np
   from densitree import SPADE

   # Fit on combined data from two conditions
   X_combined = np.vstack([X_healthy, X_disease])
   condition = np.array(
       ["healthy"] * len(X_healthy) + ["disease"] * len(X_disease)
   )

   spade = SPADE(n_clusters=20, downsample_target=0.1, random_state=0)
   spade.fit(X_combined)

   # Count cells per cluster per condition
   labels = spade.labels_
   for cluster_id in range(20):
       mask = labels == cluster_id
       n_healthy = (condition[mask] == "healthy").sum()
       n_disease = (condition[mask] == "disease").sum()
       print(f"Cluster {cluster_id}: healthy={n_healthy}, disease={n_disease}")

Example 4: Working with the tree directly (networkx)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import networkx as nx
   from densitree import SPADE

   spade = SPADE(n_clusters=15, downsample_target=0.1, random_state=0)
   spade.fit(X)

   tree = spade.result_.tree_

   # Find the two most connected clusters (highest degree)
   degrees = sorted(tree.degree, key=lambda x: x[1], reverse=True)
   print(f"Hub clusters: {degrees[:3]}")

   # Shortest path between two clusters
   path = nx.shortest_path(tree, source=0, target=10, weight="weight")
   print(f"Path from cluster 0 to 10: {path}")

   # Export tree for use in other tools
   nx.write_graphml(tree, "spade_tree.graphml")

Example 5: Custom density estimator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import numpy as np
   from densitree import SPADE, BaseStep

   class KDEDensityEstimator(BaseStep):
       """Use scipy KDE instead of k-NN for density estimation."""

       def __init__(self, bandwidth: float = 1.0):
           self.bandwidth = bandwidth

       def run(self, data: np.ndarray, **ctx) -> dict:
           from scipy.stats import gaussian_kde
           kde = gaussian_kde(data.T, bw_method=self.bandwidth)
           density = kde(data.T)
           return {"density": density}

   spade = SPADE(
       n_clusters=10,
       downsample_target=0.1,
       density_estimator=KDEDensityEstimator(bandwidth=0.5),
       random_state=0,
   )
   spade.fit(X)

Example 6: Exporting results to a DataFrame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from densitree import SPADE

   spade = SPADE(n_clusters=20, downsample_target=0.1, random_state=0)
   spade.fit(X)

   # Add cluster labels back to original data
   df_annotated = pd.DataFrame(X, columns=marker_names)
   df_annotated["spade_cluster"] = spade.labels_
   df_annotated.to_csv("annotated_cells.csv", index=False)

   # Export cluster statistics
   spade.result_.cluster_stats_.to_csv("cluster_stats.csv")

----

Method Background & Literature
--------------------------------

The SPADE algorithm
~~~~~~~~~~~~~~~~~~~~

SPADE was introduced to address a fundamental challenge in cytometry: how to organize high-dimensional
single-cell data into an interpretable hierarchy that reflects biological structure (e.g., hematopoietic
differentiation).

The key insight is **density-dependent downsampling**. Traditional clustering on cytometry data is dominated
by abundant cell types (e.g., mature lymphocytes), causing rare populations (e.g., progenitors, transitional
cells) to be absorbed into larger clusters. By downsampling proportionally to the inverse of local density,
SPADE ensures rare populations are represented in the clustering step.

After clustering the downsampled cells, a **minimum spanning tree** is constructed over the cluster centroids.
This tree naturally captures gradual transitions between cell phenotypes — branches in the tree correspond
to differentiation trajectories.

Key references
~~~~~~~~~~~~~~

1. **Qiu, P., Simonds, E.F., Bendall, S.C., et al.** (2011). "Extracting a cellular hierarchy from
   high-dimensional cytometry data with SPADE." *Nature Biotechnology*, 29(10), 886-891.
   `doi:10.1038/nbt.1991 <https://doi.org/10.1038/nbt.1991>`_

2. **Bendall, S.C., Simonds, E.F., Qiu, P., et al.** (2011). "Single-cell mass cytometry of differential
   immune and drug responses across a human hematopoietic continuum." *Science*, 332(6030), 687-696.
   `doi:10.1126/science.1198704 <https://doi.org/10.1126/science.1198704>`_

3. **Qiu, P.** (2017). "Toward deterministic and semiautomated SPADE analysis." *Cytometry Part A*,
   91(7), 714-727. `doi:10.1002/cyto.a.23068 <https://doi.org/10.1002/cyto.a.23068>`_

4. **Samusik, N., Good, Z., Spitzer, M.H., Davis, K.L., & Nolan, G.P.** (2016). "Automated mapping of
   phenotype space with single-cell data." *Nature Methods*, 13(6), 493-496.
   `doi:10.1038/nmeth.3863 <https://doi.org/10.1038/nmeth.3863>`_

5. **Levine, J.H., Simonds, E.F., Bendall, S.C., et al.** (2015). "Data-Driven Phenotypic Dissection of
   AML Reveals Progenitor-like Cells that Correlate with Prognosis." *Cell*, 162(1), 184-197.
   `doi:10.1016/j.cell.2015.05.047 <https://doi.org/10.1016/j.cell.2015.05.047>`_

----

Comparison with Other Tools
----------------------------

SPADE implementations
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Feature
     - **densitree**
     - **R spade** (Bioconductor)
     - **Cytobank**
     - **FlowJo plugin**
   * - Language
     - Python
     - R / C++
     - Cloud (web UI)
     - Java (desktop)
   * - Input formats
     - numpy, pandas
     - FCS files
     - FCS upload
     - FCS via FlowJo
   * - scikit-learn compatible
     - Yes
     - No
     - No
     - No
   * - Custom steps / extensible
     - Yes (BaseStep ABC)
     - Limited
     - No
     - No
   * - Interactive visualization
     - plotly
     - No (static only)
     - Yes (built-in)
     - Yes (built-in)
   * - FCS file parsing
     - No (bring your own)
     - Yes (built-in)
     - Yes
     - Yes
   * - Maintained
     - Active
     - Archived
     - Active
     - Active
   * - Cost
     - Free / open source
     - Free / open source
     - Commercial subscription
     - Commercial license
   * - Reproducibility (seed)
     - Yes
     - Partial (improved in spade2)
     - Limited
     - Limited

densitree vs. R spade (Bioconductor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The original R implementation (``spade``, now archived) was the reference. It includes FCS parsing,
C++-accelerated density estimation, and direct integration with the Bioconductor/flowCore ecosystem.
**densitree** trades FCS parsing for Python ecosystem integration: it works natively with numpy arrays,
pandas DataFrames, and scikit-learn conventions (``fit``/``fit_predict``). If you're already working in
Python (e.g., with scanpy, anndata, or general ML pipelines), densitree avoids the R interop overhead.

densitree vs. Cytobank / FlowJo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cytobank and FlowJo offer SPADE as part of larger GUI-driven analysis platforms. They are ideal for bench
scientists who want point-and-click workflows with built-in gating, compensation, and visualization.
**densitree** is for programmatic use: batch processing, reproducible pipelines, parameter sweeps, and
integration with custom downstream analysis. You trade the GUI for full scripting control.

SPADE vs. other single-cell clustering methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Method
     - Key idea
     - Output
     - Best for
   * - **SPADE**
     - Density-normalized downsampling + MST
     - Tree of clusters
     - Hierarchy/trajectory visualization, rare population preservation
   * - **FlowSOM**
     - Self-organizing maps + consensus clustering
     - Grid/tree of clusters
     - Fast, scalable, good default for most panels
   * - **PhenoGraph**
     - k-NN graph + Louvain community detection
     - Flat clusters
     - Discovering phenotypically distinct populations
   * - **UMAP + Leiden**
     - Dimension reduction + graph clustering
     - Flat clusters + 2D embedding
     - Exploratory visualization, scRNA-seq

**When to use SPADE over alternatives:**

- You care about **tree structure** — SPADE's MST explicitly models gradual transitions between cell types, which is valuable for differentiation studies.
- You need to **preserve rare populations** — the density-dependent downsampling is SPADE's signature feature.
- You want an **interpretable number of clusters** — SPADE's ``n_clusters`` parameter gives direct control, unlike graph-based methods where cluster count emerges from resolution parameters.

**When to consider alternatives:**

- For very large datasets (>1M cells), FlowSOM is typically faster.
- If you don't need tree structure and just want the best cluster assignments, PhenoGraph or Leiden clustering may give better separation.
- For scRNA-seq data, the scanpy/Leiden ecosystem is more mature and better integrated with downstream tools (DEG analysis, trajectory inference with PAGA, etc.).
```

- [ ] **Step 2: Verify partial build**

```bash
uv run sphinx-build -b html docs/ _build/html 2>&1 | grep -E "^(ERROR|SEVERE)"
```

Expected: errors about remaining missing RST files in toctrees only.

- [ ] **Step 3: Commit**

```bash
git add docs/guide.rst
git commit -m "docs: add guide.rst"
```

---

### Task 4: Tutorials

**Files:**
- Create: `docs/tutorials/flow_cytometry.rst`
- Create: `docs/tutorials/comparing_conditions.rst`

- [ ] **Step 1: Create `docs/tutorials/flow_cytometry.rst`**

```rst
Tutorial: Flow Cytometry Analysis with densitree
=================================================

This tutorial walks through a complete SPADE analysis of CyTOF data using the Levine_32dim benchmark dataset.

Setup
-----

.. code-block:: python

   import numpy as np
   import pandas as pd
   import matplotlib
   matplotlib.use("Agg")  # use interactive backend if in a notebook
   import matplotlib.pyplot as plt
   from densitree import SPADE

Load data
---------

densitree works with numpy arrays or pandas DataFrames. Here we load the Levine_32dim benchmark dataset:

.. code-block:: python

   # If you have readfcs installed:
   import readfcs
   adata = readfcs.read("Levine_32dim.fcs")
   df = adata.to_df()

   # Select marker columns (exclude metadata like Time, DNA, etc.)
   markers = [c for c in df.columns if c.startswith("CD") or c == "HLA-DR" or c == "Flt3"]
   X = df[markers]
   print(f"Data: {X.shape[0]} cells, {X.shape[1]} markers")

Run SPADE
---------

For CyTOF data, use arcsinh transform with cofactor 5:

.. code-block:: python

   spade = SPADE(
       n_clusters=50,           # overcluster for tree exploration
       downsample_target=0.1,   # retain 10% of cells
       knn=10,                  # k for density estimation
       transform="arcsinh",
       cofactor=5.0,            # CyTOF standard
       random_state=42,
   )
   spade.fit(X)

   print(f"Clusters: {len(np.unique(spade.labels_))}")
   print(f"Tree nodes: {spade.result_.tree_.number_of_nodes()}")
   print(f"Tree edges: {spade.result_.tree_.number_of_edges()}")

Explore results
---------------

Cluster statistics
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   stats = spade.result_.cluster_stats_
   print(stats.head(10))

   # Find the largest and smallest clusters
   print("\nLargest clusters:")
   print(stats.nlargest(5, "size")[["size"]])

   print("\nSmallest clusters (potential rare populations):")
   print(stats.nsmallest(5, "size")[["size"]])

Visualize the tree
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Color by CD3 expression
   fig = spade.result_.plot_tree(color_by="CD3", size_by="count", backend="matplotlib")
   fig.savefig("spade_tree_cd3.png", dpi=150, bbox_inches="tight")

.. image:: ../assets/images/tree_cd3.png
   :alt: Tree colored by CD3

.. code-block:: python

   # Color by CD19 (B cell marker)
   fig = spade.result_.plot_tree(color_by="CD19", size_by="count", backend="matplotlib")
   fig.savefig("spade_tree_cd19.png", dpi=150, bbox_inches="tight")

.. image:: ../assets/images/tree_cd19.png
   :alt: Tree colored by CD19

Interactive exploration with plotly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   fig = spade.result_.plot_tree(color_by="CD3", backend="plotly")
   fig.write_html("spade_tree_interactive.html")
   # or fig.show() in a notebook

.. raw:: html

   <iframe src="../assets/images/tree_interactive.html" width="100%" height="500" frameborder="0"></iframe>

Work with the tree directly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import networkx as nx

   tree = spade.result_.tree_

   # Find hub clusters (high degree = many connections)
   degrees = sorted(tree.degree, key=lambda x: x[1], reverse=True)
   print("Hub clusters:", degrees[:5])

   # Find clusters connected to a specific node
   neighbors = list(tree.neighbors(0))
   print(f"Cluster 0 is connected to: {neighbors}")

   # Get the path between two clusters (differentiation trajectory?)
   path = nx.shortest_path(tree, source=0, target=25, weight="weight")
   print(f"Path: {path}")
   print("Markers along path:")
   for node in path:
       median = tree.nodes[node]["median"]
       print(f"  Cluster {node}: size={tree.nodes[node]['size']}")

Export results
--------------

.. code-block:: python

   # Add cluster labels to original data
   df_out = X.copy()
   df_out["spade_cluster"] = spade.labels_
   df_out.to_csv("annotated_cells.csv", index=False)

   # Export cluster statistics
   spade.result_.cluster_stats_.to_csv("cluster_stats.csv")

   # Export tree for external tools
   nx.write_graphml(spade.result_.tree_, "spade_tree.graphml")

Parameter tuning tips
----------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - If you see...
     - Try...
   * - Too many small clusters
     - Decrease ``n_clusters``
   * - Rare populations missing
     - Increase ``downsample_target`` (e.g., 0.2) or decrease ``knn``
   * - Noisy tree with many short edges
     - Increase ``n_clusters`` to spread out populations
   * - Very slow
     - Decrease ``downsample_target`` (e.g., 0.05)
   * - For fluorescence flow cytometry
     - Use ``cofactor=150.0`` instead of 5.0
```

- [ ] **Step 2: Create `docs/tutorials/comparing_conditions.rst`**

```rst
Tutorial: Comparing Conditions
===============================

A common use case for SPADE is comparing cell populations between experimental conditions
(e.g., healthy vs. disease, pre vs. post treatment).

Strategy
--------

1. **Fit SPADE on the combined dataset** from all conditions
2. **Split cluster assignments by condition** and compare population sizes
3. **Visualize differences** on the tree

This ensures cells from different conditions are assigned to the same clusters, making comparison meaningful.

Example: Two conditions
-----------------------

.. code-block:: python

   import numpy as np
   import pandas as pd
   from densitree import SPADE

   # Simulate two conditions with different rare population abundances
   rng = np.random.default_rng(0)

   # Shared populations
   common_a = rng.normal(loc=[0, 0, 5, 3], scale=0.5, size=(2000, 4))
   common_b = rng.normal(loc=[4, 4, 1, 6], scale=0.5, size=(2000, 4))

   # Rare population: present in disease, nearly absent in healthy
   rare_healthy = rng.normal(loc=[2, 8, 2, 2], scale=0.3, size=(20, 4))
   rare_disease = rng.normal(loc=[2, 8, 2, 2], scale=0.3, size=(200, 4))

   X_healthy = np.vstack([common_a, common_b, rare_healthy])
   X_disease = np.vstack([common_a, common_b, rare_disease])

   # Combine
   X_combined = np.vstack([X_healthy, X_disease])
   condition = np.array(
       ["healthy"] * len(X_healthy) + ["disease"] * len(X_disease)
   )

   print(f"Combined: {len(X_combined)} cells")
   print(f"  Healthy: {(condition == 'healthy').sum()}")
   print(f"  Disease: {(condition == 'disease').sum()}")

Fit SPADE on combined data
---------------------------

.. code-block:: python

   spade = SPADE(
       n_clusters=15,
       downsample_target=0.15,
       transform=None,  # data is already on a reasonable scale
       random_state=42,
   )
   spade.fit(X_combined)

Compare cluster composition
---------------------------

.. code-block:: python

   labels = spade.labels_

   # Count cells per cluster per condition
   comparison = []
   for cluster_id in range(15):
       mask = labels == cluster_id
       n_healthy = ((condition == "healthy") & mask).sum()
       n_disease = ((condition == "disease") & mask).sum()
       total = mask.sum()

       # Fold change (disease / healthy), handling zeros
       if n_healthy > 0:
           fold_change = (n_disease / (condition == "disease").sum()) / \
                         (n_healthy / (condition == "healthy").sum())
       else:
           fold_change = float("inf")

       comparison.append({
           "cluster": cluster_id,
           "healthy": n_healthy,
           "disease": n_disease,
           "total": total,
           "fold_change": fold_change,
       })

   df_comp = pd.DataFrame(comparison).set_index("cluster")
   print(df_comp.sort_values("fold_change", ascending=False))

Visualize on the tree
---------------------

.. code-block:: python

   import matplotlib.pyplot as plt
   import matplotlib.cm as cm
   import networkx as nx

   tree = spade.result_.tree_
   pos = nx.spring_layout(tree, seed=42, weight="weight")

   # Color nodes by fold change
   fold_changes = df_comp["fold_change"].values
   # Cap infinite fold changes for visualization
   fc_capped = np.clip(fold_changes, 0.1, 10)
   log_fc = np.log2(fc_capped)

   norm = plt.Normalize(vmin=-3, vmax=3)
   colors = [cm.RdBu_r(norm(v)) for v in log_fc]
   sizes = [tree.nodes[n].get("size", 1) for n in tree.nodes]
   max_size = max(sizes) or 1
   node_sizes = [s / max_size * 800 + 100 for s in sizes]

   fig, ax = plt.subplots(figsize=(10, 8))
   nx.draw_networkx(
       tree, pos=pos, ax=ax,
       node_size=node_sizes,
       node_color=colors,
       edge_color="gray",
       with_labels=True,
       font_size=8,
   )

   sm = cm.ScalarMappable(cmap=cm.RdBu_r, norm=norm)
   sm.set_array([])
   fig.colorbar(sm, ax=ax, label="log2(fold change disease/healthy)")
   ax.set_title("SPADE Tree: Disease vs Healthy")
   ax.axis("off")
   fig.savefig("condition_comparison.png", dpi=150, bbox_inches="tight")

Blue nodes are enriched in healthy, red nodes in disease. The rare population cluster should appear as a bright red node.

.. image:: ../assets/images/condition_comparison.png
   :alt: Condition comparison

Statistical testing (advanced)
-------------------------------

For rigorous comparison with biological replicates, use a per-cluster test:

.. code-block:: python

   from scipy.stats import fisher_exact

   for cluster_id in range(15):
       mask = labels == cluster_id
       n_h = ((condition == "healthy") & mask).sum()
       n_d = ((condition == "disease") & mask).sum()
       n_h_other = (condition == "healthy").sum() - n_h
       n_d_other = (condition == "disease").sum() - n_d

       table = [[n_h, n_d], [n_h_other, n_d_other]]
       odds_ratio, p_value = fisher_exact(table)

       if p_value < 0.05:
           direction = "enriched in disease" if odds_ratio < 1 else "enriched in healthy"
           print(f"Cluster {cluster_id}: p={p_value:.4f}, OR={odds_ratio:.2f} ({direction})")
```

- [ ] **Step 3: Commit**

```bash
git add docs/tutorials/flow_cytometry.rst docs/tutorials/comparing_conditions.rst
git commit -m "docs: add tutorial RST pages"
```

---

### Task 5: Method pages

**Files:**
- Create: `docs/method/algorithm.rst`
- Create: `docs/method/improvements.rst`
- Create: `docs/method/references.rst`

- [ ] **Step 1: Create `docs/method/algorithm.rst`**

```rst
The SPADE Algorithm
===================

SPADE (Spanning-tree Progression Analysis of Density-normalized Events) was introduced by
`Qiu et al. (2011) <https://doi.org/10.1038/nbt.1991>`_ to extract cellular hierarchies from
high-dimensional cytometry data.

Motivation
----------

In cytometry experiments, cells are measured across many markers simultaneously (10--50+ parameters).
The resulting data has millions of cells in high-dimensional space. Two key challenges arise:

1. **Abundant populations dominate**: Mature cell types (e.g., T cells, B cells) vastly outnumber rare
   progenitors. Standard clustering algorithms allocate most clusters to these abundant types, losing
   resolution on rare but biologically important populations.

2. **Hierarchy matters**: Cells don't just form isolated clusters — they form a developmental continuum.
   A flat clustering misses the progression from stem cells through progenitors to mature cells.

SPADE addresses both problems.

Algorithm steps
---------------

Step 1: Density estimation
~~~~~~~~~~~~~~~~~~~~~~~~~~

For each cell :math:`i`, compute local density :math:`\rho_i` using :math:`k`-nearest neighbor distances:

.. math::

   \rho_i = \frac{1}{d_k(i) + \epsilon}

where :math:`d_k(i)` is the distance to the :math:`k`-th nearest neighbor and :math:`\epsilon` is a
small constant to avoid division by zero.

Cells in crowded regions (abundant populations) get high density; cells in sparse regions (rare
populations) get low density.

**densitree default**: :math:`k = 5`, implemented in ``DensityEstimator``.

Step 2: Density-dependent downsampling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each cell is included in the downsampled set with probability:

.. math::

   p_i = \min\left(1, \; \frac{T \cdot w_i}{\sum_j w_j}\right), \qquad w_i = \frac{1}{\rho_i}

where :math:`T` is the target number of cells to retain. Cells in dense regions have high
:math:`\rho_i`, therefore low :math:`w_i` and low inclusion probability. Rare populations (low
:math:`\rho_i`, high :math:`w_i`) are preferentially retained.

This is the signature innovation of SPADE. After downsampling, the cell distribution is approximately
uniform across phenotypic space, giving rare populations equal representation.

**densitree default**: ``downsample_target=0.05`` (retain 5% of cells).

Step 3: Agglomerative clustering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The downsampled cells are clustered using Ward's linkage hierarchical agglomerative clustering into
:math:`k` clusters. Ward's linkage minimizes within-cluster variance at each merge step, producing
compact, spherical clusters in marker space.

**densitree default**: ``n_clusters=50``, ``linkage="ward"``.

Step 4: Upsampling
~~~~~~~~~~~~~~~~~~~

Every original cell (not just the downsampled ones) is assigned to the nearest cluster centroid in
the transformed feature space. This restores the full dataset's cluster assignments without re-running
the expensive clustering.

Step 5: Minimum spanning tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A complete graph is constructed over the :math:`k` cluster centroids, with edge weights equal to the
Euclidean distance between centroids. The minimum spanning tree (MST) of this graph is extracted using
Kruskal's or Prim's algorithm (via scipy).

The MST captures the shortest-path connectivity between clusters. In biological data, branches in the
tree correspond to differentiation trajectories — a path from a stem cell cluster through intermediate
progenitors to a mature cell type.

Each node in the tree is annotated with:

- **size**: number of cells assigned to that cluster
- **median**: per-marker median expression of cells in that cluster

Data transforms
---------------

Raw cytometry data spans several orders of magnitude. Before running SPADE, markers are typically transformed:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Transform
     - Formula
     - Use case
   * - arcsinh
     - :math:`\text{arcsinh}(x / c)`
     - CyTOF (:math:`c=5`), flow cytometry (:math:`c=150`)
   * - log
     - :math:`\log(1 + x)`
     - Count data
   * - None
     - :math:`x`
     - Pre-transformed data

The arcsinh transform is approximately linear near zero and logarithmic for large values, handling
the dynamic range of fluorescence/mass signals well.

Complexity
----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Step
     - Time complexity
     - Space complexity
   * - Density estimation (k-NN)
     - :math:`O(n \log n)`
     - :math:`O(n)`
   * - Downsampling
     - :math:`O(n)`
     - :math:`O(n)`
   * - Agglomerative clustering
     - :math:`O(m^2 \log m)` where :math:`m = T`
     - :math:`O(m^2)`
   * - Upsampling (1-NN)
     - :math:`O(n \log k)`
     - :math:`O(n)`
   * - MST construction
     - :math:`O(k^2)`
     - :math:`O(k^2)`

The bottleneck is typically the density estimation step for very large datasets (:math:`n > 10^6`).
```

- [ ] **Step 2: Create `docs/method/improvements.rst`**

```rst
Improvements over Standard SPADE
==================================

densitree implements the core SPADE algorithm faithfully but also introduces several improvements and
extension points that address known limitations of the original method.

1. Deterministic mode
---------------------

**Problem**: The original SPADE produces different results on each run due to stochastic downsampling.
This was identified as a major reproducibility concern by
`Qiu (2017) <https://doi.org/10.1002/cyto.a.23068>`_.

**densitree solution**: The ``random_state`` parameter seeds all stochastic operations (downsampling,
spring layout for visualization). With a fixed seed, results are fully deterministic:

.. code-block:: python

   spade = SPADE(n_clusters=30, random_state=42)
   labels_a = spade.fit_predict(X)
   labels_b = spade.fit_predict(X)
   assert np.array_equal(labels_a, labels_b)  # always True

2. Pluggable density estimation
---------------------------------

**Problem**: The standard k-NN density estimator can be sensitive to the choice of :math:`k` and
performs poorly on data with highly variable local density scales.

**densitree solution**: The ``density_estimator`` parameter accepts any ``BaseStep`` subclass, enabling
drop-in replacement with alternative density methods:

.. code-block:: python

   from densitree import SPADE, BaseStep
   import numpy as np
   from scipy.stats import gaussian_kde

   class KDEDensity(BaseStep):
       def __init__(self, bandwidth="scott"):
           self.bandwidth = bandwidth

       def run(self, data, **ctx):
           kde = gaussian_kde(data.T, bw_method=self.bandwidth)
           return {"density": kde(data.T)}

   spade = SPADE(density_estimator=KDEDensity(), n_clusters=30)

Other candidates worth exploring:

- **Local outlier factor (LOF)** density from scikit-learn
- **KDE with adaptive bandwidth** for multi-scale density
- **Shared nearest neighbor (SNN)** density, which is more robust to dimensionality

3. Flexible transforms
-----------------------

**Problem**: The original SPADE used a fixed arcsinh transform. Different data types (CyTOF,
fluorescence flow, spectral flow, scRNA-seq) benefit from different transforms.

**densitree solution**: Built-in ``"arcsinh"``, ``"log"``, and ``None`` transforms with configurable
cofactor. The transform is applied before all pipeline steps, so clustering and density estimation
operate in the transformed space while medians in the result are computed in the original space.

4. scikit-learn compatible API
--------------------------------

**Problem**: The original R implementation uses a bespoke, script-oriented API that doesn't integrate
well with modern ML workflows.

**densitree solution**: Standard ``fit()`` / ``fit_predict()`` interface. This enables:

- Pipeline composition with ``sklearn.pipeline.Pipeline``
- Hyperparameter search with ``GridSearchCV`` (over ``n_clusters``, ``downsample_target``, ``knn``)
- Drop-in comparison with any sklearn-compatible clusterer

5. Rich result object
----------------------

**Problem**: Extracting cluster statistics, tree structure, and visualization from the R implementation
requires multiple separate function calls and manual bookkeeping.

**densitree solution**: ``SPADEResult`` bundles everything — labels, tree, downsampled data, cluster
statistics DataFrame — in a single object with a ``plot_tree()`` method.

----

Planned improvements
---------------------

Adaptive cluster count
~~~~~~~~~~~~~~~~~~~~~~~

Instead of requiring a fixed ``n_clusters``, automatically select the number of clusters using the gap
statistic or silhouette score on the downsampled data:

.. math::

   k^* = \arg\max_k \text{Silhouette}(X_\text{down}, \text{labels}_k)

This would add an ``n_clusters="auto"`` mode.

Multi-run consensus
~~~~~~~~~~~~~~~~~~~~

Run SPADE multiple times with different random seeds and build a consensus tree. This addresses the
stochasticity concern more robustly than a single deterministic run by capturing the stable structure
across runs. The consensus approach was suggested by
`Qiu (2017) <https://doi.org/10.1002/cyto.a.23068>`_.

Approximate k-NN for large datasets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For datasets with :math:`n > 10^6` cells, exact k-NN becomes a bottleneck. Using approximate nearest
neighbor libraries (PyNNDescent, FAISS, Annoy) for density estimation would provide near-linear scaling.

Edge significance testing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Not all edges in the MST are equally meaningful. Adding a permutation-based significance test for edge
weights would help distinguish biologically meaningful connections from noise-driven ones.

Marker-specific downsampling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current approach uses a single density estimate across all markers. For panels with functionally
distinct marker groups (e.g., surface markers vs. intracellular signaling), computing density on a
subset of markers (typically surface/lineage markers) while clustering on all markers may produce
better trees.
```

- [ ] **Step 3: Create `docs/method/references.rst`**

```rst
References
==========

Core SPADE publications
------------------------

1. **Qiu, P., Simonds, E.F., Bendall, S.C., Gibbs, K.D. Jr., Bruggner, R.V., Linderman, M.D., Sachs, K.,
   Nolan, G.P., & Plevritis, S.K.** (2011). "Extracting a cellular hierarchy from high-dimensional cytometry
   data with SPADE." *Nature Biotechnology*, 29(10), 886--891.
   `doi:10.1038/nbt.1991 <https://doi.org/10.1038/nbt.1991>`_

   The original SPADE paper. Introduces density-dependent downsampling + agglomerative clustering + MST
   for CyTOF data.

2. **Qiu, P.** (2017). "Toward deterministic and semiautomated SPADE analysis." *Cytometry Part A*,
   91(7), 714--727. `doi:10.1002/cyto.a.23068 <https://doi.org/10.1002/cyto.a.23068>`_

   Addresses stochasticity and proposes deterministic variants of SPADE.

Key applications
-----------------

3. **Bendall, S.C., Simonds, E.F., Qiu, P., et al.** (2011). "Single-cell mass cytometry of differential
   immune and drug responses across a human hematopoietic continuum." *Science*, 332(6030), 687--696.
   `doi:10.1126/science.1198704 <https://doi.org/10.1126/science.1198704>`_

   First high-profile CyTOF + SPADE application — mapping human hematopoiesis.

4. **Levine, J.H., Simonds, E.F., Bendall, S.C., et al.** (2015). "Data-Driven Phenotypic Dissection of
   AML Reveals Progenitor-like Cells that Correlate with Prognosis." *Cell*, 162(1), 184--197.
   `doi:10.1016/j.cell.2015.05.047 <https://doi.org/10.1016/j.cell.2015.05.047>`_

   Introduces PhenoGraph; includes SPADE comparisons. Source of the **Levine_32dim** and **Levine_13dim**
   benchmark datasets.

Benchmark studies
------------------

5. **Samusik, N., Good, Z., Spitzer, M.H., Davis, K.L., & Nolan, G.P.** (2016). "Automated mapping of
   phenotype space with single-cell data." *Nature Methods*, 13(6), 493--496.
   `doi:10.1038/nmeth.3863 <https://doi.org/10.1038/nmeth.3863>`_

   Systematic comparison of SPADE, FlowSOM, PhenoGraph, and other methods. Source of the **Samusik_01**
   benchmark dataset.

6. **Weber, L.M. & Robinson, M.D.** (2016). "Comparison of clustering methods for high-dimensional
   single-cell flow and mass cytometry data." *Cytometry Part A*, 89(12), 1084--1096.
   `doi:10.1002/cyto.a.23030 <https://doi.org/10.1002/cyto.a.23030>`_

   Comprehensive benchmark of 18 clustering methods including SPADE, with standardized evaluation metrics.

Related methods
----------------

7. **Van Gassen, S., Callebaut, B., Van Helden, M.J., et al.** (2015). "FlowSOM: Using self-organizing
   maps for visualization and interpretation of cytometry data." *Cytometry Part A*, 87(7), 636--645.
   `doi:10.1002/cyto.a.22625 <https://doi.org/10.1002/cyto.a.22625>`_

   FlowSOM — often compared to SPADE. Faster, also produces a tree, but uses SOMs instead of
   density-dependent downsampling.

8. **Levine, J.H., et al.** (2015). See reference 4 above.

   PhenoGraph — graph-based clustering using k-NN + Louvain community detection. Produces flat clusters
   (no tree), but often better cluster purity.

Datasets used in densitree benchmarks
--------------------------------------

9. **Levine_32dim**: 81,747 cells, 32 markers, 14 manually gated populations. From reference 4. Available
   via `FlowRepository FR-FCM-ZZPH <https://flowrepository.org/id/FR-FCM-ZZPH>`_ and
   `Weber & Robinson's HDCytoData <https://github.com/lmweber/HDCytoData>`_.

10. **Samusik_01**: 86,864 cells, 39 markers, 24 manually gated populations. From reference 5. Available
    via `FlowRepository FR-FCM-ZZYA <https://flowrepository.org/id/FR-FCM-ZZYA>`_ and
    `HDCytoData <https://github.com/lmweber/HDCytoData>`_.
```

- [ ] **Step 4: Commit**

```bash
git add docs/method/algorithm.rst docs/method/improvements.rst docs/method/references.rst
git commit -m "docs: add method RST pages with math"
```

---

### Task 6: Benchmarks pages

**Files:**
- Create: `docs/benchmarks/overview.rst`
- Create: `docs/benchmarks/datasets.rst`
- Create: `docs/benchmarks/results.rst`
- Create: `docs/benchmarks/comparison.rst`

- [ ] **Step 1: Create `docs/benchmarks/overview.rst`**

```rst
Benchmarks Overview
===================

densitree includes a comprehensive benchmarking framework for comparing SPADE against other single-cell
clustering methods on real and synthetic cytometry data.

What we benchmark
-----------------

We evaluate six clustering methods:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Method
     - Implementation
     - Type
   * - **densitree**
     - This library
     - Density-dependent downsampling + agglomerative + MST
   * - **FlowSOM (official)**
     - ``flowsom`` Python package (saeyslab)
     - Self-organizing maps + consensus metaclustering
   * - **FlowSOM-style**
     - MiniBatchKMeans + agglomerative
     - Fast reimplementation of the FlowSOM two-stage approach
   * - **PhenoGraph-style**
     - k-NN graph + Leiden community detection
     - Graph-based community detection
   * - **KMeans**
     - scikit-learn
     - Centroid-based flat clustering (baseline)
   * - **Agglomerative**
     - scikit-learn (with subsampling for large data)
     - Ward's linkage hierarchical clustering (baseline)

Metrics
-------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Metric
     - What it measures
     - Range
   * - **ARI** (Adjusted Rand Index)
     - Overall clustering agreement with ground truth, adjusted for chance
     - -1 to 1 (1 = perfect)
   * - **NMI** (Normalized Mutual Information)
     - Information-theoretic cluster-label agreement
     - 0 to 1 (1 = perfect)
   * - **Rare Population F1**
     - Precision/recall for populations comprising <3% of cells
     - 0 to 1 (1 = perfect)
   * - **Runtime**
     - Wall-clock time in seconds
     - Lower is better

Datasets
--------

- :doc:`datasets` — **Levine_32dim**: 104,184 cells (gated), 32 CyTOF markers, 14 populations
- :doc:`datasets` — **Synthetic**: 50,000 cells, 15 features, 12 populations (3 rare)

Running benchmarks
------------------

.. code-block:: bash

   cd benchmarks

   # Synthetic dataset (no download needed)
   python run_benchmark.py synthetic

   # Real dataset (downloads automatically)
   python run_benchmark.py Levine_32dim

   # Specific methods only
   python run_benchmark.py Levine_32dim "densitree,flowsom_official" 5

Results are saved to ``benchmarks/results/`` in JSON, CSV, and Markdown formats.
```

- [ ] **Step 2: Create `docs/benchmarks/datasets.rst`**

```rst
Benchmark Datasets
==================

Levine_32dim
------------

The standard benchmark dataset for cytometry clustering methods.

.. list-table::
   :header-rows: 0
   :widths: auto

   * - **Source**
     - `Levine et al. (2015) Cell 162(1):184-197 <https://doi.org/10.1016/j.cell.2015.05.047>`_
   * - **Total cells**
     - 265,627
   * - **Gated cells**
     - 104,184 (39.2%)
   * - **Markers**
     - 32 surface CyTOF markers
   * - **Populations**
     - 14 manually gated immune populations
   * - **Rare populations (<3%)**
     - 7
   * - **Technology**
     - CyTOF (mass cytometry)
   * - **Tissue**
     - Human bone marrow

Population distribution
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Population
     - Cells
     - Fraction
   * - Large (>5%)
     - 4 populations
     - ~32% of gated cells each
   * - Medium (1-5%)
     - 3 populations
     - ~2% each
   * - Rare (<1%)
     - 7 populations
     - 0.1--0.5% each

The high number of rare populations (half of all populations) makes this dataset particularly challenging
for methods that don't account for density imbalance.

Download
~~~~~~~~

The dataset is automatically downloaded from
`lmweber/benchmark-data-Levine-32-dim <https://github.com/lmweber/benchmark-data-Levine-32-dim>`_
when first used:

.. code-block:: python

   from benchmarks.download_data import load_dataset
   X, labels, markers = load_dataset("Levine_32dim")

Preprocessing
~~~~~~~~~~~~~

- Ungated cells (60.8% of total) are removed for evaluation
- Data is arcsinh-transformed with cofactor 5 (standard for CyTOF) before clustering
- All 32 surface markers are used for clustering

----

Synthetic
---------

A challenging synthetic dataset designed to stress-test clustering methods with overlapping populations,
hierarchical structure, and rare subsets.

.. list-table::
   :header-rows: 0
   :widths: auto

   * - **Cells**
     - 50,000
   * - **Features**
     - 15
   * - **Populations**
     - 12
   * - **Rare populations (<3%)**
     - 3
   * - **Seed**
     - 42 (deterministic)

Design
~~~~~~

- **4 lineages** of 3 sub-populations each — sub-populations within a lineage are close in feature space
  (harder to separate)
- **Per-feature variable spread** — some markers are more discriminative than others
- **3 rare populations** (~1% each, tighter clusters)
- **Global measurement noise** added

.. code-block:: python

   from benchmarks.download_data import generate_synthetic_benchmark
   X, labels, markers = generate_synthetic_benchmark()
```

- [ ] **Step 3: Create `docs/benchmarks/results.rst`**

```rst
Benchmark Results
=================

All results averaged over 3 runs with different random seeds. Metrics computed against manually gated
ground truth labels.

Levine_32dim (real CyTOF data)
--------------------------------

104,184 gated cells, 32 markers, 14 populations (7 rare).

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Method
     - ARI
     - NMI
     - Rare F1
     - Runtime (s)
   * - **densitree**
     - **0.942** ± 0.004
     - **0.930** ± 0.002
     - 0.481 ± 0.047
     - 4.0
   * - FlowSOM-style
     - 0.934 ± 0.011
     - 0.920 ± 0.008
     - 0.536 ± 0.009
     - **0.1**
   * - FlowSOM (official)
     - 0.914 ± 0.011
     - 0.914 ± 0.003
     - **0.563** ± 0.031
     - 3.6
   * - PhenoGraph-style
     - 0.908 ± 0.000
     - 0.906 ± 0.001
     - 0.221 ± 0.000
     - 88.0
   * - KMeans
     - 0.569 ± 0.025
     - 0.802 ± 0.009
     - 0.379 ± 0.043
     - 1.3

densitree achieves the **highest ARI and NMI** with the **lowest variance** (std 0.004) of any method
tested.

----

Synthetic dataset
-----------------

50,000 cells, 15 features, 12 populations (3 rare, hierarchically structured).

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Method
     - ARI
     - NMI
     - Rare F1
     - Runtime (s)
   * - **PhenoGraph-style**
     - **0.743** ± 0.002
     - **0.843** ± 0.001
     - **0.588** ± 0.125
     - 12.7
   * - Agglomerative
     - 0.694 ± 0.004
     - 0.772 ± 0.000
     - 0.500 ± 0.000
     - 5.5
   * - KMeans
     - 0.678 ± 0.005
     - 0.764 ± 0.003
     - 0.500 ± 0.000
     - 0.9
   * - **densitree**
     - 0.674 ± 0.016
     - 0.765 ± 0.005
     - 0.500 ± 0.000
     - 6.1
   * - FlowSOM (official)
     - 0.584 ± 0.013
     - 0.745 ± 0.006
     - 0.500 ± 0.000
     - 1.7
   * - FlowSOM-style
     - 0.584 ± 0.033
     - 0.732 ± 0.012
     - 0.500 ± 0.000
     - 0.0

----

Key takeaways
-------------

1. **densitree achieves state-of-the-art accuracy** on the Levine_32dim benchmark (ARI 0.942), surpassing
   FlowSOM (0.934) and PhenoGraph (0.908).

2. **PhenoGraph excels on synthetic data** with hierarchical structure, thanks to its graph-based approach
   that naturally captures complex cluster shapes.

3. **FlowSOM is the fastest** method tested (0.1s), making it ideal for interactive exploration.
   densitree trades speed for accuracy and stability.

4. **densitree uniquely combines clustering accuracy with tree structure** — the density-dependent
   downsampling and MST construction are preserved for rare population visualization.

5. **Runtime**: FlowSOM-style < KMeans << densitree ~ FlowSOM official << PhenoGraph.
```

- [ ] **Step 4: Create `docs/benchmarks/comparison.rst`**

```rst
Method Comparison
=================

A detailed analysis of how densitree compares to other cytometry clustering tools across multiple dimensions.

Algorithm comparison
--------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * -
     - densitree
     - FlowSOM
     - PhenoGraph
     - KMeans
   * - **Core approach**
     - Density downsampling + agglomerative
     - SOM + consensus metaclustering
     - k-NN graph + Leiden
     - Centroid optimization
   * - **Output**
     - Tree of clusters
     - Tree of metaclusters
     - Flat clusters
     - Flat clusters
   * - **Handles rare pops**
     - Yes (density normalization)
     - No
     - Partially (graph resolution)
     - No
   * - **Deterministic**
     - Yes (with seed)
     - Yes (with seed)
     - Approximately
     - Yes (with seed)
   * - **n_clusters**
     - User-specified
     - User-specified
     - Automatic (resolution)
     - User-specified
   * - **Scalability**
     - ~100k cells
     - ~1M cells
     - ~100k cells
     - ~1M+ cells

When to use each method
------------------------

Use densitree when
~~~~~~~~~~~~~~~~~~

- **Rare populations matter** — SPADE's density-dependent downsampling is specifically designed to
  preserve rare subsets that would be lost by other methods
- **You need tree structure** — the MST reveals differentiation hierarchies and gradual phenotypic
  transitions
- **You want overclustering + exploration** — SPADE with 50--200 clusters produces fine-grained nodes
  that you can explore interactively on the tree
- **Reproducibility is critical** — deterministic with ``random_state``

Use FlowSOM when
~~~~~~~~~~~~~~~~~

- **You know the number of populations** — FlowSOM's metaclustering is extremely effective when the
  expected structure matches the cluster count
- **Speed matters** — FlowSOM is the fastest method tested, processing 100k cells in <1 second
- **The standard FlowSOM tree is sufficient** — FlowSOM also produces a tree (the SOM grid), though
  it reflects SOM topology rather than phenotypic distances

Use PhenoGraph when
~~~~~~~~~~~~~~~~~~~~

- **Discovery is the goal** — PhenoGraph automatically determines the number of clusters
- **Cluster shapes are complex** — the graph-based approach captures non-spherical clusters that
  agglomerative methods miss
- **You don't need a tree** — PhenoGraph produces flat clusters only

Use KMeans / Agglomerative when
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Simplicity and speed** — good baselines for quick exploration
- **The data is well-separated** — these methods work fine when populations are distinct

Implementation comparison
--------------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Feature
     - densitree
     - FlowSOM (Python)
     - PhenoGraph
     - R spade
   * - **Language**
     - Python
     - Python
     - Python
     - R/C++
   * - **API**
     - sklearn-compatible
     - AnnData/scverse
     - Function-based
     - Script-based
   * - **Input**
     - numpy/pandas
     - AnnData
     - numpy
     - FCS files
   * - **FCS parsing**
     - No (bring your own)
     - Via readfcs/anndata
     - No
     - Built-in
   * - **Interactive viz**
     - plotly backend
     - scanpy integration
     - No
     - No
   * - **Custom steps**
     - Yes (BaseStep ABC)
     - Limited
     - No
     - No
   * - **pip installable**
     - Yes
     - Yes
     - Yes (archived)
     - No (BiocManager)
   * - **Active**
     - Yes
     - Yes
     - Archived (2020)
     - Archived

Honest assessment of densitree limitations
-------------------------------------------

1. **Lower ARI at matching cluster count**: When n_clusters equals the true number of populations,
   densitree's ARI (0.58) is significantly below FlowSOM (0.93) and PhenoGraph (0.91). This is partly
   because SPADE's downsampling discards information that could improve cluster boundaries.

2. **Downsampling introduces variance**: Even with a fixed seed, the particular cells retained affect
   downstream clustering. Running SPADE at its overclustering operating point (50+ clusters) mitigates
   this.

3. **No automatic cluster count**: Unlike PhenoGraph, you must specify ``n_clusters``. The planned
   ``n_clusters="auto"`` mode (see :doc:`../method/improvements`) will address this.

4. **No FCS parsing**: densitree operates on numpy arrays. You need ``readfcs``, ``fcsparser``, or
   ``flowio`` to read FCS files. This is by design — densitree focuses on the algorithm, not the I/O.

Reproducing these benchmarks
-----------------------------

.. code-block:: bash

   cd benchmarks
   pip install readfcs flowsom leidenalg igraph

   # Full benchmark on Levine_32dim (downloads 44MB FCS file)
   python run_benchmark.py Levine_32dim

   # Quick synthetic benchmark (no download)
   python run_benchmark.py synthetic

   # Specific methods, 5 runs
   python run_benchmark.py Levine_32dim "densitree,flowsom_official" 5
```

- [ ] **Step 5: Commit**

```bash
git add docs/benchmarks/overview.rst docs/benchmarks/datasets.rst docs/benchmarks/results.rst docs/benchmarks/comparison.rst
git commit -m "docs: add benchmarks RST pages"
```

---

### Task 7: API reference

**Files:**
- Create: `docs/api/spade.rst`
- Create: `docs/api/result.rst`
- Create: `docs/api/steps.rst`
- Create: `docs/api/plotting.rst`

- [ ] **Step 1: Create `docs/api/spade.rst`**

```rst
SPADE
=====

.. autoclass:: densitree.spade.SPADE
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource
```

- [ ] **Step 2: Create `docs/api/result.rst`**

```rst
SPADEResult
===========

.. autoclass:: densitree.result.SPADEResult
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource
```

- [ ] **Step 3: Create `docs/api/steps.rst`**

```rst
Pipeline Steps
==============

BaseStep
--------

.. autoclass:: densitree.steps.base.BaseStep
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

DensityEstimator
----------------

.. autoclass:: densitree.steps.density.DensityEstimator
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

DownsampleStep
--------------

.. autoclass:: densitree.steps.downsample.DownsampleStep
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

ClusterStep
-----------

.. autoclass:: densitree.steps.cluster.ClusterStep
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

UpsampleStep
------------

.. autoclass:: densitree.steps.upsample.UpsampleStep
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

MSTBuilder
----------

.. autoclass:: densitree.steps.mst.MSTBuilder
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource
```

- [ ] **Step 4: Create `docs/api/plotting.rst`**

```rst
Plotting
========

Matplotlib backend
------------------

.. autofunction:: densitree.plot.matplotlib.plot_tree

Plotly backend
--------------

.. autofunction:: densitree.plot.plotly.plot_tree
```

- [ ] **Step 5: Verify build succeeds**

```bash
uv run sphinx-build -b html docs/ _build/html 2>&1 | tail -20
```

Expected output ends with something like:
```
build succeeded.

The HTML pages are in _build/html.
```

If there are autodoc import errors, check that `sys.path.insert(0, os.path.abspath('..'))` in `conf.py` resolves the `densitree` package correctly.

- [ ] **Step 6: Commit**

```bash
git add docs/api/spade.rst docs/api/result.rst docs/api/steps.rst docs/api/plotting.rst
git commit -m "docs: add API reference RST files with autodoc"
```

---

### Task 8: Update pyproject.toml and .gitignore

**Files:**
- Modify: `pyproject.toml`
- Modify: `.gitignore`

- [ ] **Step 1: Update docs dependencies in `pyproject.toml`**

Replace the `docs` section under `[project.optional-dependencies]`:

Old:
```toml
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=1.0",
]
```

New:
```toml
docs = [
    "sphinx>=7.0",
    "pydata-sphinx-theme>=0.15",
    "sphinx-copybutton>=0.5",
]
```

- [ ] **Step 2: Add `_build/` to `.gitignore`**

Add this line to `.gitignore`:
```
_build/
```

Remove the existing `site/` line (that was the MkDocs output directory — it can stay for now as it doesn't hurt, but removing it keeps the file clean).

- [ ] **Step 3: Verify the dependency update installs correctly**

```bash
uv sync --extra docs
```

Expected: installs sphinx, pydata-sphinx-theme, sphinx-copybutton. No errors.

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml .gitignore uv.lock
git commit -m "docs: switch docs dependencies from MkDocs to Sphinx"
```

---

### Task 9: Update CI workflow

**Files:**
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Update the `docs` job in `.github/workflows/ci.yml`**

Replace the entire `docs` job:

Old:
```yaml
docs:
  runs-on: ubuntu-latest
  needs: test
  if: github.ref == 'refs/heads/master' && github.event_name == 'push'

  permissions:
    contents: write

  steps:
    - uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v4

    - name: Set up Python
      run: uv python install 3.12

    - name: Install dependencies
      run: uv sync --extra docs

    - name: Deploy docs
      run: uv run mkdocs gh-deploy --force
```

New:
```yaml
docs:
  runs-on: ubuntu-latest
  needs: test
  if: github.ref == 'refs/heads/master' && github.event_name == 'push'

  permissions:
    contents: write

  steps:
    - uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v4

    - name: Set up Python
      run: uv python install 3.12

    - name: Install dependencies
      run: uv sync --extra docs

    - name: Build docs
      run: uv run sphinx-build -b html docs/ _build/html

    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./_build/html
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: switch docs build from mkdocs to sphinx-build"
```

---

### Task 10: Remove MkDocs artifacts and final verification

**Files:**
- Delete: `mkdocs.yml`
- Delete: `docs/overrides/main.html`
- Delete: `docs/overrides/` directory

- [ ] **Step 1: Delete MkDocs files**

```bash
rm /home/aivuk/densitree/mkdocs.yml
rm -rf /home/aivuk/densitree/docs/overrides/
```

- [ ] **Step 2: Run a clean full build with warnings-as-errors**

```bash
cd /home/aivuk/densitree
rm -rf _build/
uv run sphinx-build -W -b html docs/ _build/html
```

Expected: build succeeds with exit code 0 and prints:
```
build succeeded.

The HTML pages are in _build/html.
```

If warnings appear, fix them before proceeding. Common issues:
- Missing cross-reference: check RST link syntax
- `.. image::` path not found: verify `html_extra_path = ['CNAME', 'assets']` in conf.py
- autodoc can't import module: verify `sys.path` in conf.py

- [ ] **Step 3: Spot-check the output in a browser**

```bash
cd /home/aivuk/densitree
python -m http.server 8000 --directory _build/html
```

Open `http://localhost:8000` and verify:
- Home page loads with images
- Navigation sidebar has all sections
- API pages render autodoc output
- Math renders on `method/algorithm`
- Code blocks have copy button
- Dark/light mode toggle works

- [ ] **Step 4: Commit removal of MkDocs files**

```bash
git add -A
git commit -m "docs: remove mkdocs.yml and overrides, complete Sphinx migration"
```
