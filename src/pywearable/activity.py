"""
This module contains all the functions related to the analysis
of Labfront activity data.
"""

import datetime
from typing import Union

import numpy as np
import pandas as pd

from . import constants, utils

from .loader.base import BaseLoader

_MS_TO_MINUTES_CONVERSION = 1000 * 60
_ACTIVITY_TIME_IN_MINUTES = "activeTimeInMinutes"


def get_activity_series(
    loader: BaseLoader,
    activity: str,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Get a general activity time series.

    This function returns the activity required as a time series
    for the users and period of interest.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader`, required in order to properly load data.
    activity: str
        Activity to be retrieved. Possible values are:
            - ACTIVE
            - HIGHLY_ACTIVE
            - SEDENTARY
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which data have to extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    
    Returns
    -------
    :class:`dict`
        The returned dictionary contains the activity time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    activity_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    if end_date is None:
        end_date = datetime.datetime.now()
    for id in user_ids:
        try:
            df = loader.load_garmin_connect_epoch(
                id,
                start_date,
                end_date - datetime.timedelta(minutes=15),  # TODO Do we need to do it?
            )
            activity_dict[id] = pd.Series(
                df[df[constants._EPOCH_INTENSITY_COL] == activity][
                    constants._EPOCH_ACTIVE_TIME_MS_COL
                ].values,
                index=df[df[constants._EPOCH_INTENSITY_COL] == activity][
                    constants._ISODATE_COL
                ],
            )
        except Exception as e:
            activity_dict[id] = None

    return activity_dict


def get_active_activity_series(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Get active activity time series.

    This function returns the amount of active activity as a time series
    for the users and period of interest. The values are returned as
    :class:`dict`, with a :class:`pd.Series` for each user.

    Example return values::

        {'DAV_f457c562': isoDate
            2023-09-10 08:15:00    262000
            2023-09-10 08:30:00    293000
            2023-09-10 08:45:00    422000
            2023-09-10 09:15:00    358000
            2023-09-10 13:45:00    471000
                                    ...
            2023-09-13 12:15:00     15000
            2023-09-13 12:30:00    250000
            2023-09-13 12:45:00     15000
            2023-09-13 13:00:00    135000
            2023-09-13 13:15:00    290000
            Length: 81, dtype: int64}

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which data have to extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the active activity time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    return get_activity_series(
        loader,
        constants._EPOCH_ACTIVITY_ACTIVE_VALUE,
        user_id,
        start_date,
        end_date,
    )


def get_highly_active_activity_series(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Get highly active activity time series.

    This function returns the amount of highly active activity as a time series
    for the users and period of interest.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which data have to extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the time series for highly active activity for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    return get_activity_series(
        loader,
        constants._EPOCH_ACTIVITY_HIGHLY_ACTIVE_VALUE,
        user_id,
        start_date,
        end_date,
    )


def get_sedentary_activity_series(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Get sedentary activity time series.

    This function returns the amount of sedentary activity as a time series
    for the users and period of interest.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which data have to extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the time series for sedentary activity for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    return get_activity_series(
        loader,
        constants._EPOCH_ACTIVITY_SEDENTARY_VALUE,
        user_id,
        start_date,
        end_date,
    )


def get_steps_series(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Get steps time series.

    This function returns the amount of steps as a time series
    with a granularity of 15 minutes for the users and period of interest.
    The dictionary has the ``user_id`` has key, and a :class:`pd.Series`
    as value, with the timestamp as index and the number of steps as
    values.

    Example dictionary::

        {'DAV_f457c562': isoDate
            2023-09-10 05:45:00      0
            2023-09-10 06:00:00      0
            2023-09-10 06:15:00      0
            2023-09-10 06:30:00      0
            2023-09-10 06:45:00      0
                                ...
            2023-09-13 12:15:00      9
            2023-09-13 12:30:00    328
            2023-09-13 12:45:00     10
            2023-09-13 13:00:00    149
            2023-09-13 13:15:00    409
            Name: steps, Length: 304, dtype: int64}

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which data have to extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the steps time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the steps done between start_date and end_date.
    """

    steps_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    if end_date is None:
        end_date = datetime.datetime.now()
    for id in user_ids:
        try:
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - datetime.timedelta(minutes=15)
            )
            steps_dict[id] = df.groupby(constants._ISODATE_COL)[
                constants._DAILY_SUMMARY_STEPS_COL
            ].sum()
        except:
            steps_dict[id] = None

    return steps_dict


def get_distance_series(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Get distance time series.

    This function returns the distance traveled by foot in meters as a time series
    with a granularity of 15 minutes for the users and period of interest.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which data have to extracted, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the distance time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the distance walked between start_date and end_date.
    """
    distance_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    if end_date is None:
        end_date = datetime.datetime.now()
    for id in user_ids:
        try:
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - datetime.timedelta(minutes=15)
            )
            distance_dict[id] = df.groupby(constants._ISODATE_COL)[
                constants._DAILY_SUMMARY_DISTANCE_COL
            ].sum()
        except:
            distance_dict[id] = None

    return distance_dict


def get_daily_steps(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get steps for each day.

    This function returns the total daily steps for the given participant(s)
    for each given day from ``start_date`` to ``end_date``

    Parameters
    ----------
        loader : :class:`BaseLoader`
            Initialized instance of :class:`BaseLoader`, required in order to properly load data.
        user_id : :class:`str` or :class:`list`, optional
            IDs of the users for which data have to extracted, by default "all"
        start_date :  :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
            Start date from which should be extracted, by default None.
            If None is used, then the `start_date` will be the first day with available data
            for the given `user_ids`.
        end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
            End date up to which data should be extracted, by default None.
            If None is used, then the ``end_date`` will be the last day with available data
            for the given `user_ids`.
        average: :class:'bool', optional
            Whether to average the statistic or not, by default False.
            If set to True, then the statistic is returned as the average from
            `start_date` to `end_date`. If set to False, then a single value
            is returned for each day from `start_date` to `end_date`.

    Returns
    -------
    :class:`dict`
        Dictionary of daily number of steps for participants of interest
    """

    data_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    for id in user_ids:
        participant_daily_summary = loader.load_daily_summary(id, start_date, end_date)
        if len(participant_daily_summary) > 0:
            participant_daily_summary = participant_daily_summary.groupby(
                constants._DAILY_SUMMARY_CALENDAR_DATE_COL
            ).tail(1)
            if average:
                data_dict[id] = int(
                    participant_daily_summary[
                        constants._DAILY_SUMMARY_STEPS_COL
                    ].values.mean()
                )
            else:
                data_dict[id] = pd.Series(
                    participant_daily_summary[
                        constants._DAILY_SUMMARY_STEPS_COL
                    ].values,
                    index=participant_daily_summary[
                        constants._DAILY_SUMMARY_CALENDAR_DATE_COL
                    ].dt.date,
                ).to_dict()
        else:
            data_dict[id] = None

    return data_dict


def get_daily_distance(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get distance in meters for each day.

    This function returns the amount of meters covered by the given
    user(s) for each given day from `start_date` to `end_date`.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`, required for data loading.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data loading, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data loading, by default None
    average : :class:`bool`, optional
        Whether to average the distance in meters across all days, by default False

    Returns
    -------
    :class:`dict`
        Dictionary of daily distance (in meters) for each user of interest
    """
    data_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    if end_date is None:
        end_date = datetime.datetime.now()
    for id in user_ids:
        participant_daily_summary = loader.load_daily_summary(id, start_date, end_date)
        if len(participant_daily_summary) > 0:
            participant_daily_summary = participant_daily_summary.groupby(
                constants._DAILY_SUMMARY_CALENDAR_DATE_COL
            ).tail(1)
            if average:
                data_dict[id] = int(
                    participant_daily_summary[
                        constants._DAILY_SUMMARY_DISTANCE_COL
                    ].values.mean()
                )
            else:
                data_dict[id] = pd.Series(
                    participant_daily_summary[
                        constants._DAILY_SUMMARY_DISTANCE_COL
                    ].values,
                    index=participant_daily_summary[
                        constants._DAILY_SUMMARY_CALENDAR_DATE_COL
                    ].dt.date,
                ).to_dict()
        else:
            data_dict[id] = None
        
        return data_dict


def get_daily_steps_goal(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
) -> dict:
    """Get daily steps goal.

    This function returns the steps goal for every day within the period of interest.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of data loader.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user for which daily steps goal is retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data loading, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data loading, by default None

    Returns
    ----------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys,
        and steps goal as value.
    """
    data_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    for id in user_ids:
        participant_daily_summary = loader.load_daily_summary(id, start_date, end_date)
        if len(participant_daily_summary) > 0:
            participant_daily_summary = participant_daily_summary.groupby(
                constants._DAILY_SUMMARY_CALENDAR_DATE_COL
            ).tail(1)
            data_dict[id] = pd.Series(
                participant_daily_summary[
                    constants._DAILY_SUMMARY_STEPS_GOAL_COL
                ].values,
                index=participant_daily_summary[
                    constants._DAILY_SUMMARY_CALENDAR_DATE_COL
                ].dt.date,
            ).to_dict()
        else:
            data_dict[id] = None

    return data_dict


def get_daily_intensity(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    merge_together: bool = False,
    average: bool = False,
) -> dict:
    """Gets daily intensity data for the users and period of interest

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user_id : :class:`str` or :class:`list`, optional
        User(s) for which daily steps goal is retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which daily steps goal is retrieved, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date to which daily steps goal is retrieved, by default None.
    merge_together : :class:`bool`, optional
        Whether to merge together moderate(mi) and vigorous intensities(vi) as (mi+2*vi), by default False
    average : :class:`bool`, optional
        Whether to compute the average over the entire period or get daily data, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with users as primary keys, dates as secondary keys, and daily intensities in minutes as values.
        If `average` is set to True, then the primary key is directly connected to the average intensity.
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    if end_date is None:
        end_date = datetime.datetime.now()
    for user in user_id:
        participant_daily_summaries = loader.load_daily_summary(
            user, start_date, end_date + datetime.timedelta(hours=23, minutes=45)
        )
        if len(participant_daily_summaries) > 0:
            participant_daily_summaries = participant_daily_summaries.groupby(
                constants._DAILY_SUMMARY_CALENDAR_DATE_COL
            ).tail(1)
            moderate_intensities = (
                participant_daily_summaries[
                    constants._DAILY_SUMMARY_MODERATE_INTENSITY_COL
                ]
                .div(1000 * 60)
                .values
            )
            vigorous_intensities = (
                participant_daily_summaries[
                    constants._DAILY_SUMMARY_VIGOROUS_INTENSITY_COL
                ]
                .div(1000 * 60)
                .values
            )
            daily_intensities = [
                (moderate_intensities[i], vigorous_intensities[i])
                for i in range(len(moderate_intensities))
            ]
            if not merge_together:
                data_dict[user] = pd.Series(
                    daily_intensities,
                    index=participant_daily_summaries[
                        constants._DAILY_SUMMARY_CALENDAR_DATE_COL
                    ].dt.date,
                ).to_dict()
            else:
                merged_intensities = [
                    daily_intensities[i][0] + 2 * daily_intensities[i][1]
                    for i in range(len(daily_intensities))
                ]
                if average:
                    data_dict[user] = np.mean(merged_intensities)
                else:
                    data_dict[user] = pd.Series(
                        merged_intensities,
                        index=participant_daily_summaries[
                            constants._DAILY_SUMMARY_CALENDAR_DATE_COL
                        ].dt.date,
                    ).to_dict()
        else:
            data_dict[user] = None

    return data_dict


def get_average_daily_activity_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get average daily activity levels (in minutes).

    This function computes the daily average activity levels in minutes for the
    user(s) and the period of interest.

    Example code ::


        pylabfront.activity.get_average_daily_activity_minutes(
            loader,
            user_id,
            start_date,
            end_date,
            return_as_ratio=True,
        )
        >>{'DAV_f457c562': intensity
            ACTIVE            6.5
            HIGHLY_ACTIVE     2.0
            SEDENTARY        91.5
            dtype: float64}

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader` for data loading.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio for each activity level, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with average daily activities.
    """

    activities_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    if end_date is None:
        end_date = datetime.datetime.now()
    for id in user_ids:
        try:
            # get data for the period desired
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - datetime.timedelta(minutes=15)
            )
            if len(df) == 0:
                raise Exception
            df["date"] = df[constants._ISODATE_COL].apply(lambda x: x.date())
            # group per date and type of activity
            df = (
                df.groupby(["date", constants._EPOCH_INTENSITY_COL])[
                    constants._EPOCH_ACTIVE_TIME_MS_COL
                ]
                .sum()
                .reset_index()
            )
            df = df.rename(
                columns={constants._EPOCH_ACTIVE_TIME_MS_COL: _ACTIVITY_TIME_IN_MINUTES}
            )
            if return_as_ratio:
                time_collected_per_day = (
                    df.groupby(["date"])[_ACTIVITY_TIME_IN_MINUTES].sum().reset_index()
                )
                # pivot the data so to be in dimensions that allow for division with pandas funcs
                activity_durations_per_day = df.pivot(
                    index="date",
                    columns=constants._EPOCH_INTENSITY_COL,
                    values=_ACTIVITY_TIME_IN_MINUTES,
                ).reset_index()
                ratio_df = (
                    activity_durations_per_day.iloc[:, 1:].div(
                        time_collected_per_day[_ACTIVITY_TIME_IN_MINUTES], axis=0
                    )
                    * 100
                ).fillna(0)
                activities_dict[id] = ratio_df.mean().round(1)
            else:
                activities_dict[id] = round(
                    df.groupby([constants._EPOCH_INTENSITY_COL])[
                        _ACTIVITY_TIME_IN_MINUTES
                    ].mean()
                    / _MS_TO_MINUTES_CONVERSION,
                    1,
                )
        except:
            activities_dict[id] = None

    return activities_dict


def get_average_daily_sedentary_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get average daily sedentary minutes.

    This function computes the average daily sedentary
    minutes across the timeframe of interest for the
    given user(s). The return value is a :class:`dict` with
    the id of the user(s) as keys, and the daily average
    sedentary minutes as value.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader` required for data loading.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with user id as key, and sedentary minutes as value.
    """

    activities_dict = get_average_daily_activity_minutes(
        loader, start_date, end_date, user_id, return_as_ratio
    )
    sedentary_dict = {}

    for participant_id in activities_dict.keys():
        participant_activities = activities_dict[participant_id]
        try:
            sedentary_dict[participant_id] = participant_activities.get(
                constants._EPOCH_ACTIVITY_SEDENTARY_VALUE, 0
            )
        except:
            sedentary_dict[participant_id] = None

    return sedentary_dict


def get_average_daily_active_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get average daily active minutes.

    This function computes the average daily active
    minutes across the timeframe of interest for the
    given user(s). The return value is a :class:`dict` with
    the id of the user(s) as keys, and the daily average
    active minutes as value.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader` required for data loading.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with user id as key, and active minutes as value.
    """

    activities_dict = get_average_daily_activity_minutes(
        loader, start_date, end_date, user_id, return_as_ratio
    )
    active_dict = {}

    for participant_id in activities_dict.keys():
        participant_activities = activities_dict[participant_id]
        try:
            active_dict[participant_id] = participant_activities.get(
                constants._EPOCH_ACTIVITY_ACTIVE_VALUE, 0
            )
        except:
            active_dict[participant_id] = None

    return active_dict


def get_average_daily_highly_active_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get average daily highly active minutes.

    This function computes the average daily highly active
    minutes across the timeframe of interest for the
    given user(s). The return value is a :class:`dict` with
    the id of the user(s) as keys, and the daily average
    highly active minutes as value.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Initialized instance of :class:`BaseLoader` required for data loading.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with user id as key, and highly active minutes as value.
    """
    activities_dict = get_average_daily_activity_minutes(
        loader, start_date, end_date, user_id, return_as_ratio
    )
    highly_active_dict = {}

    for participant_id in activities_dict.keys():
        participant_activities = activities_dict[participant_id]
        try:
            highly_active_dict[participant_id] = participant_activities.get(
                constants._EPOCH_ACTIVITY_HIGHLY_ACTIVE_VALUE, 0
            )
        except:
            highly_active_dict[participant_id] = None

    return highly_active_dict


def get_average_weekly_activities(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get average weekly activities for every day of the week.

    This function retrieves weekly activities minutes for
    every day of the week (0 to 6, 0 being Monday and 6 Sunday).
    The return value is a :class:`dict` with the user id as key,
    and a :class:`pd.DataFrame` as value, with weekday as index,
    and a column for each intensity value.

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    dict
        Dictionary with user id as key, and a :class:`pd.DataFrame` as value.
    """

    weekday_activities_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    if end_date is None:
        end_date = datetime.datetime.now()
    for id in user_ids:
        try:
            # get data for that period
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - datetime.timedelta(minutes=15)
            )
            if len(df) == 0:
                raise Exception
            # create columns to tell for each entry which day it is, both calendar date and weekday
            df["date"] = df[constants._ISODATE_COL].apply(lambda x: x.date())
            df["weekday"] = df[constants._ISODATE_COL].apply(lambda x: x.weekday())
            # calculate for every calendar date the total amount time for each activity
            df = (
                df.groupby(["date", constants._EPOCH_INTENSITY_COL, "weekday"])[
                    constants._EPOCH_ACTIVE_TIME_MS_COL
                ]
                .sum()
                .reset_index()
            )
            if return_as_ratio:
                activity_df = df.pivot(
                    index=["date", "weekday"],
                    columns=constants._EPOCH_INTENSITY_COL,
                    values=constants._EPOCH_ACTIVE_TIME_MS_COL,
                ).reset_index()
                time_collected_df = (
                    df.groupby(["date"])[constants._EPOCH_ACTIVE_TIME_MS_COL]
                    .sum()
                    .reset_index()
                )
                ratio_df = pd.concat(
                    [
                        activity_df.iloc[:, 2:]
                        .div(
                            time_collected_df[constants._EPOCH_ACTIVE_TIME_MS_COL],
                            axis=0,
                        )
                        .fillna(0),
                        activity_df.weekday,
                    ],
                    axis=1,
                )
                weekday_activities_dict[id] = (
                    ratio_df.groupby("weekday").mean() * 100
                ).round(1)
            else:
                # calculate for every weekday the mean amount of time for each activity
                df = (
                    df.groupby([constants._EPOCH_INTENSITY_COL, "weekday"])[
                        constants._EPOCH_ACTIVE_TIME_MS_COL
                    ]
                    .mean()
                    .reset_index()
                )
                # make it more readable and transform MS to minutes
                df = (
                    df.pivot(
                        index="weekday",
                        columns=constants._EPOCH_INTENSITY_COL,
                        values=constants._EPOCH_ACTIVE_TIME_MS_COL,
                    )
                    / _MS_TO_MINUTES_CONVERSION
                )
                weekday_activities_dict[id] = df.fillna(0).round(1)
        except:
            weekday_activities_dict[id] = None

    return weekday_activities_dict


