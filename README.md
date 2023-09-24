# pylabfront
[![Documentation Status](https://readthedocs.org/projects/pylabfront/badge/?version=latest)](https://pylabfront.readthedocs.io/en/latest/?badge=latest)

Do you need to deal with wearable data collected with [Labfront](https://labfront.com)? Then you are in the right place!
In this repository you will find a Python package that you can use to analyse all data collected through Labfront, which is a platform that can be used to easily collect data from wearable devices. One of the key issues in using Labfront, in comparison to other platforms for physiological data collection and visualization (see: [Empatica Care](https://www.empatica.com/en-eu/care/)) is that it does not offer an appropriate dashboard for the visualization of data, and only shows you if the users have synced their smartwatches with the app. 

The aim of this Python package is to offer a series of functions for the loading and analysis of the data. Furthermore, the aim is to build a command line interface (CLI) for data extraction and a web-based dashboard for:
- visualization of physiological data
- automatic analysis of data with feature extraction
- summary of data

## Installation
At this stage of development, the package is still not uploaded to PyPi, and thus can be only be installed through a local installation:

1. Clone the repository with `git clone git@github.com:dado93/pylabfront.git`
2. `cd pylabfront`
3. `pip install --editable .`

## Usage
The package was designed to be used in the most straightforward way:

```
import pylabfront.loader.LabfrontLoader

_BASE_FOLDER = "..." # Path to folder with data downloaded from Labfront

labfront_loader = pylabfront.loader.LabfrontLoader()
sleep_summaries = labfront_loader.load_garmin_connect_sleep_summary("user-01")
```

## Contributing

## Documentation
The format for documentation is [numpy-style](https://numpydoc.readthedocs.io/en/latest/format.html).
The documentation of the package can be built locally using [sphinx](www.sphinx-doc.org).
1. `cd docs`
2. `make html`
3. Open in your browser the file index.html that you can find in docs/_build/html