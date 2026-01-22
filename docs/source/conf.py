# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'heterograph'
copyright = '2025, Custom Computing Group'
author = 'Custom Computing Group'
release = '1.0'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import os.path as osp
import fnmatch
import yaml

# adapted from: https://github.com/abey79/vsketch

root_src = osp.join(osp.abspath('../../'))

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
    "sphinx.ext.githubpages",
    "myst_parser",
    "sphinx_copybutton",
    "autoapi.extension",
    "nbsphinx"
]

# debug: never to avoid re-executing the notebooks
nbsphinx_execute="always" # auto|always|never
nbsphinx_allow_errors = False

doctest_global_setup = '''
from heterograph.query import *
from heterograph import *
from artisan import *
'''

templates_path = ['_templates']

# Don't mess with double-dash used in CLI options
smartquotes_action = "qe"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "venv", ".*", "notebooks_/.pytest_cache/README.md"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

#html_theme = 'furo'

suppress_warnings = ["config.cache"]


html_static_path = ['_static']

# -- Napoleon options
napoleon_include_init_with_doc = False
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True


# -- autoapi configuration ---------------------------------------------------
autoapi_dirs = [osp.join(root_src, 'heterograph')]
autoapi_type = "python"
autoapi_member_order = "bysource"
# debug: keep rst files
autoapi_keep_files = False
autoapi_options= [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    "imported-members",
    "private-members",
    "special-members"
    'show-inheritance-diagram']

autoapi_ignore = ['*tests*']

autoapi_template_dir= '_templates/autoapi'

# -- custom auto_summary() macro ---------------------------------------------


def contains(seq, item):
    """Jinja2 custom test to check existence in a container.

    Example of use:
    {% set class_methods = methods|selectattr("properties", "contains", "classmethod") %}

    Related doc: https://jinja.palletsprojects.com/en/3.1.x/api/#custom-tests
    """
    return item in seq


import pprint
def prepare_jinja_env(jinja_env) -> None:
    """Add `contains` custom test to Jinja environment."""
    jinja_env.tests["contains"] = contains

    def print_attributes(obj):
        print(f"{obj.type}")

    jinja_env.filters["print_attributes"] = print_attributes



autoapi_prepare_jinja_env = prepare_jinja_env

# Custom role for labels used in auto_summary() tables.
rst_prolog = """
.. role:: summarylabel
"""

# Related custom CSS
html_css_files = [
    "css/label.css",
]

with open("api-filter.yml", 'r') as file:
    filters = yaml.safe_load(file)


def autoapi_skip_members(app, what, name, obj, skip, options):
    if (filters is not None) and (what in filters):
        _filters_what = filters[what]
        for incl in _filters_what:
            if incl[0] == '+':
                incl = incl[1:]
                if_match_skip = False
            elif incl[0] == '!':
                incl = incl[1:]
                if_match_skip = True
            else:
                if_match_skip = True
            if fnmatch.fnmatch(name, incl):
                return if_match_skip
        return False

    return False


def setup(app):
    app.connect("autoapi-skip-member", autoapi_skip_members)


