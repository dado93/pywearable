"""
This module contains all the functions related to the analysis
of Labfront activity data.
"""

import pylabfront.utils as utils
import pandas as pd
import numpy as np

from datetime import timedelta

_LABFRONT_ISO_DATE_KEY = "isoDate"
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL = "calendarDate"
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_COL = "steps"
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_GOAL_COL = "stepsGoal"
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL = "distanceInMeters"
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_MODERATE_INTENSITY_COL = (
    "moderateIntensityDurationInMs"
)
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_VIGOROUS_INTENSITY_COL = (
    "vigorousIntensityDurationInMs"
)
_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL = "intensity"
_LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL = "activeTimeInMs"

_MS_TO_HOURS_CONVERSION = 1000 * 60 * 60
_MS_TO_MINUTES_CONVERSION = 1000 * 60


def get_activity_by_period(loader, activity, start_date, end_date, user_id="all"):
    """Get a general activity time series.

    This function returns the activity required as a time series
    for the users and period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_ids``.
    user_id : :class:`str`, optional
        IDs of the users for which data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the activity time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    activity_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)

    for id in user_ids:
        try:
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - timedelta(minutes=15)
            )
            activity_dict[id] = pd.Series(
                df[df[_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL] == activity][
                    _LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL
                ].values,
                index=df[df.intensity == activity].isoDate,
            )
        except:
            activity_dict[id] = None

    return activity_dict


def get_active(loader, start_date, end_date, user_id="all"):
    """Get activity time series.

    This function returns the amount of activity as a time series
    for the users and period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_ids``.
    user_id : :class:`str`, optional
        IDs of the users for which data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the activity time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    return get_activity_by_period(loader, "ACTIVE", start_date, end_date, user_id)


def get_highly_active(loader, start_date, end_date, user_id="all"):
    """Get intensive activity time series.

    This function returns the amount of activity as a time series
    for the users and period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_ids``.
    user_id : :class:`str`, optional
        IDs of the users for which data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the time series for intensive activity for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    return get_activity_by_period(
        loader, "HIGHLY_ACTIVE", start_date, end_date, user_id
    )


def get_sedentary(loader, start_date, end_date, user_id="all"):
    """Get sedentary activity time series.

    This function returns the amount of sedentary activity as a time series
    for the users and period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_ids``.
    user_id : :class:`str`, optional
        IDs of the users for which data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the time series for sedentary activity for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the desired activity level between start_date and end_date.
    """
    return get_activity_by_period(loader, "SEDENTARY", start_date, end_date, user_id)


def get_steps(loader, start_date, end_date, user_id="all"):
    """Get steps time series.

    This function returns the amount of steps as a time series
    with a granularity of 15 minutes for the users and period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_ids``.
    user_id : :class:`str`, optional
        IDs of the users for which data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the steps time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the steps done between start_date and end_date.
    """

    steps_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)

    for id in user_ids:
        try:
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - timedelta(minutes=15)
            )
            steps_dict[id] = df.groupby(_LABFRONT_ISO_DATE_KEY)[
                _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_COL
            ].sum()
        except:
            steps_dict[id] = None

    return steps_dict


def get_distance(loader, start_date, end_date, user_id="all"):
    """Get distance time series.

    This function returns the distance travelled by foot in meters as a time series
    with a granularity of 15 minutes for the users and period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_ids``.
    user_id : :class:`str`, optional
        IDs of the users for which data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the distance time series for the given ``user_id``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a time series of the distance walked between start_date and end_date.
    """
    distance_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)

    for id in user_ids:
        try:
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - timedelta(minutes=15)
            )
            distance_dict[id] = df.groupby(_LABFRONT_ISO_DATE_KEY)[
                _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL
            ].sum()
        except:
            distance_dict[id] = None

    return distance_dict


def get_steps_per_day(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get steps for each day.

    This function returns the total daily steps for the given participant(s)
    for each given day from ``start_date`` to ``end_date``

    Parameters
    ----------
        loader : :class:`pylabfront.loader`
            Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
        start_date :  :class:`datetime.datetime`, optional
            Start date from which should be extracted, by default None.
            If None is used, then the `start_date` will be the first day with available data
            for the given `user_ids`.
        end_date : :class:`datetime.datetime`, optional
            End date up to which data should be extracted, by default None.
            If None is used, then the ``end_date`` will be the last day with available data
            for the given `user_ids`.
        user_id : :class:`str`, optional
            IDs of the users for which data have to extracted, by default "all"
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

    for id in user_ids:
        participant_daily_summary = loader.load_garmin_connect_daily_summary(
            id, start_date, end_date
        )
        if len(participant_daily_summary) > 0:
            participant_daily_summary = participant_daily_summary.groupby(
                _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL
            ).tail(1)
            if average:
                data_dict[id] = int(
                    participant_daily_summary[
                        _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_COL
                    ].values.mean()
                )
            else:
                data_dict[id] = pd.Series(
                    participant_daily_summary[
                        _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_COL
                    ].values,
                    index=participant_daily_summary[
                        _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL
                    ],
                ).to_dict()
        else:
            data_dict[id] = None

    return data_dict


def get_distance_per_day(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get distance covered for each day.

    This function returns the amount of meters covered for the given participant(s)
    for each given day from ``start_date`` to ``end_date``

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_dt (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_dt (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list, optional): List of participants of interest. Defaults to "all".
        average (bool, optional): Indication whether to calculate the average. Defaults to False.

    Returns:
        dict: Dictionary of daily meters covered by participants of interest
    """
    data_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)

    for id in user_ids:
        participant_epochs = loader.load_garmin_connect_epoch(
            id, start_date, end_date + timedelta(hours=23, minutes=45)
        )
        if len(participant_epochs) > 0:
            participant_epochs[
                _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL
            ] = participant_epochs[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.date())
            participant_daily_summary = (
                participant_epochs.groupby(
                    _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL
                )[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL]
                .sum()
                .reset_index()
            )
            if average:
                data_dict[id] = int(
                    participant_daily_summary[
                        _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL
                    ].values.mean()
                )
            else:
                data_dict[id] = pd.Series(
                    participant_daily_summary[
                        _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL
                    ].values,
                    index=participant_daily_summary[
                        _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL
                    ],
                ).to_dict()
        else:
            data_dict[id] = None

    return data_dict


