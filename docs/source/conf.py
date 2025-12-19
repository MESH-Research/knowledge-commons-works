# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Knowledge Commons Works"
copyright = "2025, Mesh Research"
author = "Mesh Research"
release = "0.7.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["myst_parser", "sphinx_copybutton", "sphinx.ext.autosectionlabel"]

templates_path = ["_templates"]
exclude_patterns = []

autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 4


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
# html_theme = "pydata_sphinx_theme"
# html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    # "show_nav_level": 2,
    # "navbar_center": ["navbar-nav"],
}
# html_sidebars = {
# "**": [
#     "sidebar-nav-bs",
#     "sidebar-ethical-ads",
# ]
# }
