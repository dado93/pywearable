from io import StringIO
from pathlib import Path

import numpy as np
import numpy.testing
import pandas as pd
import pandas.testing
import pytest

import pywearable.constants
import pywearable.sleep


@pytest.fixture
def sleep_summary():
    sleep_summary = pd.read_csv(
        StringIO(
            """sleepSummaryId,calendarDate,timezoneOffsetInMs,unixTimestampInMs,isoDate,durationInMs,unmeasurableSleepInMs,deepSleepDurationInMs,lightSleepDurationInMs,remSleepInMs,awakeDurationInMs,overallSleepQualifier,overallSleepScore,validation,totalDurationQualifier,awakeCountQualifier,restlessnessQualifier,stressQualifier,remPercentageQualifier,lightPercentageQualifier,deepPercentageQualifier
x4c64722-64595538-6630,2023-05-09,7200000,1683576120000,2023-05-08T22:02:00.000+02:00,26160000,0,3900000,15480000,6780000,780000,GOOD,88,ENHANCED_FINAL,GOOD,GOOD,EXCELLENT,EXCELLENT,EXCELLENT,GOOD,FAIR
x4c64722-645ab9b4-55c8,2023-05-10,7200000,1683667380000,2023-05-09T23:23:00.000+02:00,21960000,0,3420000,12780000,5760000,120000,FAIR,79,ENHANCED_FINAL,FAIR,EXCELLENT,EXCELLENT,EXCELLENT,EXCELLENT,EXCELLENT,FAIR
x4c64722-645bf6d0-6888,2023-05-11,7200000,1683748560000,2023-05-10T21:56:00.000+02:00,26760000,0,6420000,12060000,8280000,480000,EXCELLENT,91,ENHANCED_FINAL,GOOD,EXCELLENT,EXCELLENT,EXCELLENT,GOOD,EXCELLENT,EXCELLENT
x4c64722-645d63f8-5c94,2023-05-12,7200000,1683842040000,2023-05-11T23:54:00.000+02:00,23700000,0,4260000,9600000,9240000,600000,FAIR,70,ENHANCED_FINAL,FAIR,EXCELLENT,EXCELLENT,FAIR,POOR,EXCELLENT,EXCELLENT
            """
        ),
        index_col=0,
    )
    sleep_summary[pywearable.constants._ISODATE_COL] = pd.to_datetime(
        sleep_summary[pywearable.constants._UNIXTIMESTAMP_IN_MS_COL]
        + sleep_summary[pywearable.constants._TIMEZONEOFFSET_IN_MS_COL],
        unit="ms",
        utc=True,
    ).dt.tz_localize(None)
    return sleep_summary


