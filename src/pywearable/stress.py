"""
This module contains all the functions related to the analysis
of Labfront stress data.
"""

import datetime
from datetime import timedelta
from typing import Union

import numpy as np
import pandas as pd

from . import constants, sleep, utils
from .loader.base import BaseLoader


def get_body_battery(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Gets body battery time series

    Parameters
    ----------
    loader : :class:`BaseLoader`
        An instance of a data loader
    user_id : Union[str, list], optional
        The id(s) for which body battery must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None

    Returns
    -------
    :class:`dict`
        Dictionary with user IDs as primary keys,
        and body battery time series as values.
    """

    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        try:
            df = loader.load_stress(user, start_date, end_date)
            data_dict[user] = pd.Series(
                df[constants._STRESS_BODY_BATTERY_COL].values,
                index=df[constants._ISODATE_COL],
            )
        except:
            data_dict[user] = None

    return data_dict


def get_stress(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
):
    """Get stress time series for a given period.

    Parameters
    ----------
    loader: :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader.
    user_id : Union[str, list], optional
        The id(s) for which stress must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None

    Returns:
    --------
    :class:`dict`
        Dictionary with participant id(s) as key(s),
        and stress time series as value(s).
        Stress values of -1,-2 are included in the series.
    """

    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        try:
            df = loader.load_stress(user, start_date, end_date)
            data_dict[user] = pd.Series(
                df[constants._STRESS_STRESS_LEVEL_COL].values,
                index=df[constants._ISODATE_COL],
            )
        except:
            data_dict[user] = None

    return data_dict


def get_daily_stress_statistics(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    entire_period: bool = False,
):
    """Get avg/max statistics for daily stress.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        Instance of `LabfrontLoader`.
    user_id : Union[str, list], optional
        The id(s) for which stress statistics must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    entire_period : :class:`bool`, optional
        Whether statistics are computed over the entire period, not daily. Defaults to False.

    Returns:
    --------
    :class:`dict`
        Dictionary reporting information about daily levels of stress.
    """

    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        try:
            df = loader.load_daily_summary(
                user, start_date, end_date + timedelta(hours=23, minutes=45)
            )
            df = df.groupby(constants._CALENDAR_DATE_COL).tail(
                1
            )  # consider the last reading of every day
            # need to filter out days where the info isn't available (nan or -1)
            df = df[
                np.logical_and(
                    ~df[constants._DAILY_SUMMARY_AVG_STRESS_IN_STRESS_LVL_COL].isna(),
                    df[constants._DAILY_SUMMARY_AVG_STRESS_IN_STRESS_LVL_COL] != -1,
                )
            ]
            if entire_period:
                data_dict[user] = round(
                    df[constants._DAILY_SUMMARY_AVG_STRESS_IN_STRESS_LVL_COL].mean(), 1
                ), round(
                    df[constants._DAILY_SUMMARY_MAX_STRESS_IN_STRESS_LVL_COL].max(), 1
                )
            else:
                data_dict[user] = pd.Series(
                    zip(
                        df[constants._DAILY_SUMMARY_AVG_STRESS_IN_STRESS_LVL_COL],
                        df[constants._DAILY_SUMMARY_MAX_STRESS_IN_STRESS_LVL_COL],
                    ),
                    index=df[constants._CALENDAR_DATE_COL],
                )
        except:
            data_dict[user] = None

    return data_dict


def get_average_stress_weekday(
    loader: BaseLoader, start_date=None, end_date=None, user_id="all"
):
    """Gets the average daily stress in working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (str, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant ID(s) as key(s) and average workday stress as value(s)
    """
    data_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        df = loader.load_daily_summary(
            user, start_date, end_date - timedelta(minutes=15)
        )
        if len(df) > 0:
            df = df.groupby(constants._CALENDAR_DATE_COL).tail(
                1
            )  # consider the last reading of every day
            df["weekday"] = df[constants._ISODATE_COL].apply(lambda x: x.weekday())
            df.groupby("weekday")[
                constants._DAILY_SUMMARY_AVG_STRESS_IN_STRESS_LVL_COL
            ].mean().reset_index()
            df["isWeekend"] = ~df["weekday"].isin(range(0, 5))
            data_dict[user] = round(
                df.groupby("isWeekend")["averageStressInStressLevel"].mean()[False], 1
            )
        else:
            data_dict[user] = None

    return data_dict


def get_average_stress_weekend(loader, start_date=None, end_date=None, user_id="all"):
    """Gets the average daily stress in weekends (Sat-Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (str, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant ID(s) as key(s) and average weekend stress as value(s)
    """
    data_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        df = loader.load_daily_summary(
            user, start_date, end_date - timedelta(minutes=15)
        )
        if len(df) > 0:
            df = df.groupby(constants._CALENDAR_DATE_COL).tail(
                1
            )  # consider the last reading of every day
            df["weekday"] = df[constants._ISODATE_COL].apply(lambda x: x.weekday())
            df.groupby("weekday")[
                constants._DAILY_SUMMARY_AVG_STRESS_IN_STRESS_LVL_COL
            ].mean().reset_index()
            df["isWeekend"] = ~df["weekday"].isin(range(0, 5))
            data_dict[user] = round(
                df.groupby("isWeekend")["averageStressInStressLevel"].mean()[True], 1
            )
        else:
            data_dict[user] = None

    return data_dict


def get_daily_stress_metric(
    loader, stress_metric, user_id="all", start_date=None, end_date=None 
):
    """Get daily summary of the metric.

    This function returns the garmin connect daily summary for the stress metric of interest

    Parameters
    -----------
    loader: :class:`pylabfront.loader.LabfrontLoader`
        Instance of `LabfrontLoader`.
    sleep_stage: :class:`str`
        Type of stress metric to be extracted. Valid strings are:
            - rest: rest level stress (0-25).
            - low: low level stress (25-50).
            - medium: medium level stress (50-75).
            - high: high level stress (75-100).
            - unreliable: unreliable measurement of stress (-2/-1).
            - score: qualifier for the daily stress.
    start_date :class:`datetime.datetime`, optional
        Start date from which stress metric should be extracted, by default None.
    end_date :class:`datetime.datetime`, optional
        End date from which stress metric should be extracted, by default None.
    user_id: :class:`str`, optional
        ID of the users, by default "all".

    Returns
    -------
    :class:`dict`
        Dictionary with calendar day as key, and daily summary of the stress metric as value.
    """

    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    if stress_metric.lower() == "rest":
        column = constants._DAILY_SUMMARY_REST_STRESS_DURATION_IN_MS_COL
    elif stress_metric.lower() == "low":
        column = constants._DAILY_SUMMARY_LOW_STRESS_DURATION_IN_MS_COL
    elif stress_metric.lower() == "medium":
        column = constants._DAILY_SUMMARY_MEDIUM_STRESS_DURATION_IN_MS_COL
    elif stress_metric.lower() == "high":
        column = constants._DAILY_SUMMARY_HIGH_STRESS_DURATION_IN_MS_COL
    elif stress_metric.lower() == "unreliable":
        column = constants._DAILY_SUMMARY_UNRELIABLE_STRESS_DURATION_IN_MS_COL
    elif stress_metric.lower() == "score" or stress_metric.lower() == "qualifier":
        column = constants._DAILY_SUMMARY_STRESS_SCORE_COL
    else:
        raise ValueError("Invalid metric")

    for user in user_id:
        user_daily_summary = loader.load_daily_summary(user, start_date, end_date)
        if len(user_daily_summary) > 0:
            user_daily_summary = user_daily_summary.groupby(
                constants._CALENDAR_DATE_COL
            ).tail(
                1
            )  # consider last summary
            data_dict[user] = pd.Series(
                user_daily_summary[column].replace(np.nan, None).values,
                index=user_daily_summary[constants._CALENDAR_DATE_COL],
            ).to_dict()
        else:
            data_dict[user] = None

    return data_dict


def get_rest_duration(
    loader: BaseLoader, user_id="all", start_date=None, end_date=None
):
    """Get duration of daily rest stress in ms.

    This function returns the absolute time spent in rest stress level (0-25)
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily rest data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily rest data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which daily rest data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily rest for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily rest duration``
    """
    return get_daily_stress_metric(loader, "rest", start_date, end_date, user_id)


def get_low_stress_duration(
    loader: BaseLoader, start_date=None, end_date=None, user_id="all"
):
    """Get duration of daily low stress in ms.

    This function returns the absolute time spent in low stress level (25-50)
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily low stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily low stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which daily low stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily low stress duration for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily low stress duration``
    """
    return get_daily_stress_metric(loader, "low", start_date, end_date, user_id)


def get_medium_stress_duration(
    loader: BaseLoader, start_date=None, end_date=None, user_id="all"
):
    """Get duration of daily medium stress in ms.

    This function returns the absolute time spent in medium stress level (50-75)
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily medium stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily medium stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which daily medium stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily medium stress duration for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily medium stress duration``
    """
    return get_daily_stress_metric(loader, "medium", start_date, end_date, user_id)


def get_high_stress_duration(
    loader: BaseLoader, start_date=None, end_date=None, user_id="all"
):
    """Get duration of daily high stress in ms.

    This function returns the absolute time spent in high stress level (75-100)
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily high stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily high stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which daily high stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily high stress duration for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily high stress duration``
    """
    return get_daily_stress_metric(loader, "high", start_date, end_date, user_id)


def get_unreliable_stress_duration(loader: BaseLoader,
                                   user_id: Union[str, list] = "all",
                                   start_date: Union[datetime.datetime, datetime.date, str, None] = None,
                                   end_date: Union[datetime.datetime, datetime.date, str, None] = None
):
    """Get duration of unreliable daily stress measures in ms.

    This function returns the absolute daily time where stress measures were unreliable (-2/-1)
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily unreliable stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily unreliable stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which daily unreliable stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily unreliable stress duration for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily unreliable stress duration``
    """
    return get_daily_stress_metric(loader, "unreliable", start_date, end_date, user_id)


def get_stress_score(loader: BaseLoader,
                     user_id: Union[str, list] = "all",
                     start_date: Union[datetime.datetime, datetime.date, str, None] = None,
                     end_date: Union[datetime.datetime, datetime.date, str, None] = None):
    """Get a qualifier that summarizes the daily amount of stress.

    This function returns a score for the daily amount of stress
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which stress score data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which stress score data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which stress score data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the daily stress qualifier for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily stress qualifier``
    """
    return get_daily_stress_metric(loader, "score", user_id, start_date, end_date)


def get_sleep_battery_recovery(loader: BaseLoader,
                               user_id: Union[str, list] = "all",
                               start_date: Union[datetime.datetime, datetime.date, str, None] = None,
                               end_date: Union[datetime.datetime, datetime.date, str, None] = None
):
    """Get body battery recovered during sleep.

    This function returns the amount of body battery recovered while sleeping
    for the given participant(s), in the time range of interest.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of BaseLoader, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which battery recovery have to be extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the amount of body battery recharged
        for the given ``user_id``, for all sleep periods detected.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``body battery recharged``
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        data_dict[user] = {}
        sleep_timestamps = sleep.get_sleep_timestamps(
            loader=loader, user_id=user, start_date=start_date, end_date=end_date
        )[user]
        if not (sleep_timestamps is None):
            for k, v in sleep_timestamps.items():
                sleep_onset, awake_time = v[0], v[1]

                df = loader.load_stress(user, sleep_onset, awake_time)
                if len(df) == 0:
                    continue

                df = df[~df[constants._STRESS_BODY_BATTERY_COL].isna()]
                df = df.reset_index(drop=True)
                if len(df) == 0:
                    continue
                df = (
                    df.groupby(constants._ISODATE_COL)[
                        constants._STRESS_BODY_BATTERY_COL
                    ]
                    .mean()
                    .sort_index()
                )

                data_dict[user][k] = int(df.iloc[-1] - df.iloc[0])

    return data_dict


def get_min_body_battery(loader: BaseLoader,
                         user_id: Union[str, list] = "all",
                         start_date: Union[datetime.datetime, datetime.date, str, None] = None,
                         end_date: Union[datetime.datetime, datetime.date, str, None] = None):
    """Get minimum daily body battery.

    This function returns the minimum recorded daily body battery
    for the given user(s), in the time range of interest.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which minimum body battery have to be extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the minimum daily body battery for the given ``user_id``.
        The primary key(s) of the dictionary is the id of the user(s) of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``minimum body battery``
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        df = loader.load_stress(user, start_date, end_date - timedelta(minutes=1))
        if len(df) > 0:
            df["date"] = df[constants._ISODATE_COL].apply(lambda x: x.date())
            data_dict[user] = pd.Series(
                df.groupby("date")[constants._STRESS_BODY_BATTERY_COL].min()
            ).to_dict()
        else:
            data_dict[user] = None

    return data_dict


def get_max_body_battery(loader: BaseLoader,
                         user_id: Union[str, list] = "all",
                         start_date: Union[datetime.datetime, datetime.date, str, None] = None,
                         end_date: Union[datetime.datetime, datetime.date, str, None] = None
):
    """Get maximum daily body battery.

    This function returns the maximum recorded daily body battery
    for the given user(s), in the time range of interest.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of BaseLoader, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for max body battery have to be extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the maximum daily body battery for the given ``user_id``.
        The primary key(s) of the dictionary is the id of the user(s) of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``maximum body battery``
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        df = loader.load_garmin_connect_stress(
            user, start_date, end_date - timedelta(minutes=1)
        )
        if len(df) > 0:
            df["date"] = df[constants._ISODATE_COL].apply(lambda x: x.date())
            data_dict[user] = pd.Series(
                df.groupby("date")[constants._STRESS_BODY_BATTERY_COL].max()
            ).to_dict()
        else:
            data_dict[user] = None

    return data_dict


def get_average_stress(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
):
    daily_stress_stats = get_daily_stress_statistics(
        loader, user_id, start_date, end_date
    )

    data_dict = {}

    for user in daily_stress_stats.keys():
        if daily_stress_stats[user] is None:
            data_dict[user] = None
        else:
            data_dict[user] = {
                k.date(): v[0] for k, v in daily_stress_stats[user].items()
            }

    return data_dict


def get_waking_body_battery(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
):
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        data_dict[user] = {}
        sleep_timestamps = sleep.get_sleep_timestamps(
            loader, user, start_date, end_date
        )[user]
        if not (sleep_timestamps is None):
            for k, v in sleep_timestamps.items():
                sleep_onset, awake_time = v[0], v[1]

                df = loader.load_stress(user, sleep_onset, awake_time)
                if len(df) == 0:
                    continue

                df = df[~df[constants._STRESS_BODY_BATTERY_COL].isna()]
                if len(df) == 0:
                    continue
                df = (
                    df.groupby(constants._ISODATE_COL)[
                        constants._STRESS_BODY_BATTERY_COL
                    ]
                    .mean()
                    .sort_index()
                )

                data_dict[user][k] = int(df.iloc[-1])

    return data_dict


def get_body_battery_starting_sleep(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
):
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        data_dict[user] = {}
        sleep_timestamps = sleep.get_sleep_timestamps(
            loader, user, start_date, end_date
        )[user]
        if not (sleep_timestamps is None):
            for k, v in sleep_timestamps.items():
                sleep_onset, awake_time = v[0], v[1]

                df = loader.load_stress(user, sleep_onset, awake_time)
                if len(df) == 0:
                    continue

                df = df[~df[constants._STRESS_BODY_BATTERY_COL].isna()]
                if len(df) == 0:
                    continue
                df = (
                    df.groupby(constants._ISODATE_COL)[
                        constants._STRESS_BODY_BATTERY_COL
                    ]
                    .mean()
                    .sort_index()
                )

                data_dict[user][k] = int(df.iloc[0])

    return data_dict


def get_night_average_stress(loader: BaseLoader,
                             user_id: Union[str, list] = "all",
                             start_date: Union[datetime.datetime, datetime.date, str, None] = None,
                             end_date: Union[datetime.datetime, datetime.date, str, None] = None):
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        data_dict[user] = {}
        sleep_timestamps = sleep.get_sleep_timestamps(
            loader, user, start_date, end_date
        )[user]
        if not (sleep_timestamps is None):
            for date, (start_hour, end_hour) in sleep_timestamps.items():
                df = loader.load_stress(user,
                                                start_hour,
                                                end_hour)
                if len(df) == 0:
                    continue
                else:
                    df = df.drop_duplicates()
                    df = df.loc[~df.stressLevel.isin([-1,-2])]
                    df = utils.filter_out_awake(loader, user, df, date)
                    if len(df) > 0:
                        data_dict[user][date] = round(df[constants._STRESS_STRESS_LEVEL_COL].mean(),1)
                    else:
                        continue
    
    return data_dict