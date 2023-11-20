import datetime

import numpy as np
import pandas as pd
import pytest

import pywearable.constants as constants
from pywearable.loader import LifeSnapsLoader

# TODO We need to mock the MongoDB to run the tests


@pytest.fixture(scope="session")
def lifesnaps_loader():
    return LifeSnapsLoader()


def test_load_breq_questionnaire(lifesnaps_loader: LifeSnapsLoader):
    user_id = "621e2efa67b776a2409dd1c3"
    start_date = datetime.datetime(2021, 5, 26)
    end_date = datetime.datetime(2021, 6, 11)
    breq_questionnaire = lifesnaps_loader.load_breq_questionnaire(
        user_id, start_date, end_date
    )
    assert isinstance(breq_questionnaire, pd.DataFrame)
    assert {
        constants._UNIXTIMESTAMP_IN_MS_COL,
        constants._TIMEZONEOFFSET_IN_MS_COL,
        constants._ISODATE_COL,
    }.issubset(breq_questionnaire.columns)


def test_load_daily_spo2(lifesnaps_loader: LifeSnapsLoader):
    """
    Objective: Test the loading of daily spo2 data from
    LifeSnaps dataset.
    ---------------------------------------------------
    Checks:
    - returned variabile is a pd.DataFrame
    - pd.DataFrame contains the required columns
    - pd.DataFrame contains data of the requested timeframe

    """
    user_id = "621e2efa67b776a2409dd1c3"
    start_date = datetime.datetime(2021, 5, 26)
    end_date = datetime.datetime(2021, 6, 11)
    daily_spo2 = lifesnaps_loader.load_daily_spo2(user_id, start_date, end_date)
    assert isinstance(daily_spo2, pd.DataFrame)
    assert {
        constants._UNIXTIMESTAMP_IN_MS_COL,
        "average_value",
        "lower_bound",
        "upper_bound",
    }.issubset(daily_spo2.columns)
