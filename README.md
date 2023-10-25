# pywearable
[![Documentation Status](https://readthedocs.org/projects/pywearable/badge/?version=latest)](https://pywearable.readthedocs.io/en/latest/?badge=latest)

Do you need to deal with wearable data? Then you are in the right place!
In this repository you will find a Python package that you can use to analyse all data collected with several data sources. At the moment, we support:
- [Labfront](https://labfront.com/)

The aim of this Python package is to offer a series of functions for the loading and analysis of the data. Furthermore, the aim is to build a command line interface (CLI) for data extraction and a web-based dashboard for:
- visualization of physiological data
- automatic analysis of data with feature extraction
- summary of data

## Installation
At this stage of development, the package is still not uploaded to PyPi, and thus can be only be installed through a local installation:

1. Clone the repository with `git clone git@github.com:dado93/pywearable.git`
2. `cd pywearable`
3. `git branch pywearable && git checkout pywearable`
4. `git pull origin pywearable`
3. `pip install --editable .`

## Usage
The package was designed to be used in the most straightforward way:

```
import pywearable.loader.labfront

_BASE_FOLDER = "..." # Path to folder with data downloaded from Labfront

labfront_loader = pywearable.loader.labfront.LabfrontLoader()
sleep_summaries = labfront_loader.load_garmin_connect_sleep_summary("user-01")
```

## Contributing

## Documentation
The format for documentation is [numpy-style](https://numpydoc.readthedocs.io/en/latest/format.html).
The documentation of the package can be built locally using [sphinx](www.sphinx-doc.org).
1. `cd docs`
2. `make html`
3. Open in your browser the file index.html that you can find in docs/_build/html