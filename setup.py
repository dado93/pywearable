try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'A package to parse, analyse, and visualize Labfront data.',
    'author': 'Davide Marzorati',
    'url': 'https://github.com/dado93/pylabfront',
    'download_url': 'https://github.com/dado93/pylabfront',
    'author_email': 'davide.marzorati.93@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['pylabfront'],
    'scripts': [],
    'name': 'pylabfront'
}

setup(**config)