@pytest.fixture
def sleep_stages():
    sleep_stages = pd.read_csv(
        StringIO(
            """sleepSummaryId,timezoneOffsetInMs,unixTimestampInMs,isoDate,durationInMs,type
x4c64722-64595538-6630,7200000,1683576120000,2023-05-08T22:02:00.000+02:00,600000,light
x4c64722-64595538-6630,7200000,1683576720000,2023-05-08T22:12:00.000+02:00,960000,deep
x4c64722-64595538-6630,7200000,1683577680000,2023-05-08T22:28:00.000+02:00,60000,awake
x4c64722-64595538-6630,7200000,1683577740000,2023-05-08T22:29:00.000+02:00,600000,light
x4c64722-64595538-6630,7200000,1683578340000,2023-05-08T22:39:00.000+02:00,720000,deep
x4c64722-64595538-6630,7200000,1683579060000,2023-05-08T22:51:00.000+02:00,1800000,light
x4c64722-64595538-6630,7200000,1683580860000,2023-05-08T23:21:00.000+02:00,2700000,rem
x4c64722-64595538-6630,7200000,1683583560000,2023-05-09T00:06:00.000+02:00,840000,light
x4c64722-64595538-6630,7200000,1683584400000,2023-05-09T00:20:00.000+02:00,1080000,deep
x4c64722-64595538-6630,7200000,1683585480000,2023-05-09T00:38:00.000+02:00,2520000,light
x4c64722-64595538-6630,7200000,1683588000000,2023-05-09T01:20:00.000+02:00,1260000,rem
x4c64722-64595538-6630,7200000,1683589260000,2023-05-09T01:41:00.000+02:00,2760000,light
x4c64722-64595538-6630,7200000,1683592020000,2023-05-09T02:27:00.000+02:00,360000,deep
x4c64722-64595538-6630,7200000,1683592380000,2023-05-09T02:33:00.000+02:00,240000,light
x4c64722-64595538-6630,7200000,1683592620000,2023-05-09T02:37:00.000+02:00,660000,awake
x4c64722-64595538-6630,7200000,1683593280000,2023-05-09T02:48:00.000+02:00,1440000,light
x4c64722-64595538-6630,7200000,1683594720000,2023-05-09T03:12:00.000+02:00,780000,deep
x4c64722-64595538-6630,7200000,1683595500000,2023-05-09T03:25:00.000+02:00,540000,light
x4c64722-64595538-6630,7200000,1683596040000,2023-05-09T03:34:00.000+02:00,2820000,rem
x4c64722-64595538-6630,7200000,1683598860000,2023-05-09T04:21:00.000+02:00,960000,light
x4c64722-64595538-6630,7200000,1683599820000,2023-05-09T04:37:00.000+02:00,60000,awake
x4c64722-64595538-6630,7200000,1683599880000,2023-05-09T04:38:00.000+02:00,3180000,light
x4c64722-645bf6d0-6888,7200000,1683748560000,2023-05-10T21:56:00.000+02:00,3180000,deep
x4c64722-645d63f8-5c94,7200000,1683842040000,2023-05-11T23:54:00.000+02:00,600000,awake
x4c64722-645d63f8-5c94,7200000,1683842640000,2023-05-12T00:04:00.000+02:00,3000000,light
        """
        )
    )
    sleep_stages[pywearable.constants._ISODATE_COL] = pd.to_datetime(
        sleep_stages[pywearable.constants._UNIXTIMESTAMP_IN_MS_COL]
        + sleep_stages[pywearable.constants._TIMEZONEOFFSET_IN_MS_COL],
        unit="ms",
        utc=True,
    ).dt.tz_localize(None)
    return sleep_stages


def test_compute_sleep_score(sleep_summary):
    sleep_score = pywearable.sleep._compute_sleep_score(sleep_summary)
    assert type(sleep_score) == pd.Series
    numpy.testing.assert_array_equal(sleep_score.values, [88, 79, 91, 70])


def test_compute_sleep_efficiency(sleep_summary):
    sleep_efficiency = pywearable.sleep._compute_sleep_efficiency(sleep_summary)
    assert type(sleep_efficiency) == pd.Series
    numpy.testing.assert_allclose(
        sleep_efficiency, [97.1, 99.46, 98.24, 100.0], atol=0.1
    )


def test_compute_sleep_maintenance_efficiency(sleep_summary, sleep_stages):
    sleep_maintenance_efficiency = (
        pywearable.sleep._compute_sleep_maintenance_efficiency(
            sleep_summary, sleep_stages
        )
    )
    assert type(sleep_maintenance_efficiency) == pd.Series
    numpy.testing.assert_allclose(
        sleep_maintenance_efficiency, [97.1, np.nan, np.nan, np.nan], atol=0.1
    )


def test_compute_awakenings(sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame):
    sleep_awakenings = pywearable.sleep._compute_awakenings(sleep_summary, sleep_stages)
    assert type(sleep_awakenings) == pd.Series
    assert sleep_awakenings["x4c64722-64595538-6630"] == 3.0
    assert sleep_awakenings["x4c64722-645bf6d0-6888"] == 0.0
    assert np.isnan(sleep_awakenings["x4c64722-645ab9b4-55c8"])