def get_steps_goal_per_day(loader, start_date=None, end_date=None, user_id="all"):
    """Get daily steps goal

    This function returns the steps goal for every day within the period of interest

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily steps goal is retrieved, by default None.
    end_date : :class:`datetime.datetime`, optional
        End date to which daily steps goal is retrieved, by default None.
    user_id : :class:`str`, optional
        ID of the user for which daily steps goal is retrieved, by default "all".

    Returns
    ----------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys,
        and steps goal as value.
    """
    data_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)

    for id in user_ids:
        participant_daily_summary = loader.load_garmin_connect_daily_summary(
            id, start_date, end_date
        )
        if len(participant_daily_summary) > 0:
            participant_daily_summary = participant_daily_summary.groupby(
                _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL
            ).tail(1)
            data_dict[id] = pd.Series(
                participant_daily_summary[
                    _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_GOAL_COL
                ].values,
                index=participant_daily_summary[
                    _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL
                ],
            ).to_dict()
        else:
            data_dict[id] = None

    return data_dict

def get_daily_intensity(loader,
                        start_date=None,
                        end_date=None,
                        user_id="all",
                        merge_together=False,
                        average=False):
    """Gets daily intensity data for the users and period of interest

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily steps goal is retrieved, by default None.
    end_date : :class:`datetime.datetime`, optional
        End date to which daily steps goal is retrieved, by default None.
    user_id : :class:`str`, optional
        ID of the user for which daily steps goal is retrieved, by default "all".
    merge_together : bool, optional
        whether to merge together moderate(mi) and vigorous intensities(vi) as (mi+2*vi), by default False
    average : bool, optional
        whether to compute the average over the entire period or get daily data, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with users as primary keys, dates as secondary keys, and daily intensities as values.
        If `average` is set to True, then the primary key is directly connected to the average intensity.
    """
    data_dict = {}
    
    user_id = utils.get_user_ids(loader,user_id)

    for user in user_id: 
        participant_daily_summaries = loader.load_garmin_connect_daily_summary(user,
                                                                               start_date,
                                                                               end_date+timedelta(hours=23,minutes=45))
        if len(participant_daily_summaries) > 0:
            participant_daily_summaries = participant_daily_summaries.groupby(_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL).tail(1)
            moderate_intensities = participant_daily_summaries[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_MODERATE_INTENSITY_COL].div(1000*60).values
            vigorous_intensities = participant_daily_summaries[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_VIGOROUS_INTENSITY_COL].div(1000*60).values
            daily_intensities = [(moderate_intensities[i], vigorous_intensities[i]) for i in range(len(moderate_intensities))]
            if not merge_together:
                data_dict[user] = pd.Series(daily_intensities,
                                               index=participant_daily_summaries[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL]).to_dict()
            else:
                merged_intensities = [daily_intensities[i][0]+2*daily_intensities[i][1] for i in range(len(daily_intensities))]
                if average:
                    data_dict[user] = np.mean(merged_intensities)
                else:
                    data_dict[user] = pd.Series(merged_intensities,
                                               index=participant_daily_summaries[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL].to_dict())
        else:
            data_dict[user] = None

    return data_dict

