try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Get and Process Daily Climate Reports from NWS',
    'author': 'Steven Zimmerman',
    'url': 'www.none.com',
    'download_url': 'www.none.com',
    'author_email': 'steven@somewhere.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['climReport'],
    'scripts': [],
    'name': 'projectname'
}

setup(**config)