"""
This module contains all the functions related to the analysis
of Labfront activity data.
"""

import pylabfront.utils as utils
import pandas as pd

from datetime import datetime,timedelta


_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_FOLDER = "garmin-connect-daily-summary"
_LABFRONT_GARMIN_CONNECT_EPOCH_FOLDER = "garmin-connect-epoch"

_LABFRONT_ISO_DATE_KEY = 'isoDate'
_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL = "intensity"
_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL = "activeTimeInMs"

_MS_TO_HOURS_CONVERSION = 1000*60*60
_MS_TO_MINUTES_CONVERSION = 1000*60


def get_activity_by_period(loader, activity, start_dt, end_dt, participant_ids="all"):

    activity_dict = {}

    if participant_ids == "all":
        participant_ids = loader.get_user_ids()

    if isinstance(participant_ids, str):
        participant_ids = [participant_ids]

    if not isinstance(participant_ids, list):
        raise TypeError("participant_ids has to be a list.")

    for participant_id in participant_ids:
        try:
            df = loader.load_garmin_connect_epoch(participant_id,start_dt,end_dt-timedelta(minutes=15))
            activity_dict[participant_id] = pd.Series(df[df[_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL] == activity][_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].values,
                                                      index= df[df.intensity == activity].isoDate)
        except:
            activity_dict[participant_id] = None

    return activity_dict

def get_active(loader, start_dt, end_dt, participant_ids="all"):
    return get_activity_by_period(loader, "ACTIVE", start_dt, end_dt, participant_ids)

def get_highly_active(loader, start_dt, end_dt, participant_ids="all"):
    return get_activity_by_period(loader, "HIGHLY_ACTIVE", start_dt, end_dt, participant_ids)

def get_sedentary(loader, start_dt, end_dt, participant_ids="all"):
    return get_activity_by_period(loader, "SEDENTARY", start_dt, end_dt, participant_ids)


