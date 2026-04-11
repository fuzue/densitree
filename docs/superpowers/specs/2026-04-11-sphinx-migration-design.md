# Sphinx Migration Design

**Date:** 2026-04-11  
**Project:** densitree  
**Status:** Approved

## Context

Material for MkDocs entered maintenance mode in November 2025 with ~12 months of remaining support, after which the project will be unmaintained. The maintainer launched Zensical as a successor, but it is too new and unproven. Migrating to Sphinx aligns densitree with the scientific Python ecosystem (NumPy, SciPy, scikit-learn, pandas) and provides a long-term stable documentation foundation.

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Doc format | reStructuredText (RST) | Native Sphinx, no translation layer, better intersphinx cross-references |
| Hosting | GitHub Pages (unchanged) | Current setup at densitree.fuzue.tech, no disruption |
| Theme | PyData Sphinx Theme | Scientific Python standard, used by NumPy/SciPy/scikit-learn |
| API docs | autodoc + napoleon | Full control, matches how the scientific Python ecosystem does it |

## Project Structure

```
docs/
  conf.py                        # Sphinx config (replaces mkdocs.yml)
  index.rst                      # Root toctree
  getting-started/
    installation.rst
    quickstart.rst
  guide.rst
  tutorials/
    flow_cytometry.rst
    comparing_conditions.rst
  api/
    spade.rst
    result.rst
    steps.rst
    plotting.rst
  benchmarks/
    overview.rst
    datasets.rst
    results.rst
    comparison.rst
  method/
    algorithm.rst
    improvements.rst
    references.rst
  assets/
    images/                      # unchanged
```

`mkdocs.yml` is deleted. `_build/` is added to `.gitignore`.

## Sphinx Configuration (`conf.py`)

### Extensions

- `sphinx.ext.autodoc` — pulls docstrings from source
- `sphinx.ext.napoleon` — parses NumPy-style docstrings
- `sphinx.ext.autosummary` — generates summary tables for API pages
- `sphinx.ext.intersphinx` — cross-links to external docs
- `sphinx.ext.viewcode` — "view source" links
- `sphinx-copybutton` — copy button on code blocks

### Intersphinx Targets

Python stdlib, NumPy, SciPy, scikit-learn, pandas, matplotlib, networkx, plotly.

### Theme Configuration

PyData Sphinx Theme with:
- GitHub repo link in navbar
- PyPI link in navbar
- Light/dark mode toggle (built-in)

## Content Migration

### Markdown → RST Conversions

| Markdown | RST |
|---|---|
| `# Heading` | `Heading\n=======` |
| ` ```python ``` ` | `.. code-block:: python` |
| `!!! note` | `.. note::` |
| `$$...$$` | `.. math::` |
| `` $...$ `` | `` :math:`...` `` |
| `![alt](path)` | `.. image:: path` |
| `[text](url)` | `` `text <url>`_ `` |

### Interactive HTML Tree

The `assets/images/tree_interactive.html` embed uses `.. raw:: html` with an iframe, identical to the current approach.

### API Reference Files

Each API RST file uses explicit autodoc directives. Example for `api/spade.rst`:

```rst
SPADE
=====

.. autoclass:: densitree.SPADE
   :members:
   :undoc-members:
   :show-inheritance:
```

Same pattern for `SPADEResult`, pipeline steps, and plotting functions.

## GitHub Actions Deployment

### Updated workflow steps

1. `pip install -e ".[docs]"` — install Sphinx dependencies
2. `sphinx-build -b html docs/ _build/html` — build docs
3. Deploy `_build/html/` to `gh-pages` branch (same target as now)

### Updated `pyproject.toml` docs extras

```toml
docs = [
    "sphinx>=7.0",
    "pydata-sphinx-theme>=0.15",
    "sphinx-copybutton>=0.5",
]
```

## Out of Scope

- Content changes — the migration preserves all existing content as-is
- URL structure changes — page URLs should remain equivalent where possible
- Any new documentation pages or sections
