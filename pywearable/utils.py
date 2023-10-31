"""
This module contains utility functions that don't directly load/compute metrics.
"""

import datetime
import time
from cmath import phase, rect
from math import degrees, radians
from typing import Union

import dateutil.parser
import hrvanalysis
import numpy as np
import pandas as pd

from .loader.base import BaseLoader
from . import constants

_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = "lastSampleUnixTimestampInMs"
_LABFRONT_QUESTIONNAIRE_STRING = "questionnaire"
_LABFRONT_TODO_STRING = "todo"
_MS_TO_DAY_CONVERSION = 1000 * 60 * 60 * 24


def check_date(
    date: Union[datetime.datetime, datetime.date, str, None]
) -> datetime.datetime:
    """Convert date to :class:`datetime.datetime` format

    Parameters
    ----------
    date : datetime.datetime or datetime.date or str or None
        Date to be converted

    Returns
    -------
    datetime.datetime
        Converted date.

    Raises
    ------
    ValueError
        If ``date`` is not of valid format.
    """
    # Check dates and times
    if isinstance(date, str):
        return dateutil.parser.parse(date)
    elif type(date) == datetime.date:
        return datetime.datetime.combine(date, datetime.time())
    elif date is None:
        return None
    elif type(date) == datetime.datetime:
        return date
    else:
        raise ValueError(f"{type(date)} is not valid.")


def get_user_ids(loader: "BaseLoader", user_id: Union[str, list]):
    """Returns user ids in the appropriate format required by pywearable functions

    Parameters
    ----------
    loader : :class:`BaseLoader`
        An instance of a data loader
    user_id : :class:`str` or :class:`list`
        The id(s) of the user(s9) of interest

    Returns
    -------
    list
        List of all the full user ids of interest.
    """
    if user_id == "all":
        user_id = loader.get_full_ids()

    elif isinstance(user_id, str):
        user_id = loader.get_full_id(user_id)
        user_id = [user_id]

    elif not isinstance(user_id, list):
        raise TypeError("user_id has to be a list.")

    return user_id


def get_summary(loader: "BaseLoader", comparison_date=time.time()):
    """Returns a general summary of the latest update of every metric for every participant

    Args:
        loader (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        comparison_date (float): unix time in seconds for comparison. Defaults to the current unix time.

    Returns:
        DataFrame: general summary of the number of full days since metrics were updated for all participants.
        Entries are NaN if the metric has never been registered for the participant.
    """

    available_metrics = set(loader.get_available_metrics())
    available_metrics.discard("todo")
    available_metrics.discard("questionnaire")
    available_metrics = sorted(list(available_metrics))
    available_questionnaires = loader.get_available_questionnaires()
    available_todos = loader.get_available_todos()

    features_dictionary = {}

    for participant_id in sorted(loader.get_user_ids()):
        full_participant_id = loader.get_full_id(participant_id)
        features_dictionary[participant_id] = {}
        participant_metrics = loader.get_available_metrics([participant_id])
        participant_questionnaires = loader.get_available_questionnaires(
            [participant_id]
        )
        participant_todos = loader.get_available_todos([participant_id])

        for metric in available_metrics:
            if metric not in participant_metrics:
                features_dictionary[participant_id][metric] = None
            else:  # figure out how many days since the last update
                last_unix_times = [
                    v[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY]
                    for v in loader.data_dictionary[full_participant_id][
                        metric
                    ].values()
                ]
                number_of_days_since_update = (
                    comparison_date * 1000 - max(last_unix_times)
                ) // _MS_TO_DAY_CONVERSION
                features_dictionary[participant_id][
                    metric
                ] = number_of_days_since_update

        for questionnaire in available_questionnaires:
            if questionnaire not in participant_questionnaires:
                features_dictionary[participant_id][questionnaire] = None
            else:
                last_unix_times = [
                    v[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY]
                    for v in loader.data_dictionary[full_participant_id][
                        _LABFRONT_QUESTIONNAIRE_STRING
                    ][questionnaire].values()
                ]
                number_of_days_since_update = (
                    comparison_date * 1000 - max(last_unix_times)
                ) // _MS_TO_DAY_CONVERSION
                features_dictionary[participant_id][
                    questionnaire
                ] = number_of_days_since_update

        for todo in available_todos:
            if todo not in participant_todos:
                features_dictionary[participant_id][todo] = None
            else:
                last_unix_times = [
                    v[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY]
                    for v in loader.data_dictionary[full_participant_id][
                        _LABFRONT_TODO_STRING
                    ][todo].values()
                ]
                number_of_days_since_update = (
                    comparison_date * 1000 - max(last_unix_times)
                ) // _MS_TO_DAY_CONVERSION
                features_dictionary[participant_id][todo] = number_of_days_since_update

    df = pd.DataFrame(features_dictionary)
    return df.T


