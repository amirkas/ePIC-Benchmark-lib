# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path('..', 'src').resolve()))


# -- Project information -----------------------------------------------------

project = "ePIC Workflows"
copyright = "2025, Lawrence Berkeley National Laboratory"
author = "Amir Abdou"


# -- General configuration ---------------------------------------------------
# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.graphviz",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_copybutton",
    "sphinx_gitref",
    
]


intersphinx_mapping = {
    "rtd": ("https://docs.readthedocs.io/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

#Graphviz configuration
graphviz_output_format = 'svg'

#autodoc_pydantic settings
autodoc_pydantic_model_show_json = False
autodoc_pydantic_settings_show_json = False
autodoc_pydantic_model_hide_paramlist = True
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_field_list_validators = False





#Set gitref branch
gitref_branch = "documentation"
gitref_updating = True

templates_path = ["_templates"]

# -- Options for EPUB output
epub_show_urls = "footnote"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = "sphinx_rtd_theme"

# html_theme = "pydata_sphinx_theme"

# html_theme_options = {
#     "**": ["sidebar-nav-bs.html"], #Ensures primary sidebar (left) is displayed
#     "ethical_ads": {},  # disables Ethical Ads
# }

# html_theme = "sphinxawesome_theme"

# html_theme_options = {
#     "globaltoc_includehidden": True, 

# }

html_theme = "sphinx_book_theme"

html_theme_options = {
    "path_to_docs": "docs",
    "repository_url": "https://github.com/amirkas/ePIC-Benchmark-lib",
    "repository_branch": "documentation",
    "use_repository_button": True,
    "max_navbar_depth": 4,
    "home_page_in_toc": True,
    "collapse_navbar": False,
    "show_navbar_depth": 1,
    "logo": {
        "text": "ePIC Workflows",
        "image_light": "_static/ePIC_transparent_black_bkgnd.png",
        "image_dark": "_static/ePIC_transparent_white_bkgnd_new.png",
    }
}




# html_theme_options = {
#   "show_nav_level": 2,
#   "primary_sidebar_end": [],
# }

# html_sidebars = {
#     "**": ["sidebar-nav-bs"]
# }



# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# html_css_files = [
#     'custom.css',
# ]

# def setup(app):
#     app.add_css_file("custom.css")
