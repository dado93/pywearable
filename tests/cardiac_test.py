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
        loader=base_loader, user_id=["user-01"], return_df=True, return_multi_index=True
    )
    assert type(average_hr) is pd.Series
    assert type(average_hr.index) is pd.MultiIndex
    assert average_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_AVERAGE_HEART_RATE
    assert "user-01" in average_hr.index.get_level_values("user")


def test_get_average_heart_rate_kind(base_loader):
    average_hr = pywearable.cardiac.get_avg_heart_rate(
        loader=base_loader, user_id=["user-01"], return_df=True, return_multi_index=True
    )
    assert type(average_hr) is pd.Series
    assert type(average_hr.index) is pd.MultiIndex
    assert average_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_AVERAGE_HEART_RATE
    assert "user-01" in average_hr.index.get_level_values("user")


def test_get_maximum_heart_rate(base_loader):
    max_hr = pywearable.cardiac.get_max_heart_rate(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(max_hr) is pd.Series
    assert type(max_hr.index) is pd.MultiIndex
    assert max_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_MAXIMUM_HEART_RATE
    assert "user-01" in max_hr.index.get_level_values("user")


def test_get_rest_heart_rate(base_loader):
    rest_hr = pywearable.cardiac.get_rest_heart_rate(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(rest_hr) is pd.Series
    assert type(rest_hr.index) is pd.MultiIndex
    assert rest_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_RESTING_HEART_RATE
    assert "user-01" in rest_hr.index.get_level_values("user")


def test_get_minimum_heart_rate(base_loader):
    min_hr = pywearable.cardiac.get_min_heart_rate(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(min_hr) is pd.Series
    assert type(min_hr.index) is pd.MultiIndex
    assert min_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_MINIMUM_HEART_RATE
    assert "user-01" in min_hr.index.get_level_values("user")


def test_get_heart_rate_statistics_error(base_loader):
    ################################################
    #               Rest Heart Rate                #
    ################################################
    with pytest.raises(ValueError):
        pywearable.cardiac.get_heart_rate_statistics(
            loader=base_loader,
            statistic="another metric",
            user_id="user-01",
            return_df=True,
            return_multi_index=True,
        )


def test_get_heart_rate_statistics(base_loader):
    ################################################
    #               Rest Heart Rate                #
    ################################################
    rest_hr = pywearable.cardiac.get_heart_rate_statistics(
        loader=base_loader,
        statistic=pywearable.cardiac._CARDIAC_STATISTIC_RESTING_HEART_RATE,
        user_id="user-01",
        return_df=True,
        return_multi_index=True,
    )
    assert type(rest_hr) is pd.Series
    assert type(rest_hr.index) is pd.MultiIndex
    assert rest_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_RESTING_HEART_RATE
    assert "user-01" in rest_hr.index.get_level_values("user")

    ################################################
    #             Average Heart Rate               #
    ################################################
    avg_hr = pywearable.cardiac.get_heart_rate_statistics(
        loader=base_loader,
        statistic=pywearable.cardiac._CARDIAC_STATISTIC_AVERAGE_HEART_RATE,
        user_id="user-01",
        return_df=True,
        return_multi_index=True,
    )
    assert type(avg_hr) is pd.Series
    assert type(avg_hr.index) is pd.MultiIndex
    assert avg_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_AVERAGE_HEART_RATE
    assert "user-01" in avg_hr.index.get_level_values("user")

    ################################################
    #             Minimum Heart Rate               #
    ################################################
    min_hr = pywearable.cardiac.get_heart_rate_statistics(
        loader=base_loader,
        statistic=pywearable.cardiac._CARDIAC_STATISTIC_MINIMUM_HEART_RATE,
        user_id="user-01",
        return_df=True,
        return_multi_index=True,
    )
    assert type(min_hr) is pd.Series
    assert type(min_hr.index) is pd.MultiIndex
    assert min_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_MINIMUM_HEART_RATE
    assert "user-01" in min_hr.index.get_level_values("user")

    ################################################
    #             Maximum Heart Rate               #
    ################################################
    max_hr = pywearable.cardiac.get_heart_rate_statistics(
        loader=base_loader,
        statistic=pywearable.cardiac._CARDIAC_STATISTIC_MAXIMUM_HEART_RATE,
        user_id="user-01",
        return_df=True,
        return_multi_index=True,
    )
    assert type(max_hr) is pd.Series
    assert type(max_hr.index) is pd.MultiIndex
    assert max_hr.name == pywearable.cardiac._CARDIAC_STATISTIC_MAXIMUM_HEART_RATE
    assert "user-01" in max_hr.index.get_level_values("user")

    hr_df = pywearable.cardiac.get_heart_rate_statistics(
        loader=base_loader,
        statistic=[
            pywearable.cardiac._CARDIAC_STATISTIC_MAXIMUM_HEART_RATE,
            pywearable.cardiac._CARDIAC_STATISTIC_MINIMUM_HEART_RATE,
        ],
        user_id="user-01",
        return_df=True,
        return_multi_index=True,
    )
    assert type(hr_df) is pd.DataFrame
    assert type(hr_df.index) is pd.MultiIndex
    assert pywearable.cardiac._CARDIAC_STATISTIC_MAXIMUM_HEART_RATE in hr_df.columns
    assert pywearable.cardiac._CARDIAC_STATISTIC_MINIMUM_HEART_RATE in hr_df.columns
    assert "user-01" in max_hr.index.get_level_values("user")


#############################################
#     Heart Rate Variability Statistics     #
#############################################
def test_get_hf(base_loader):
    night_hf = pywearable.cardiac.get_night_hf(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(night_hf) is pd.Series
    assert type(night_hf.index) is pd.MultiIndex
    assert night_hf.name == pywearable.cardiac._CARDIAC_STATISTIC_HIGH_FREQUENCY
    assert "user-01" in night_hf.index.get_level_values("user")


def test_get_lf(base_loader):
    night_lf = pywearable.cardiac.get_night_lf(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(night_lf) is pd.Series
    assert type(night_lf.index) is pd.MultiIndex
    assert night_lf.name == pywearable.cardiac._CARDIAC_STATISTIC_LOW_FREQUENCY
    assert "user-01" in night_lf.index.get_level_values("user")


def test_get_lfhf(base_loader):
    night_lfhf = pywearable.cardiac.get_night_lfhf(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(night_lfhf) is pd.Series
    assert type(night_lfhf.index) is pd.MultiIndex
    assert (
        night_lfhf.name
        == pywearable.cardiac._CARDIAC_STATISTIC_LOW_HIGH_FREQUENCY_RATIO
    )
    assert "user-01" in night_lfhf.index.get_level_values("user")


def test_get_rmssd(base_loader):
    night_rmssd = pywearable.cardiac.get_night_rmssd(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(night_rmssd) is pd.Series
    assert type(night_rmssd.index) is pd.MultiIndex
    assert (
        night_rmssd.name
        == pywearable.cardiac._CARDIAC_STATISTIC_ROOT_MEAN_SQUARED_SUCCESSIVE_DIFFERENCES
    )
    assert "user-01" in night_rmssd.index.get_level_values("user")


def test_get_sdnn(base_loader):
    night_sdnn = pywearable.cardiac.get_night_sdnn(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(night_sdnn) is pd.Series
    assert type(night_sdnn.index) is pd.MultiIndex
    assert (
        night_sdnn.name
        == pywearable.cardiac._CARDIAC_STATISTIC_STANDARD_DEVIATION_NORMAL_TO_NORMAL
    )
    assert "user-01" in night_sdnn.index.get_level_values("user")


def test_heart_rate_variability_statistics(base_loader):
    for statistic in pywearable.cardiac._CARDIAC_HRV_STATISTICS:
        hrv_statistic = pywearable.cardiac.get_hrv_statistic(
            loader=base_loader,
            statistic=statistic,
            user_id="user-01",
            return_df=True,
            return_multi_index=True,
        )
        assert type(hrv_statistic) is pd.Series
        assert type(hrv_statistic.index) is pd.MultiIndex
        assert "user-01" in hrv_statistic.index.get_level_values("user")
        assert hrv_statistic.name == statistic


def test_heart_rate_variability_statistics(base_loader):
    hrv_statistics = pywearable.cardiac.get_hrv_statistics(
        loader=base_loader, user_id="user-01", return_df=True, return_multi_index=True
    )
    assert type(hrv_statistics) is pd.DataFrame
    assert type(hrv_statistics.index) is pd.MultiIndex
    assert "user-01" in hrv_statistics.index.get_level_values("user")
    assert set(pywearable.cardiac._CARDIAC_HRV_STATISTICS).issubset(
        hrv_statistics.columns
    )