def is_task_repeatable(file_path):
    """Returns boolean indication of questionnaire/todo repeatability

    Args:
        file_path (Path): path to the folder of the questionnaire/todo csv files

    Returns:
        bool: Indication if the questionnaire/todo is repeatable
    """
    csv_path = list((file_path).iterdir())[0]
    with open(csv_path, "r") as f:
        for _ in range(5):
            line = f.readline().split(",")
    return line[7] == "true"


def is_weekend(day):
    """Indication if the day considered is either a Saturday or Sunday.

    Args:
        day (datetime): date of interest.

    Returns:
        bool: True/False depending if day is a weekend day or not.
    """
    return day.weekday() in [5, 6]


def find_nearest_timestamp(timestamp, timestamp_array):
    """Finds the closest time between a set of timestamps to a given timestamp.

    Args:
        timestamp (datetime): Date of interest, of which to find closest timestamp.
        timestamp_array (datetime): Array of datetimes

    Returns:
        datetime: Closest datetime in timestamp_array to timestamp
    """
    return min(timestamp_array, key=lambda x: abs(x - timestamp))


def trend_analysis(
    data_dict : dict,
    start_date : datetime.datetime,
    end_date : datetime.datetime,
    ma_kind : str ="normal",
    baseline_periods : int = 7,
    min_periods_baseline : int = 3,
    normal_range_periods : int = 30,
    min_periods_normal_range : int = 20,
    std_multiplier : float = 1.,
):
    """Performs trend analysis on daily data for a pre-loaded metric.

    Parameters
    ----------
    data_dict : class: dict
        Dictionary with dates as keys and daily metric data as values.
    start_date : :class:`datetime.datetime`
        Start date of the period of interest
    end_date : :class:`datetime.datetime`
        End date of the period of interest (inclusive)
    ma_kind : :class: str, optional
        type of moving average to compute, can be either normal or exponential, by default "normal"
    baseline_periods : int, optional
        number of period values to be used for the computation of the rolling baseline, by default 7 (MA7)
    min_periods_baseline : int, optional
        minimum number of period values needed for the baseline to be considered valid, by default 3
    normal_range_periods : int, optional
        number of period values to be used for the computation of the rolling normal range, by default 30
    min_periods_normal_range : int, optional
        minimum number of period values needed for the normal range to be considered valid, by default 20
    std_multiplier : int, optional
        multiplier of the standard deviation for the computation of lower and upper bounds of the normal range, by default 1

    Returns
    -------
    pandas.DataFrame
    including daily metric, baseline, and normal range params.
    """
    idx = pd.date_range(start_date, end_date)
    s = pd.Series(data_dict)
    s.index = pd.DatetimeIndex(s.index)
    s = s.reindex(idx, fill_value=None)
    df = pd.DataFrame(s, columns=["metric"])
    if ma_kind == "normal":
        df["BASELINE"] = df.metric.rolling(
            window=baseline_periods, min_periods=min_periods_baseline
        ).mean()
    elif ma_kind == "exponential":
        df["BASELINE"] = df.metric.ewm(
            span=baseline_periods, min_periods=min_periods_baseline
        ).mean()
    else:
        raise ValueError('Moving average kind can only be "normal" or "exponential"')
    df["NR_MEAN"] = df.metric.rolling(
        window=normal_range_periods, min_periods=min_periods_normal_range
    ).mean()
    df["NR_STD"] = df.metric.rolling(
        window=normal_range_periods, min_periods=min_periods_normal_range
    ).std()
    df["NR_LOWER_BOUND"] = df["NR_MEAN"] - std_multiplier * df["NR_STD"]
    df["NR_UPPER_BOUND"] = df["NR_MEAN"] + std_multiplier * df["NR_STD"]
    return df


def mean_angle(deg):
    return degrees(phase(sum(rect(1, radians(d)) for d in deg) / len(deg)))


