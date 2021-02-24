# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, make it absolute.

import logging
import os
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adt


logging.basicConfig(level="DEBUG")


# -- Project information -----------------------------------------------------

project = "ADT"
copyright = "2021 Lewis Gaul"
author = "Lewis Gaul"

# The full version, including alpha/beta/rc tags
release = adt.__version__
version = ".".join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
]

# Add support for parsing markdown files.
source_parsers = {
    # ".md": CommonMarkParser,
}

source_suffix = [".rst"]

# A boolean that decides whether module names are prepended to all object names
# (for object types where a "module" of some kind is defined).
add_module_names = True

# Tell Sphinx to warn about all references where the target cannot be found.
nitpicky = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "README*"]


# -- Extension configuration -------------------------------------------------

# Automatically documented members are sorted alphabetical (value
# 'alphabetical'), by member type (value 'groupwise') or by source order (value
# 'bysource').
autodoc_member_order = "groupwise"

# Display type hints in the description.
autodoc_typehints = "description"

# This value selects what content will be inserted into the main body of an
# autoclass directive. The possible values are: 'class', 'init', 'both'.
# autoclass_content = "both"

autodoc_default_options = {
    "special-members": "__init__",
    "undoc-members": True,
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
# html_theme = "nature"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Add a custom style sheet to make some slight modifications to the theme.
# html_style = "custom.css"

# Add a logo to the top left of the page.
# html_logo = "_static/logo.png"

# Add a logo to be used in the browser tab.
# html_favicon = html_logo

# Set the title.
html_title = f"{project} {version}"

# Last updated date in the footer.
html_last_updated_fmt = "%Y-%b-%d"

# Override the default sidebars. The dict keys match file paths.
html_sidebars = {
    "**": [
        # "localtoc.html",
        "globaltoc.html",
        # "relations.html",
        # "sourcelink.html",
        "searchbox.html",
    ],
}


# -- Custom extensions -------------------------------------------------------


def remove_module_docstring(app, what, name, obj, options, lines):
    if what == "module":
        del lines[:]


def setup(app):
    app.connect("autodoc-process-docstring", remove_module_docstring)
    app.add_css_file("custom.css")
