import pytest

import pywearable.utils


@pytest.mark.parametrize(
    "times, mean_time",
    [
        [["23:30", "00:00", "23:00"], "23:30"],
        [["23:30", "00:30"], "00:00"],
        [["21:15", "22:47"], "22:01"],
    ],
)
def test_mean_time(times, mean_time):
    computed_mean_time = pywearable.utils.mean_time(times)
    assert computed_mean_time == mean_time


@pytest.mark.parametrize(
    "times, earliest_bedtime",
    [
        [["19:40", "00:00", "00:50"], "19:40"],
        [["20:40", "00:00"], "20:40"],
        [["00:00", "00:01", "00:02"], "00:00"],
    ],
)
def test_get_earliest_bedtime(times, earliest_bedtime):
    computed_earliest_bedtime = pywearable.utils.get_earliest_bedtime(times)
    assert computed_earliest_bedtime == earliest_bedtime


@pytest.mark.parametrize(
    "times, earliest_wakeup_time",
    [
        [["07:30", "04:30", "04:29"], "04:29"],
        [["08:10", "06:50"], "06:50"],
        [["23:40", "07:00", "09:00"], "23:40"],
    ],
)
def test_get_earliest_bedtime(times, earliest_wakeup_time):
    computed_earliest_wakeup_time = pywearable.utils.get_earliest_wakeup_time(times)
    assert computed_earliest_wakeup_time == earliest_wakeup_time


@pytest.mark.parametrize(
    "times, latest_bedtime",
    [
        [["19:40", "00:00", "00:50"], "00:50"],
        [["20:40", "00:00"], "00:00"],
        [["00:00", "00:01", "00:02"], "00:02"],
    ],
)
def test_get_latest_bedtime(times, latest_bedtime):
    computed_latest_bedtime = pywearable.utils.get_latest_bedtime(times)
    assert computed_latest_bedtime == latest_bedtime


@pytest.mark.parametrize(
    "times, latest_wakeup_time",
    [
        [["07:30", "04:30", "04:29"], "07:30"],
        [["08:10", "06:50"], "08:10"],
        [["23:40", "07:00", "09:00"], "09:00"],
    ],
)
def test_get_latest_wakeup_time(times, latest_wakeup_time):
    computed_latest_wakeup_time = pywearable.utils.get_latest_wakeup_time(times)
    assert computed_latest_wakeup_time == latest_wakeup_time
