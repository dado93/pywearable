import datetime
from pathlib import Path

import pandas as pd
import pytest

from pywearable.loader.labfront.loader import LabfrontLoader


@pytest.fixture
def loader(scope="session"):
    return LabfrontLoader(Path("sample_data"))


def test_get_user_ids(loader: LabfrontLoader):
    user_ids = loader.get_user_ids()
    assert type(user_ids) == list
    assert user_ids == ["user-01"]


def test_get_full_ids(loader):
    full_ids = loader.get_full_ids()
    assert type(full_ids) == list
    assert full_ids == ["user-01_6732ab82-077a-4bfd-8f89-246aba683253"]


def test_get_full_id(loader):
    full_id = loader.get_full_id("user-01")
    assert type(full_id) == str
    assert full_id == "user-01_6732ab82-077a-4bfd-8f89-246aba683253"


def test_get_user_id(loader):
    user_id = loader.get_user_id("user-01_6732ab82-077a-4bfd-8f89-246aba683253")
    assert type(user_id) == str
    assert user_id == "user-01"


def test_get_labfront_ids(loader: LabfrontLoader):
    labfront_id = loader.get_labfront_ids()
    assert type(labfront_id) == list
    assert labfront_id == ["6732ab82-077a-4bfd-8f89-246aba683253"]


def test_load_heart_rate_invalid_user_id(loader: LabfrontLoader):
    with pytest.raises(ValueError):
        loader.load_garmin_connect_heart_rate("user-02")


@pytest.mark.parametrize("start_date", [None])
def test_load_heart_rate_is_df(loader: LabfrontLoader, start_date):
    df = loader.load_garmin_connect_heart_rate("user-01")
    assert isinstance(df, pd.DataFrame)


def test_load_heart_rate_is_empty(loader: LabfrontLoader):
    df = loader.load_garmin_connect_heart_rate(
        "user-01", end_date=datetime.datetime(1970, 1, 1)
    )
    assert len(df) == 0
