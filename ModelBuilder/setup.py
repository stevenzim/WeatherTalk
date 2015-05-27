try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Kaggle competition. Random acts of pizza.',
    'author': 'Steven Z, Can U, Bianca, Kevin & Tom',
    'url': 'https://github.com/903group6/Pizza',
    'download_url': 'https://github.com/903group6/Pizza',
    'author_email': 'szimme@essex.ac.uk',
    'version': '0.1',
    'install_requires': ['nose','nltk','sklearn'],
    'packages': ['raop'],
    'scripts': [],
    'name': 'group6raop'
}

setup(**config)
