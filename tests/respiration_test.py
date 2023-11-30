import datetime
import os

import pandas as pd
import pytest

import pywearable.constants
import pywearable.loader
import pywearable.respiration

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
MOCK_VALUES_DIR = os.path.join(CURRENT_DIR, "mock_values")
PULSE_OX_USER_ID = "01"


@pytest.fixture
def pulse_ox():
    """
    pytest.fixture that returns pulse ox data in the
    format required by pywearable.
    """
    pulse_ox_file = os.path.join(MOCK_VALUES_DIR, "pulse_ox.csv")
    pulse_ox = pd.read_csv(pulse_ox_file)
    pulse_ox[pywearable.constants._ISODATE_COL] = pd.to_datetime(
        pulse_ox[pywearable.constants._UNIXTIMESTAMP_IN_MS_COL]
        + pulse_ox[pywearable.constants._TIMEZONEOFFSET_IN_MS_COL],
        unit="ms",
        utc=True,
    ).dt.tz_localize(None)
    pulse_ox[pywearable.constants._CALENDAR_DATE_COL] = pd.to_datetime(
        pulse_ox[pywearable.constants._CALENDAR_DATE_COL], format="%Y-%m-%d"
    ).dt.date
    return pulse_ox


@pytest.fixture()
def base_loader(mocker, pulse_ox):
    """
    Fixture that returns a BaseLoader with mock values
    for the load_sleep_summary and load_sleep_stage
    functions. The value returned by these functions
    are specified by the sleep_summary and
    sleep_stages fixtures.
    """
    loader = pywearable.loader.BaseLoader()
    mocker.patch(
        "pywearable.loader.BaseLoader.load_pulse_ox",
        return_value=pulse_ox,
    )
    mocker.patch(
        "pywearable.loader.BaseLoader.get_user_ids",
        return_value=[PULSE_OX_USER_ID],
    )
    return loader


def test_mean_rest_pulse_ox(base_loader):
    mean_rest_pulse_ox = pywearable.respiration.get_mean_rest_pulse_ox(base_loader)
    assert type(mean_rest_pulse_ox) == dict
    assert PULSE_OX_USER_ID in mean_rest_pulse_ox.keys()
    assert (
        pywearable.respiration._RESPIRATION_METRIC_MEAN_PULSE_OX
        in mean_rest_pulse_ox[PULSE_OX_USER_ID].keys()
    )
