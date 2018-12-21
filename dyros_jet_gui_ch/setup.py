#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup
  
d = generate_distutils_setup(
    packages=['dyros_jet_gui_ch'],
    package_dir={'': 'src'},
    scripts=['scripts/dyros_jet_gui_ch.py']
)

setup(**d)