def get_average_weekday_sedentary_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get the weekly average sedentary minutes for weekdays.

    This function gets daily average sedentary minutes for each user(s)
    in a given time frame, for weekdays (Monday-Friday).

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`.
    user_id : ;class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    :class:`dict`
        Dictionary reporting for every user(s) the
        average weekly amount of minutes spent sedentary.
    """

    avg_sedentary_dict = {}

    for k, v in get_average_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_sedentary_dict[k] = None
        else:
            df = v.reset_index()
            avg_sedentary_dict[k] = round(
                df.loc[df.weekday.isin(range(0, 5))][
                    constants._EPOCH_ACTIVITY_SEDENTARY_VALUE
                ].mean(),
                1,
            )

    return avg_sedentary_dict


def get_average_weekday_active_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get the weekly average active minutes for weekdays.

    This function gets weekly average active minutes for each user(s)
    in a given time frame, for weekdays (Monday-Friday).

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    :class:`dict`
        Dictionary reporting for every user(s) the
        average weekly amount of minutes spent active.
    """

    avg_active_dict = {}

    for k, v in get_average_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_active_dict[k] = round(
                df.loc[df.weekday.isin(range(0, 5))][
                    constants._EPOCH_ACTIVITY_ACTIVE_VALUE
                ].mean(),
                1,
            )

    return avg_active_dict


def get_average_weekday_highly_active_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get the weekly average highly active minutes for weekdays.

    This function gets weekly average highly active minutes for each user(s)
    in a given time frame, for weekdays (Monday-Friday).

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    :class:`dict`
        Dictionary reporting for every user(s) the
        average weekly amount of minutes spent highly active.
    """

    avg_highly_active_dict = {}

    for k, v in get_average_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_highly_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_highly_active_dict[k] = round(
                df.loc[df.weekday.isin(range(0, 5))][
                    constants._EPOCH_ACTIVITY_HIGHLY_ACTIVE_VALUE
                ].mean(),
                1,
            )

    return avg_highly_active_dict


def get_average_weekend_sedentary_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get the weekly average sedentary minutes in weekends.

    This function gets weekly average sedentary minutes for each user(s)
    in a given time frame, for weekends (Saturday-Sunday).

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    return_as_ratio : :class:`bool`, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    :class:`dict`
        Dictionary reporting for every user(s) the
        average weekly amount of minutes spent sedentary.
    """

    avg_sedentary_dict = {}

    for k, v in get_average_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_sedentary_dict[k] = None
        else:
            df = v.reset_index()
            avg_sedentary_dict[k] = round(
                df.loc[~df.weekday.isin(range(0, 5))][
                    constants._EPOCH_ACTIVITY_SEDENTARY_VALUE
                ].mean(),
                1,
            )

    return avg_sedentary_dict


def get_average_weekend_active_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get the weekly average active minutes in weekends.

    This function gets weekly average active minutes for each user(s)
    in a given time frame, for weekends (Saturday-Sunday).

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`.
    user_id : :class:`str` or :class:`list`, optional
        User(s) of interest, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : datetime.datetime or datetime.date or str or None, optional
        End date for data retrieval, by default None
    return_as_ratio : bool, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    dict
        Dictionary reporting for every user(s) the
        average weekly amount of minutes spent active.
    """

    avg_active_dict = {}

    for k, v in get_average_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_active_dict[k] = round(
                df.loc[~df.weekday.isin(range(0, 5))][
                    constants._EPOCH_ACTIVITY_ACTIVE_VALUE
                ].mean(),
                1,
            )

    return avg_active_dict


def get_average_weekend_highly_active_minutes(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    return_as_ratio: bool = False,
) -> dict:
    """Get the weekly average highly active minutes in weekends.

    This function gets weekly average highly active minutes for each user(s)
    in a given time frame, for weekends (Saturday-Sunday).

    Parameters
    ----------
    loader : :class:`BaseLoader`
        Instance of :class:`BaseLoader`.
    user_id : str or list, optional
        User(s) of interest, by default "all"
    start_date : datetime.datetime or datetime.date or str or None, optional
        Start date for data retrieval, by default None
    end_date : datetime.datetime or datetime.date or str or None, optional
        End date for data retrieval, by default None
    return_as_ratio : bool, optional
        Return values as ratio with respect to all activities, by default False

    Returns
    -------
    dict
        Dictionary reporting for every user(s) the
        average weekly amount of minutes spent highly active.
    """

    avg_highly_active_dict = {}

    for k, v in get_average_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_highly_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_highly_active_dict[k] = round(
                df.loc[~df.weekday.isin(range(0, 5))][
                    constants._EPOCH_ACTIVITY_HIGHLY_ACTIVE_VALUE
                ].mean(),
                1,
            )

    return avg_highly_active_dict
