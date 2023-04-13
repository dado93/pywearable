# pylabfront

In this repository you will find a Python package that you can use to analyse data collected through [Labfront](https://labfront.com). Labfront is a platform that can be used to easily collect data from wearable devices. One of the key issues in using Labfront, in comparison to other platforms for physiological data collection and visualization (see: [Empatica Care](https://www.empatica.com/en-eu/care/)) is that it does not offer an appropriate dashboard for the visualization of data, and only shows you if the users have synced their smartwatches with the app. 

The aim of this Python package is to offer a command line interface (CLI) for data extraction and a web-based dashboard for:
- visualization of physiological data
- automatic analysis of data with feature extraction
- summary of data

## Installation
At this stage of development, the package can be installed only through `setup.py`:

1. Clone the repository with `git clone git@github.com:dado93/pylabfront.git`
2. `cd pylabfront`
3. `python setup.py` or, if you want to contribute to the project, `python setup.py develop`

## Documentation
The documentation of the package can be built locally using [sphinx](www.sphinx-doc.org)
1. `cd docs`
2. `make html`
3. Open in your browser the file index.html that you can find in docs/_build/html