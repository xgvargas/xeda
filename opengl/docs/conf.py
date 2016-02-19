#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Xeda documentation build configuration file, created by
# sphinx-quickstart on Thu Feb 11 20:18:46 2016.
#

import sys
import os
from recommonmark.parser import CommonMarkParser
sys.path.insert(0, os.path.abspath('..'))


# version

project = 'Xeda'
copyright = '2016, Gustavo Vargas'
author = 'Gustavo Vargas'
version = '0.1'
release = '0.1.0'


# Modules

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    ]


# Files

templates_path = ['_templates']
exclude_patterns = ['_build', '*_ui.rst']
# source_suffix = '.rst'
source_suffix = ['.rst', '.md']
master_doc = 'index'


# General

language = None
add_function_parentheses = False
add_module_names = True
show_authors = False
todo_include_todos = True
pygments_style = 'sphinx'
#modindex_common_prefix = []
source_parsers = {'.md': CommonMarkParser}


# HTML

#html_logo = None
#html_favicon = None
html_theme = 'sphinx_rtd_theme'
#html_theme_options = {}
#html_theme_path = []
html_static_path = ['_static']
#html_extra_path = []
html_use_smartypants = True
html_show_sourcelink = False
html_show_sphinx = True
htmlhelp_basename = 'Xedadoc'
#html_title = None
#html_short_title = None
#html_sidebars = {}
#html_additional_pages = {}
#html_show_copyright = True
# html_use_opensearch = 'http://meu-link.com'


# autodoc

autodoc_member_order = 'groupwise'
autoclass_content = 'both'
autodoc_default_flags = [
    'members',
    # 'private-members',
    # 'special-members',
    'undoc-members',
    'show-inheritance',
    ]
