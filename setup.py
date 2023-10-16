try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    "description": "A package to parse, analyse, and visualize wearable data.",
    "author": "Davide Marzorati",
    "url": "https://github.com/dado93/pywearable",
    "download_url": "https://github.com/dado93/pywearable",
    "author_email": "davide.marzorati.93@gmail.com",
    "version": "0.1",
    "install_requires": ["pandas"],
    "packages": ["pywearable"],
    "scripts": [],
    "name": "pywearable",
    "python_requires": ">=3.9.0",
}

setup(**config)
