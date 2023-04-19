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


def get_daily_stress_profiles(loader, start_date=None, end_date=None, participant_ids="all"):
    # take inspiration from sleep summary stage by day for this one
    pass