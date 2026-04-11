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
html_extra_path = ['CNAME', 'assets']

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
