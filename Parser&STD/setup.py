from setuptools import setup, find_packages

setup(
    name='unam.fi.compilers.g5.08',
    version='1.0.0',
    package_dir={'': 'Parser&STD'},  # Indica dónde buscar
    packages=find_packages(where='Parser&STD'),
)