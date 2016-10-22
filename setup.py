#from distutils.core import setup
#from distutils.extension import Extension
#from Cython.Build import cythonize
import numpy

from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("custmem.pyx"),
    include_dirs = [numpy.get_include()]
)