def get_avg_daily_activities(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Create a dictionary reporting for every participant of interest
    the mean amount of daily time spent per activity level during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list, optional): List of participants of interest. Defaults to "all".
        raturn_as_ratio (bool, optional): Indication of whather the values returned should be in ratio form. Defaults to False.

    Returns:
        dict: Dictionary of participants activities duration in minutes (or ratio).
        If there was no data for a participant for the period of interest, the value is None.
    """

    activities_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)

    for id in user_ids:
        try:
            # get data for the period desired
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - timedelta(minutes=15)
            )
            if len(df) == 0:
                raise Exception
            df["date"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.date())
            # group per date and type of activity
            df = (
                df.groupby(["date", _LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL])[
                    _LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL
                ]
                .sum()
                .reset_index()
            )
            if return_as_ratio:
                time_collected_per_day = (
                    df.groupby(["date"])[
                        _LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL
                    ]
                    .sum()
                    .reset_index()
                )
                # pivot the data so to be in dimensions that allow for division with pandas funcs
                activity_durations_per_day = df.pivot(
                    index="date",
                    columns=_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL,
                    values=_LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL,
                ).reset_index()
                ratio_df = (
                    activity_durations_per_day.iloc[:, 1:].div(
                        time_collected_per_day.activeTimeInMs, axis=0
                    )
                    * 100
                ).fillna(0)
                activities_dict[id] = ratio_df.mean().round(1)
            else:
                activities_dict[id] = round(
                    df.groupby([_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL])[
                        _LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL
                    ].mean()
                    / _MS_TO_MINUTES_CONVERSION,
                    1,
                )
        except:
            activities_dict[id] = None

    return activities_dict


def get_avg_daily_sedentary(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Create a dictionary reporting for every participant of interest
    the amount of time spent sedentary during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Indication of whather the values returned should be in ratio form. Defaults to False.

    Returns:
        dict: Dictionary of participants' sedentary activity during the day in minutes (or ratio).
        If there was no data or sedentary time for a participant, the value is None.
    """
    activities_dict = get_avg_daily_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    )
    sedentary_dict = {}

    for participant_id in activities_dict.keys():
        participant_activities = activities_dict[participant_id]
        try:
            sedentary_dict[participant_id] = participant_activities.get("SEDENTARY", 0)
        except:
            sedentary_dict[participant_id] = None

    return sedentary_dict


def get_avg_daily_active(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Create a dictionary reporting for every participant of interest
    the amount of time spent active during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Indication of whather the values returned should be in ratio form. Defaults to False.

    Returns:
        dict: Dictionary of active time per participant in minutes (or ratio).
        If there was no data or active time for a participant, the value is None.
    """
    activities_dict = get_avg_daily_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    )
    active_dict = {}

    for participant_id in activities_dict.keys():
        participant_activities = activities_dict[participant_id]
        try:
            active_dict[participant_id] = participant_activities.get("ACTIVE", 0)
        except:
            active_dict[participant_id] = None

    return active_dict


def get_avg_daily_highly_active(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Create a dictionary reporting for every participant of interest
    the amount of time spent highly active during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Indication of whather the values returned should be in ratio form. Defaults to False.

    Returns:
        dict: Dictionary of active time per participant in minutes (or ratio).
        If there was no data or highly active time for a participant, the value is None.
    """
    activities_dict = get_avg_daily_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    )
    highly_active_dict = {}

    for participant_id in activities_dict.keys():
        participant_activities = activities_dict[participant_id]
        try:
            highly_active_dict[participant_id] = participant_activities.get(
                "HIGHLY_ACTIVE", 0
            )
        except:
            highly_active_dict[participant_id] = None

    return highly_active_dict


