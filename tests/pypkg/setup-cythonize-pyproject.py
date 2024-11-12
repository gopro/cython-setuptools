from setuptools import setup
from cython_setuptools import create_extensions

setup(ext_modules=create_extensions(__file__, cythonize=True))
