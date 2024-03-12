""""
This test module is designed to test all the functions
related to the cardiac.py module.
"""

import pandas as pd
import pytest

import pywearable.cardiac

#############################################
#          Heart Rate Statistics            #
#############################################


def test_get_average_heart_rate(base_loader):
    average_hr = pywearable.cardiac.get_avg_heart_rate(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(average_hr) is pd.Series
    assert type(average_hr.index) is pd.MultiIndex
    assert average_hr.name == pywearable.cardiac._CARDIAC_METRIC_AVERAGE_HEART_RATE
    assert "user-01" in average_hr.index.get_level_values("user")


def test_get_maximum_heart_rate(base_loader):
    max_hr = pywearable.cardiac.get_max_heart_rate(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(max_hr) is pd.Series
    assert type(max_hr.index) is pd.MultiIndex
    assert max_hr.name == pywearable.cardiac._CARDIAC_METRIC_MAXIMUM_HEART_RATE
    assert "user-01" in max_hr.index.get_level_values("user")


def test_get_rest_heart_rate(base_loader):
    rest_hr = pywearable.cardiac.get_rest_heart_rate(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(rest_hr) is pd.Series
    assert type(rest_hr.index) is pd.MultiIndex
    assert rest_hr.name == pywearable.cardiac._CARDIAC_METRIC_RESTING_HEART_RATE
    assert "user-01" in rest_hr.index.get_level_values("user")


#############################################
#     Heart Rate Variability Statistics     #
#############################################
def test_get_hf(base_loader):
    night_hf = pywearable.cardiac.get_night_hf(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(night_hf) is pd.Series
    assert type(night_hf.index) is pd.MultiIndex
    assert night_hf.name == pywearable.cardiac._CARDIAC_METRIC_HIGH_FREQUENCY
    assert "user-01" in night_hf.index.get_level_values("user")
