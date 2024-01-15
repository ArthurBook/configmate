# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import pathlib
import sys
from sphinx.ext import autodoc

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "configmate"
copyright = "2023, Arthur Böök"
author = "Arthur Böök"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.doctest",  # test snippets in the documentation
    "sphinx.ext.autosummary",  # generate autodoc summaries
    "sphinx.ext.autodoc",  # generate documentation from docstrings
    "sphinx.ext.napoleon",  # support for Google-style docstrings
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here.
sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