def get_avg_daily_activities(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """Create a dictionary reporting for every participant of interest
    the mean amount of daily time spent per activity level during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list, optional): List of participants of interest. Defaults to "all".
        raturn_as_ratio (bool, optional): Indication of whather the values returned should be in ratio form. Defaults to False.

    Returns:
        dict: Dictionary of participants activities duration in minutes (or ratio).
        If there was no data for a participant for the period of interest, the value is None.
    """

    activities_dict = {}

    if participant_ids == "all":
        participant_ids = loader.get_user_ids()

    if isinstance(participant_ids, str):
        participant_ids = [participant_ids]
    
    if not isinstance(participant_ids, list):
        raise TypeError("participant_ids has to be a list.")
    
    for participant_id in participant_ids:
        try:
            # get data for the period desired
            df = loader.load_garmin_connect_epoch(participant_id,start_dt,end_dt-timedelta(minutes=15))
            if len(df) == 0:
                raise Exception
            df["date"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.date())
            # group per date and type of activity
            df = df.groupby(["date",_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL])[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].sum().reset_index()
            if return_as_ratio:
                time_collected_per_day = df.groupby(["date"])[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].sum().reset_index()
                # pivot the data so to be in dimensions that allow for division with pandas funcs
                activity_durations_per_day = df.pivot(index="date",columns=_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL,values=_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL).reset_index()
                ratio_df = (activity_durations_per_day.iloc[:,1:].div(time_collected_per_day.activeTimeInMs,axis=0)*100).fillna(0)
                activities_dict[participant_id] = ratio_df.mean().round(1)
            else:
                activities_dict[participant_id] = round(df.groupby([_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL])[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].mean() / _MS_TO_MINUTES_CONVERSION, 1)
        except:
            activities_dict[participant_id] = None

    return activities_dict

def get_avg_daily_sedentary(loader, start_dt=None, end_dt=None, participant_ids="all", return_as_ratio=False):
    """Create a dictionary reporting for every participant of interest 
    the amount of time spent sedentary during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Indication of whather the values returned should be in ratio form. Defaults to False.

    Returns:
        dict: Dictionary of participants' sedentary activity during the day in minutes (or ratio).
        If there was no data or sedentary time for a participant, the value is None.
    """
    activities_dict = get_avg_daily_activities(loader, start_dt, end_dt, participant_ids, return_as_ratio)
    sedentary_dict = {}

    for participant_id in activities_dict.keys():
        partecipant_activities = activities_dict[participant_id]
        try:
            sedentary_dict[participant_id] = partecipant_activities.get("SEDENTARY",0)
        except:     
            sedentary_dict[participant_id] = None

    return sedentary_dict

def get_avg_daily_active(loader, start_dt=None, end_dt=None, participant_ids="all", return_as_ratio=False):
    """Create a dictionary reporting for every participant of interest 
    the amount of time spent active during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Indication of whather the values returned should be in ratio form. Defaults to False.
        
    Returns:
        dict: Dictionary of active time per participant in minutes (or ratio).
        If there was no data or active time for a participant, the value is None.
    """
    activities_dict = get_avg_daily_activities(loader, start_dt, end_dt, participant_ids, return_as_ratio)
    active_dict = {}

    for participant_id in activities_dict.keys():
        partecipant_activities = activities_dict[participant_id]
        try:
            active_dict[participant_id] = partecipant_activities.get("ACTIVE",0)
        except:     
            active_dict[participant_id] = None

    return active_dict

def get_avg_daily_highly_active(loader, start_dt=None, end_dt=None, participant_ids="all", return_as_ratio=False):
    """Create a dictionary reporting for every participant of interest 
    the amount of time spent highly active during the period indicated

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Indication of whather the values returned should be in ratio form. Defaults to False.
        
    Returns:
        dict: Dictionary of active time per participant in minutes (or ratio).
        If there was no data or highly active time for a participant, the value is None.
    """
    activities_dict = get_avg_daily_activities(loader, start_dt, end_dt, participant_ids, return_as_ratio)
    highly_active_dict = {}

    for participant_id in activities_dict.keys():
        partecipant_activities = activities_dict[participant_id]
        try:
            highly_active_dict[participant_id] = partecipant_activities.get("HIGHLY_ACTIVE",0)
        except:     
            highly_active_dict[participant_id] = None

    return highly_active_dict

def get_avg_weekly_activities(loader, start_dt=None, end_dt=None, participant_ids="all"):
    """Creates a dictionary reporting for every participant of interest
    a DataFrame detailing the mean amount of time spent for activity level for
    every day of the week (0 to 6, 0 being Monday and 6 Sunday)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".

    Returns:
        dict: Dictionary of the weekly activities of the participants (as a DataFrame).
        If no activity was registered in the period of interest for a partecipant,
        values are None instead.
    """

    weekday_activities_dict = {}

    if participant_ids == "all":
        participant_ids = loader.get_user_ids()

    if isinstance(participant_ids, str):
        participant_ids = [participant_ids]

    if not isinstance(participant_ids, list):
        raise TypeError("participant_ids has to be a list.")

    for participant_id in participant_ids:
        try:
            # get data for that period
            df = loader.load_garmin_connect_epoch(participant_id,start_dt,end_dt-timedelta(minutes=15))
            if len(df) == 0:
                raise Exception
            # create columns to tell for each entry which day it is, both calendar date and weekday
            df["date"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.date())
            df["weekday"] = df[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.weekday())
            # calculate for every calendar date the total amount time for each activity
            df = df.groupby(["date", _LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL, "weekday"])[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].sum().reset_index() 
            # calculate for every weekday the mean amount of time for each activity
            df = df.groupby([_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL, "weekday"])[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].mean().reset_index()
            # make it more readable and transform MS to minutes
            df = df.pivot(index="weekday", columns=_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL, values=_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL) / _MS_TO_MINUTES_CONVERSION
            weekday_activities_dict[participant_id] = df.fillna(0).round(1)
        except:
            weekday_activities_dict[participant_id] = None

    return weekday_activities_dict

def get_avg_weekday_sedentary(loader, start_dt=None, end_dt=None, participant_ids="all"):
    pass

def get_avg_weekday_active():
    pass

def get_avg_weekend_sedentary():
    pass

def get_avg_weekend_active():
    pass


# partecipants, start_dt, end_dt -> dict k: part_id, v: return