def get_avg_weekly_activities(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Creates a dictionary reporting for every participant of interest
    a DataFrame detailing the mean amount of time spent for activity level for
    every day of the week (0 to 6, 0 being Monday and 6 Sunday)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary of the weekly activities of the participants (as a DataFrame).
        If no activity was registered in the period of interest for a participant,
        values are None instead.
    """

    weekday_activities_dict = {}

    user_ids = utils.get_user_ids(loader, user_id)

    for id in user_ids:
        try:
            # get data for that period
            df = loader.load_garmin_connect_epoch(
                id, start_date, end_date - timedelta(minutes=15)
            )
            if len(df) == 0:
                raise Exception
            # create columns to tell for each entry which day it is, both calendar date and weekday
            df["date"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.date())
            df["weekday"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.weekday())
            # calculate for every calendar date the total amount time for each activity
            df = (
                df.groupby(
                    ["date", _LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL, "weekday"]
                )[_LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL]
                .sum()
                .reset_index()
            )
            if return_as_ratio:
                activity_df = df.pivot(
                    index=["date", "weekday"],
                    columns=_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL,
                    values=_LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL,
                ).reset_index()
                time_collected_df = (
                    df.groupby(["date"])[
                        _LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL
                    ]
                    .sum()
                    .reset_index()
                )
                ratio_df = pd.concat(
                    [
                        activity_df.iloc[:, 2:]
                        .div(
                            time_collected_df[
                                _LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL
                            ],
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
                    df.groupby(
                        [_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL, "weekday"]
                    )[_LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL]
                    .mean()
                    .reset_index()
                )
                # make it more readable and transform MS to minutes
                df = (
                    df.pivot(
                        index="weekday",
                        columns=_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL,
                        values=_LABFRONT_GARMIN_CONNECT_EPOCH_ACTIVE_TIME_MS_COL,
                    )
                    / _MS_TO_MINUTES_CONVERSION
                )
                weekday_activities_dict[id] = df.fillna(0).round(1)
        except:
            weekday_activities_dict[id] = None

    return weekday_activities_dict


def get_avg_weekday_sedentary(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Get the daily average amount of time (in minutes) spent sedentary
    by participants of interest in a given time frame, for working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whether to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the
        average daily amount of minutes spent sedentary.
    """

    avg_sedentary_dict = {}

    for k, v in get_avg_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_sedentary_dict[k] = None
        else:
            df = v.reset_index()
            avg_sedentary_dict[k] = round(
                df.loc[df.weekday.isin(range(0, 5))].SEDENTARY.mean(), 1
            )

    return avg_sedentary_dict


def get_avg_weekday_active(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Get the daily average amount of time (in minutes) spent active
    by participants of interest in a given time frame, for working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the
        average daily amount of minutes spent active.
    """

    avg_active_dict = {}

    for k, v in get_avg_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_active_dict[k] = round(
                df.loc[df.weekday.isin(range(0, 5))].ACTIVE.mean(), 1
            )

    return avg_active_dict


def get_avg_weekday_highly_active(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Get the daily average amount of time (in minutes) spent highly active
    by participants of interest in a given time frame, for working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the
        average daily amount of minutes spent highly active.
    """

    avg_highly_active_dict = {}

    for k, v in get_avg_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_highly_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_highly_active_dict[k] = round(
                df.loc[df.weekday.isin(range(0, 5))].HIGHLY_ACTIVE.mean(), 1
            )

    return avg_highly_active_dict

    return avg_highly_active_dict


def get_avg_weekend_sedentary(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Get the daily average amount of time (in minutes) spent sedentary
    by participants of interest in a given time frame, during weekends (Sat/Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the
        average daily amount of minutes spent sedentary, during weekends.
    """

    avg_sedentary_dict = {}

    for k, v in get_avg_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_sedentary_dict[k] = None
        else:
            df = v.reset_index()
            avg_sedentary_dict[k] = round(
                df.loc[~df.weekday.isin(range(0, 5))].SEDENTARY.mean(), 1
            )

    return avg_sedentary_dict


def get_avg_weekend_active(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Get the daily average amount of time (in minutes) spent active
    by participants of interest in a given time frame, for weekends (Sat/Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the
        average daily amount of minutes spent active, during weekends.
    """

    avg_active_dict = {}

    for k, v in get_avg_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_active_dict[k] = round(
                df.loc[~df.weekday.isin(range(0, 5))].ACTIVE.mean(), 1
            )

    return avg_active_dict


def get_avg_weekend_highly_active(
    loader, start_date=None, end_date=None, user_id="all", return_as_ratio=False
):
    """Get the daily average amount of time (in minutes) spent highly active
    by participants of interest in a given time frame, for weekends (Sat/Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the
        average daily amount of minutes spent highly active, during weekends.
    """

    avg_highly_active_dict = {}

    for k, v in get_avg_weekly_activities(
        loader, start_date, end_date, user_id, return_as_ratio
    ).items():
        if v is None:
            avg_highly_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_highly_active_dict[k] = round(
                df.loc[~df.weekday.isin(range(0, 5))].HIGHLY_ACTIVE.mean(), 1
            )

    return avg_highly_active_dict
