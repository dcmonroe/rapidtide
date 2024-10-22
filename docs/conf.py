#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rapidtide documentation build configuration file, created by
# sphinx-quickstart on Thu Jun 16 15:27:19 2016.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import os
import sys
from datetime import datetime

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(".."))
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("sphinxext"))
sys.path.insert(0, os.path.abspath("../rapidtide"))
print(sys.path)

import versioneer

current_dir = os.getcwd()
os.chdir(os.path.dirname(versioneer.__file__))

versioneer.VCS = "git"
versioneer.versionfile_source = "../rapidtide/_version.py"
versioneer.versionfile_build = "../rapidtide/_version.py"
versioneer.tag_prefix = "rapidtide-"  # tags are like rapidtide-1.2.0
versioneer.parentdir_prefix = ".."

__version = versioneer.get_version().replace(".dirty", "")

del versioneer
os.chdir(current_dir)

on_rtd = os.environ.get("READTHEDOCS", None) == "True"


from github_link import make_linkcode_resolve

import rapidtide

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'
pdf_break_level = 2

# generate autosummary even if no references
autosummary_generate = True
autodoc_default_flags = ["members", "inherited-members"]
add_module_names = True

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxarg.ext",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "myst_parser",
    "numpydoc",
    "sphinx.ext.ifconfig",
    "sphinx.ext.linkcode",
    "sphinx_gallery.gen_gallery",
    "sphinxcontrib.bibtex",
]

from distutils.version import LooseVersion

import sphinx

if LooseVersion(sphinx.__version__) < LooseVersion("1.4"):
    extensions.append("sphinx.ext.pngmath")
else:
    extensions.append("sphinx.ext.imgmath")

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = [".rst"]

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "rapidtide"
copyright = "2016-" + datetime.today().strftime("%Y") + ", Blaise Frederick"
author = "Blaise Frederick"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
import rapidtide.util as tide_util

version = tide_util.version()[0].replace("v", "").split("+")[0]
# The full version, including alpha/beta/rc tags.
release = version

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
# html_theme = 'sphinxdoc'
import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.
# "<project> v<release> documentation" by default.
# html_title = 'rapidtide v0.1.0'

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# https://github.com/rtfd/sphinx_rtd_theme/issues/117
def setup(app):
    app.add_css_file("theme_overrides.css")


# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not None, a 'Last updated on:' timestamp is inserted at every page
# bottom, using the given strftime format.
# The empty string is equivalent to '%b %d, %Y'.
# html_last_updated_fmt = None

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'h', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'r', 'sv', 'tr', 'zh'
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# 'ja' uses this config value.
# 'zh' user can custom change `jieba` dictionary path.
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
# html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = "rapidtidedoc"

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
    # Latex figure (float) alignment
    #'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        master_doc,
        "rapidtide.tex",
        "rapidtide Documentation",
        "Blaise Frederick",
        "manual",
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "rapidtide", "rapidtide Documentation", [author], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "rapidtide",
        "rapidtide Documentation",
        author,
        "rapidtide",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

# The following is used by sphinx.ext.linkcode to provide links to github
linkcode_resolve = make_linkcode_resolve(
    "rapidtide",
    "https://github.com/bbfrederick/" "rapidtide/blob/{revision}/" "{package}/{path}#L{lineno}",
)

# -----------------------------------------------------------------------------
# intersphinx
# -----------------------------------------------------------------------------
_python_version_str = f"{sys.version_info.major}.{sys.version_info.minor}"
_python_doc_base = f"https://docs.python.org/{_python_version_str}"
intersphinx_mapping = {
    "python": (_python_doc_base, None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": (
        "https://docs.scipy.org/doc/scipy/reference",
        (None, "./_intersphinx/scipy-objects.inv"),
    ),
    "matplotlib": (
        "https://matplotlib.org/stable/",
        (None, "https://matplotlib.org/stable/objects.inv"),
    ),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "nibabel": ("https://nipy.org/nibabel/", None),
    "nilearn": ("http://nilearn.github.io/stable/", None),
    "scikit-learn": ("http://scikit-learn.org/stable", None),
}

# -----------------------------------------------------------------------------
# sphinxcontrib-bibtex
# -----------------------------------------------------------------------------
bibtex_bibfiles = ["references.bib"]
bibtex_style = "unsrt"
bibtex_reference_style = "author_year"
bibtex_footbibliography_header = ""

# -----------------------------------------------------------------------------
# sphinx gallery
# -----------------------------------------------------------------------------
sphinx_gallery_conf = {
    # path to your examples scripts
    "examples_dirs": "../examples",
    # path where to save gallery generated examples
    "gallery_dirs": "auto_examples",
    "backreferences_dir": "_build/gen_modules/backreferences",
    # Modules for which function level galleries are created.  In
    # this case sphinx_gallery and numpy in a tuple of strings.
    "doc_module": ("rapidtide"),
}
