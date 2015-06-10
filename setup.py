try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'MSc Thesis Code',
    'author': 'Steven Zimmerman',
    'url': 'https://github.com/stevenzim/WeatherTalk',
    'download_url': 'https://github.com/stevenzim/WeatherTalk',
    'author_email': 'szimme@essex.ac.uk',
    'version': '0.1',
    'install_requires': [],
    'packages': ['tests','tweetcollector','wxcollector','db','models'],
    'scripts': [],
    'name': 'wxtalk'
}

setup(**config)