def test_compute_latencies(sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame):
    sleep_latencies = pywearable.sleep._compute_latencies(sleep_summary, sleep_stages)
    assert type(sleep_latencies) == pd.DataFrame
    assert set(
        [
            pywearable.constants._SLEEP_STAGE_AWAKE_STAGE_VALUE,
            pywearable.constants._SLEEP_STAGE_DEEP_STAGE_VALUE,
            pywearable.constants._SLEEP_STAGE_REM_STAGE_VALUE,
            pywearable.constants._SLEEP_STAGE_LIGHT_STAGE_VALUE,
        ]
    ).issubset(sleep_latencies.columns)
    # Check latencies for a given sleep summary
    assert sleep_latencies.loc["x4c64722-64595538-6630", "deep"] == 10
    assert sleep_latencies.loc["x4c64722-64595538-6630", "awake"] == 26
    assert sleep_latencies.loc["x4c64722-64595538-6630", "light"] == 0
    assert sleep_latencies.loc["x4c64722-64595538-6630", "rem"] == 79
    # Check latencies for sleep summary with only one sleep stage
    assert sleep_latencies.loc["x4c64722-645bf6d0-6888", "deep"] == 0
    assert np.isnan(sleep_latencies.loc["x4c64722-645bf6d0-6888", "light"])
    # Check latencies for sleep summary with no sleep stages
    assert np.isnan(sleep_latencies.loc["x4c64722-645ab9b4-55c8", "rem"])
    assert np.isnan(sleep_latencies.loc["x4c64722-645ab9b4-55c8", "light"])


def test_compute_waso(sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame):
    waso = pywearable.sleep._compute_wake_after_sleep_onset(sleep_summary, sleep_stages)
    assert type(waso) == pd.Series
    # Check latencies for a given sleep summary
    assert waso.loc["x4c64722-64595538-6630"] == 13.0
    # Check latencies for sleep summary with no wake sleep stage
    assert waso.loc["x4c64722-645bf6d0-6888"] == 0
    # Check latencies for sleep summary with no sleep stages
    assert np.isnan(waso.loc["x4c64722-645ab9b4-55c8"])


def test_compute_sleep_onset_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
):
    sol = pywearable.sleep._compute_sleep_onset_latency(sleep_summary, sleep_stages)
    assert type(sol) == pd.Series
    # Check onset latency
    assert sol.loc["x4c64722-64595538-6630"] == 0.0
    assert sol.loc["x4c64722-645bf6d0-6888"] == 0.0
    assert sol.loc["x4c64722-645d63f8-5c94"] == 10.0
    # Check onset latency for sleep summary with no sleep stages
    assert np.isnan(sol.loc["x4c64722-645ab9b4-55c8"])


def test_compute_sleep_period_time(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
):
    sol = pywearable.sleep._compute_sleep_period_time(sleep_summary, sleep_stages)
    assert type(sol) == pd.Series
    # Check sleep onset latency for given sleep summaries
    assert sol.loc["x4c64722-64595538-6630"] == 449.0
    assert sol.loc["x4c64722-645bf6d0-6888"] == 53.0
    # Check sleep period time for sleep summary with first stage as awake
    assert sol.loc["x4c64722-645d63f8-5c94"] == 50.0
    # Check sleep period time for sleep summary with no sleep stages
    assert np.isnan(sol.loc["x4c64722-645ab9b4-55c8"])


def test_compute_unmeasurable_duration(sleep_summary: pd.DataFrame):
    unmeasurable_duration = pywearable.sleep._compute_unmeasurable_duration(
        sleep_summary, sleep_stages
    )
    assert type(unmeasurable_duration) == pd.Series
    # Check sleep onset latency for given sleep summaries
    assert unmeasurable_duration.loc["x4c64722-64595538-6630"] == 0.0
    assert unmeasurable_duration.loc["x4c64722-645bf6d0-6888"] == 0.0


def test_compute_stage_count(sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame):
    counts = pywearable.sleep._compute_stage_count(sleep_summary, sleep_stages)
    assert type(counts) == pd.DataFrame
    assert counts.loc["x4c64722-64595538-6630", "light"] == 11.0
    assert counts.loc["x4c64722-64595538-6630", "deep"] == 5.0
    assert counts.loc["x4c64722-64595538-6630", "awake"] == 3.0
    assert np.isnan(counts.loc["x4c64722-645ab9b4-55c8", "deep"])
    assert counts.loc["x4c64722-645bf6d0-6888", "deep"] == 1.0
    assert counts.loc["x4c64722-645d63f8-5c94", "light"] == 1.0
    assert counts.loc["x4c64722-645d63f8-5c94", "rem"] == 0.0
