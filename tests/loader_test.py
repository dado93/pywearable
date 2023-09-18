import datetime
from pathlib import Path

import pandas as pd
import pytest

import pylabfront.loader


@pytest.fixture
def loader():
    return pylabfront.loader.LabfrontLoader(Path("sample_data"))


def test_load_heart_rate_invalid_user_id(loader: pylabfront.loader.LabfrontLoader):
    with pytest.raises(ValueError):
        loader.load_garmin_connect_heart_rate("user-02")


@pytest.mark.parametrize("start_date", [None])
def test_load_heart_rate_is_df(loader: pylabfront.loader.LabfrontLoader, start_date):
    df = loader.load_garmin_connect_heart_rate("user-01")
    assert isinstance(df, pd.DataFrame)


def test_load_heart_rate_is_empty(loader: pylabfront.loader.LabfrontLoader):
    df = loader.load_garmin_connect_heart_rate(
        "user-01", end_date=datetime.datetime(1970, 1, 1)
    )
    assert len(df) == 0
