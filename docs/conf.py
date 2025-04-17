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

