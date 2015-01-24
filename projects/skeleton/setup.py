try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My Test Project',
    'author': 'Steven Zimmerman',
    'url': 'www.none.com',
    'download_url': 'www.none.com',
    'author_email': 'steven@somewhere.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'projectname'
}

setup(**config)