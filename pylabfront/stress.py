"""
This module contains all the functions related to the analysis
of Labfront stress data.
"""

import pylabfront.utils as utils
import pandas as pd
import numpy as np

from datetime import timedelta

_LABFRONT_ISO_DATE_KEY = 'isoDate'
_LABFRONT_BODY_BATTERY_KEY = "bodyBattery"
_LABFRONT_STRESS_LEVEL_KEY = "stressLevel"
_LABFRONT_CALENDAR_DAY_KEY = "calendarDate"
_LABFRONT_AVERAGE_STRESS_KEY = "averageStressInStressLevel"
_LABFRONT_MAXIMUM_STRESS_KEY = "maxStressInStressLevel"
_LABFRONT_REST_STRESS_KEY ="restStressDurationInMs"
_LABFRONT_LOW_STRESS_KEY = "lowStressDurationInMs"
_LABFRONT_MEDIUM_STRESS_KEY = "mediumStressDurationInMs"
_LABFRONT_HIGH_STRESS_KEY = "highStressDurationInMs"
_LABFRONT_UNRELIABLE_STRESS_KEY = "activityStressDurationInMs"
_LABFRONT_STRESS_SCORE_KEY = "stressQualifier"

_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL = "calendarDate"

def get_body_battery(loader, start_date=None, end_date=None, participant_ids="all"):
    """ Get body battery time series for a given period

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_ids (str, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant id(s) as key(s), and body battery time series as value(s).
    """

    data_dict = {}
    
    participant_ids = utils.get_user_ids(loader,participant_ids)
    
    for participant_id in participant_ids:
        try:
            df = loader.load_garmin_connect_stress(participant_id,
                                                   start_date,
                                                   end_date-timedelta(minutes=15))
            data_dict[participant_id] = pd.Series(df[_LABFRONT_BODY_BATTERY_KEY].values,index=df[_LABFRONT_ISO_DATE_KEY])
        except:
            data_dict[participant_id] = None

    return data_dict

def get_stress(loader, start_date=None, end_date=None, participant_ids="all"):
    """ Get stress time series for a given period

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_ids (str, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant id(s) as key(s), and stress time series as value(s).
        Stress values of -1,-2 are included in the series.
    """

    data_dict = {}
    
    participant_ids = utils.get_user_ids(loader,participant_ids)
    
    for participant_id in participant_ids:
        try:
            df = loader.load_garmin_connect_stress(participant_id,
                                                   start_date,
                                                   end_date-timedelta(minutes=15))
            data_dict[participant_id] = pd.Series(df[_LABFRONT_STRESS_LEVEL_KEY].values,index=df[_LABFRONT_ISO_DATE_KEY])
        except:
            data_dict[participant_id] = None

    return data_dict


def get_minmax_body_battery_per_day(loader, start_date=None, end_date=None, participant_ids="all"):
    """ Get minmax daily body battery for a given time period

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_ids (str, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant id(s) as key(s), and (min,max) body battery as values.
    """


    bb_dict = {}

    return bb_dict

def get_daily_stress_metrics(loader, start_date=None, end_date=None, participant_ids="all", entire_period=False):
    """ Get avg/max metrics for daily stress.

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_ids (str, optional): ID of the participants. Defaults to "all".
        entire_period (bool, optional): Indication if metrics are computed over the entire period, not daily. Defaults to False.

    Returns:
        dict: Dictionary reporting information about daily levels of stress.
    """

    data_dict = {}
    
    participant_ids = utils.get_user_ids(loader,participant_ids)
    
    for participant_id in participant_ids:
        df = loader.load_garmin_connect_daily_summary(participant_id,
                                                          start_date,
                                                          end_date-timedelta(minutes=15))
        if len(df) > 0:    
            if entire_period:
                data_dict[participant_id] = round(df[_LABFRONT_AVERAGE_STRESS_KEY].mean(),1), round(df[_LABFRONT_MAXIMUM_STRESS_KEY].max(),1)
            else:
                data_dict[participant_id] = pd.Series(zip(df[_LABFRONT_AVERAGE_STRESS_KEY],df[_LABFRONT_MAXIMUM_STRESS_KEY]),
                                                  index=df[_LABFRONT_CALENDAR_DAY_KEY])
        else:
            data_dict[participant_id] = None

    return data_dict

def get_average_stress_weekday(loader, start_date=None, end_date=None, participant_ids="all"):
    """ Gets the average daily stress in working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_ids (str, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant ID(s) as key(s) and average workday stress as value(s)
    """
    data_dict = {}
    participant_ids = utils.get_user_ids(loader,participant_ids)

    for partecipant_id in participant_ids:
        df =loader.load_garmin_connect_daily_summary(partecipant_id,
                                                     start_date,
                                                     end_date-timedelta(minutes=15))
        if len(df) > 0:
            df["weekday"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.weekday())
            df.groupby("weekday")[_LABFRONT_AVERAGE_STRESS_KEY].mean().reset_index()
            df["isWeekend"] = ~df["weekday"].isin(range(0,5))
            data_dict[partecipant_id] = round(df.groupby("isWeekend")["averageStressInStressLevel"].mean()[False],1)
        else:
            data_dict[partecipant_id] = None

    return data_dict