def mean_time(times):
    t = (time.split(":") for time in times)
    seconds = ((int(m) * 60 + int(h) * 3600) for h, m in t)
    day = 24 * 60 * 60
    to_angles = [s * 360.0 / day for s in seconds]
    mean_as_angle = mean_angle(to_angles)
    mean_seconds = mean_as_angle * day / 360.0
    if mean_seconds < 0:
        mean_seconds += day
    h, m = divmod(mean_seconds, 3600)
    m, s = divmod(m, 60)
    return "%02i:%02i" % (h, m)


def filter_bbi(
    bbi,
    remove_outliers=True,
    remove_ectopic=True,
    verbose=False,
    low_rri=300,
    high_rri=2000,
    ectopic_method="malik",
    interpolation_method="linear",
):
    """Get filtered bbi data.

    This function returns bbi data filtered out from outliers and/or ectopic beats.

    Parameters
    ----------
    bbi : list
        series of beat to beat interval
    remove_outliers : bool, optional
        determines if outliers below ``low_rri`` and above ``high_rri`` should be filtered out, by default True
    remove_ectopic : bool, optional
        determines if ectopic beats should be removed from the bbi series, by default True
    verbose : bool, optional
        whether the function should print out data about the amount of outliers/ectopic beats removed, by default False
    low_rri : int, optional
        lower threshold for outlier detection, by default 300
    high_rri : int, optional
        upper threshold for outlier detection, by default 2000
    ectopic_method : str, optional
        method used to determine and filter out ectopic beats, by default "malik"
    interpolation_method : str, optional
        method used to interpolate missing values after the removal of outliers/ectopic beats, by default "linear"
    """
    if remove_outliers:
        bbi = hrvanalysis.remove_outliers(
            bbi, low_rri=low_rri, high_rri=high_rri, verbose=verbose
        )
        bbi = hrvanalysis.interpolate_nan_values(
            bbi, interpolation_method=interpolation_method
        )
    if remove_ectopic:
        bbi = hrvanalysis.remove_ectopic_beats(
            bbi, method=ectopic_method, verbose=verbose
        )
        bbi = hrvanalysis.interpolate_nan_values(
            bbi, interpolation_method=interpolation_method
        )
    return bbi


def filter_out_awake_bbi(loader, user, bbi_df, date, resolution=1):
    """Filters out night bbi data relative to periods where the user was awake

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user : class:`str`
        ID of the user for which bbi data has to be filtered.
    bbi_df : class:`pandas.DataFrame`
        DataFrame of bbi data
    date : class:`pandas.Timestamp`
        Timestamp of the date relative to the night in consideration.
    resolution : class:`int`
        Resolution of the hypnogram used to find awakening periods

    Returns
    -------
    pandas.DataFrame
    DataFrame in the same format of `bbi_df`, including only bbi data of periods when the participant is asleep.
    """
    # we get the hypnogram for that day
    hypnogram = loader.load_hypnogram(user_id = user,
                                     start_date = date,
                                     end_date= date,
                                     resolution=resolution)[date]
    hypnogram_start = hypnogram["start_time"]
    hypnogram_end = hypnogram["end_time"]
    hypnogram = hypnogram["values"]

    # stage differences
    hypnogram_diff = np.concatenate(
        [
            [0],
            np.diff(hypnogram)
        ]
    ) 
    # if there has been a negative change and the current stage is awake, then count it as awakening start
    awakening_starts = np.logical_and(hypnogram == 0, hypnogram_diff < 0)
    # if there has been a positive change and the previous stage was awake, then count it as awakening end
    awakening_ends = np.concatenate([[0],np.logical_and(hypnogram[:-1] == 0, hypnogram_diff[1:] > 0)])
    # get the indexes of starts and ends
    idx_starts = [idx for idx, start in enumerate(awakening_starts) if start]
    idx_ends = [idx for idx, end in enumerate(awakening_ends) if end]
    # based on the start of the sleep and the indexes of the awakenings, get the datetimes
    datetime_starts = [hypnogram_start + datetime.timedelta(minutes=idx*resolution) for idx in idx_starts]
    datetime_ends = [hypnogram_start + datetime.timedelta(minutes=idx*resolution) for idx in idx_ends]

    # at this point we filter out the bbi DataFrame from the awakening periods
    for start, end in zip(datetime_starts, datetime_ends):
        bbi_df = bbi_df.loc[
            (bbi_df[constants._ISODATE_COL] < start) | (bbi_df[constants._ISODATE_COL] > end)
        ]

    return bbi_df
