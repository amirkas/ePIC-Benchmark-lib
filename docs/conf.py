import os
import sys

import requests

sys.path.insert(0, os.path.abspath('../'))

import ePIC_benchmarks

extensions = [
    'nbshpinx',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.linkcode',
    'sphinx.ext.napoleon'
]

source_suffix = '.rst'

master_doc = 'index'

project = 'ePIC Benchmarks'
copyright = '2024-2025, ePIC Benchmarks'
author = 'Amir Abdou'

autosummary_generate = True
