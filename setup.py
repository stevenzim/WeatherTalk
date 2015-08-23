try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'MSc Thesis Code',
    'author': 'Steven E. Zimmerman',
    'url': 'https://github.com/stevenzim/WeatherTalk',
    'download_url': 'https://github.com/stevenzim/WeatherTalk',
    'author_email': 'szimme@essex.ac.uk',
    'version': '1.0',
    'install_requires': ['TwitterAPI','sklearn','numpy','nltk','psycopg2'],
    'packages': ['tests','tweetcollector','wxcollector','db','model'],
    'name': 'WeatherTalk'
}

setup(**config)