def get_average_stress_weekend(loader, start_date=None, end_date=None, participant_ids="all"):
    """ Gets the average daily stress in weekends (Sat-Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_ids (str, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant ID(s) as key(s) and average weekend stress as value(s)
    """
    data_dict = {}
    participant_ids = utils.get_user_ids(loader,participant_ids)

    for partecipant_id in participant_ids:
        df = loader.load_garmin_connect_daily_summary(partecipant_id,
                                                     start_date,
                                                     end_date-timedelta(minutes=15))
        if len(df) > 0:
            df["weekday"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.weekday())
            df.groupby("weekday")[_LABFRONT_AVERAGE_STRESS_KEY].mean().reset_index()
            df["isWeekend"] = ~df["weekday"].isin(range(0,5))
            data_dict[partecipant_id] = round(df.groupby("isWeekend")["averageStressInStressLevel"].mean()[True],1)
        else:
            data_dict[partecipant_id] = None

    return data_dict

def get_daily_stress_metric(loader, stress_metric, start_date=None, end_date=None, user_ids="all"):
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
            - score: qualifer for the daily stress.
    start_date :class:`datetime.datetime`, optional
        Start date from which stress metric should be extracted, by default None.
    end_date :class:`datetime.datetime`, optional
        End date from which stress metric should be extracted, by default None.
    user_ids: :class:`str`, optional
        ID of the users, by default "all".

    Returns
    -------
    :class:`dict`
        Dictionary with calendar day as key, and daily summary of the stress metric as value.
    """
    
    data_dict = {}

    user_ids = utils.get_user_ids(loader,user_ids)

    if stress_metric.lower() == "rest":
        column = _LABFRONT_REST_STRESS_KEY
    elif stress_metric.lower() == "low":
        column = _LABFRONT_LOW_STRESS_KEY
    elif stress_metric.lower() == "medium":
        column = _LABFRONT_MEDIUM_STRESS_KEY
    elif stress_metric.lower() == "high":
        column = _LABFRONT_HIGH_STRESS_KEY
    elif stress_metric.lower() == "unreliable":
        column = _LABFRONT_UNRELIABLE_STRESS_KEY
    elif stress_metric.lower() == "score" or stress_metric.lower() == "qualifier":
        column = _LABFRONT_STRESS_SCORE_KEY
    else:
        raise ValueError("Invalid metric")
    
    for user in user_ids:
        user_daily_summary = loader.load_garmin_connect_daily_summary(
            user, start_date, end_date
        )
        if len(user_daily_summary) > 0:
            data_dict[user] = pd.Series(
                user_daily_summary[column].values,
                index=user_daily_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL]
            ).to_dict()
        else:
            data_dict[user] = None

    return data_dict

def get_rest_duration(loader, start_date=None, end_date=None, user_ids="all"):
    """Get duration of daily rest stress.

    This function returns the absolute time spent in rest stress level (0-25) 
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily rest data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_ids``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily rest data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_ids``.
    user_ids : :class:`str`, optional
        IDs of the users for which daily rest data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily rest for the given ``user_ids``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily rest duration``
    """
    return get_daily_stress_metric(loader, "rest", start_date, end_date, user_ids)

def get_low_stress_duration(loader, start_date=None, end_date=None, user_ids="all"):
    """Get duration of daily low stress.

    This function returns the absolute time spent in low stress level (25-50) 
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily low stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_ids``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily low stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_ids``.
    user_ids : :class:`str`, optional
        IDs of the users for which daily low stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily low stress duration for the given ``user_ids``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily low stress duration``
    """
    return get_daily_stress_metric(loader, "low", start_date, end_date, user_ids)

def get_medium_stress_duration(loader, start_date=None, end_date=None, user_ids="all"):
    """Get duration of daily medium stress.

    This function returns the absolute time spent in medium stress level (50-75) 
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily medium stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_ids``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily medium stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_ids``.
    user_ids : :class:`str`, optional
        IDs of the users for which daily medium stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily medium stress duration for the given ``user_ids``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily medium stress duration``
    """
    return get_daily_stress_metric(loader, "medium", start_date, end_date, user_ids)

def get_high_stress_duration(loader, start_date=None, end_date=None, user_ids="all"):
    """Get duration of daily high stress.

    This function returns the absolute time spent in high stress level (75-100) 
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily high stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_ids``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily high stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_ids``.
    user_ids : :class:`str`, optional
        IDs of the users for which daily high stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily high stress duration for the given ``user_ids``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily high stress duration``
    """
    return get_daily_stress_metric(loader, "high", start_date, end_date, user_ids)

def get_unreliable_stress_duration(loader, start_date=None, end_date=None, user_ids="all"):
    """Get duration of unreliable daily stress measures.

    This function returns the absolute daily time where stress measures were unreliable (-2/-1) 
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which daily unreliable stress data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_ids``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which daily unrealiable stress data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_ids``.
    user_ids : :class:`str`, optional
        IDs of the users for which daily unreliable stress data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the duration of daily unreliable stress duration for the given ``user_ids``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily unreliable stress duration``
    """
    return get_daily_stress_metric(loader, "unreliable", start_date, end_date, user_ids)

def get_stress_score(loader, start_date=None, end_date=None, user_ids="all"):
    """Get a qualifier that summarizes the daily amount of stress.

    This function returns a score for the daily amount of stress
    for the given participant(s).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which stress score data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_ids``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which stress score data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_ids``.
    user_ids : :class:`str`, optional
        IDs of the users for which stress score data have to extracted, by default "all"

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the daily stress qualifier for the given ``user_ids``.
        The primary key of the dictionary is the id of the user of interest.
        Each value is a nested dictionary with the following structure:
            - ``day`` : ``daily stress qualifier``
    """
    return get_daily_stress_metric(loader, "score", start_date, end_date, user_ids)