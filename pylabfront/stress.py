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

def get_daily_stress_profiles(loader, start_date=None, end_date=None, participant_ids="all"):
    pass


def get_sleep_summary_stage_by_day(loader, sleep_stage, start_date=None, end_date=None, participant_id="all"):
    """Get total time spent in a sleep stage for each day.

    This function returns the absolute time spent in a certain sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        sleep_stage (str): Type of sleep stage or metric to be extracted.
                            'REM': REM sleep stage.
                            'LIGHT_SLEEP': Light sleep stage.
                            'DEEP_SLEEP': Deep sleep stage.
                            'AWAKE': Awake sleep stage.
                            'UNMEASURABLE': Unmeasureable sleep stage.
                            'DURATION': Total duration of sleep.
                            'SLEEP_SCORE': Sleep score computed by Garmin.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep stages should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep stages should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with calendar day as key, and time spent in `sleep_stage` as value.
    """
    data_dict = {}
    if participant_id == "all":
        # get all participant ids automatically
        participant_id = loader.get_user_ids()

    if isinstance(participant_id, str):
        participant_id = [participant_id]

    if not isinstance(participant_id, list):
        raise TypeError("participant_ids has to be a list.")
    if sleep_stage == 'REM':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL
    elif sleep_stage == 'LIGHT_SLEEP':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_LIGHT_SLEEP_MS_COL
    elif sleep_stage == 'DEEP_SLEEP':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_DEEP_SLEEP_MS_COL
    elif sleep_stage == 'AWAKE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_SLEEP_MS_COL
    elif sleep_stage == 'UNMEASURABLE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_MS_COL
    elif sleep_stage == 'DURATION':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL
    elif sleep_stage == 'SLEEP_SCORE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SCORE_COL
    else:
        raise ValueError("Invalid metric")

    for participant in participant_id:
        # Load sleep summary data
        participant_sleep_summary = loader.load_garmin_connect_sleep_summary(
            participant, start_date, end_date)
        if len(participant_sleep_summary) > 0:
            data_dict[participant] = pd.Series(participant_sleep_summary[column].values,
                                               index=participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL]).to_dict()

    return data_dict

def get_stress_per_weekday():
    pass

def get_stress_per_weekend():
    pass
