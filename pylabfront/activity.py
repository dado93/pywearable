"""
This module contains all the functions related to the analysis
of Labfront activity data.
"""

import pylabfront.utils as utils
import pandas as pd
import numpy as np

from datetime import timedelta

_LABFRONT_ISO_DATE_KEY = 'isoDate'
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL = 'calendarDate'
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_COL = 'steps'
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL = "distanceInMeters"
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

def get_steps_per_day(loader, start_dt=None, end_dt=None, participant_ids="all",average=False):
    """Get steps for each day.

    This function returns the total daily steps for the given participant(s) 
    for each given day from ``start_date`` to ``end_date``

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_dt (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_dt (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list, optional): List of participants of interest. Defaults to "all".
        average (bool, optional): Indication whather to calculate the average. Defaults to False.

    Returns:
        dict: Dictionary of daily number of steps for participants of interest
    """

    data_dict = {}
    if participant_ids == "all":
        participant_ids = loader.get_user_ids()

    if isinstance(participant_ids, str):
        participant_ids = [participant_ids]

    for participant_id in participant_ids: 
        participant_daily_summary = loader.load_garmin_connect_daily_summary(participant_id, start_dt, end_dt-timedelta(minutes=15))
        if len(participant_daily_summary) > 0:
            if average:
                data_dict[participant_id] = int(participant_daily_summary[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_COL].values.mean())
            else:
                data_dict[participant_id] = pd.Series(participant_daily_summary[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STEPS_COL].values, 
                                              index=participant_daily_summary[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL]).to_dict()
        else:
            data_dict[participant_id] = None
        
    return data_dict

def get_distance_per_day(loader, start_dt=None, end_dt=None, participant_ids="all",average=False):
    """Get distance covered for each day.

    This function returns the amount of meters covered for the given participant(s) 
    for each given day from ``start_date`` to ``end_date``

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_dt (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_dt (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list, optional): List of participants of interest. Defaults to "all".
        average (bool, optional): Indication whather to calculate the average. Defaults to False.

    Returns:
        dict: Dictionary of daily meters covered by participants of interest
    """
    data_dict = {}
    if participant_ids == "all":
        participant_ids = loader.get_user_ids()

    if isinstance(participant_ids, str):
        participant_ids = [participant_ids]

    for participant_id in participant_ids: 
        participant_daily_summary = loader.load_garmin_connect_daily_summary(participant_id, start_dt, end_dt-timedelta(minutes=15))
        if len(participant_daily_summary) > 0:
            if average:
                data_dict[participant_id] = int(participant_daily_summary[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL].values.mean())
            else:
                data_dict[participant_id] = pd.Series(participant_daily_summary[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_DISTANCE_COL].values, 
                                              index=participant_daily_summary[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DAY_COL]).to_dict()
        else:
            data_dict[participant_id] = None

    return data_dict

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

def get_avg_weekly_activities(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """Creates a dictionary reporting for every participant of interest
    a DataFrame detailing the mean amount of time spent for activity level for
    every day of the week (0 to 6, 0 being Monday and 6 Sunday)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.
        
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
            if return_as_ratio:
                activity_df = df.pivot(index=["date","weekday"],
                                       columns=_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL,
                                         values=_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL).reset_index()
                time_collected_df = df.groupby(["date"])[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].sum().reset_index()
                ratio_df = pd.concat([activity_df.iloc[:,2:].div(time_collected_df[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL],axis=0).fillna(0),
                                      activity_df.weekday],axis=1)
                weekday_activities_dict[participant_id] = (ratio_df.groupby("weekday").mean()*100).round(1)
            else:       
                # calculate for every weekday the mean amount of time for each activity
                df = df.groupby([_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL, "weekday"])[_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL].mean().reset_index()
                # make it more readable and transform MS to minutes
                df = df.pivot(index="weekday", columns=_LABFRONT_GARMIN_CONNECT_EPOCH_INTENSITY_COL, values=_LABFRONT_GARMING_CONNECT_EPOCH_ACTIVE_TIME_MS_COL) / _MS_TO_MINUTES_CONVERSION
                weekday_activities_dict[participant_id] = df.fillna(0).round(1)
        except:
            weekday_activities_dict[participant_id] = None

    return weekday_activities_dict

def get_avg_weekday_sedentary(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """ Get the daily average amount of time (in minutes) spent sedentary
    by participants of interest in a given time frame, for working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the 
        average daily amount of minutes spent sedentary.
    """

    avg_sedentary_dict = {}
 
    for k,v in get_avg_weekly_activities(loader,start_dt,end_dt,participant_ids,return_as_ratio).items():
        if v is None:
            avg_sedentary_dict[k] = None
        else:
            df = v.reset_index()
            avg_sedentary_dict[k] = round(df.loc[df.weekday.isin(range(0,5))].SEDENTARY.mean(),1)

    return avg_sedentary_dict


def get_avg_weekday_active(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """ Get the daily average amount of time (in minutes) spent active
    by participants of interest in a given time frame, for working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the 
        average daily amount of minutes spent active.
    """

    avg_active_dict = {}
 
    for k,v in get_avg_weekly_activities(loader,start_dt,end_dt,participant_ids,return_as_ratio).items():
        if v is None:
            avg_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_active_dict[k] = round(df.loc[df.weekday.isin(range(0,5))].ACTIVE.mean(),1)

    return avg_active_dict

def get_avg_weekday_highly_active(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """ Get the daily average amount of time (in minutes) spent highly active
    by participants of interest in a given time frame, for working days (Mon-Fri)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the 
        average daily amount of minutes spent highly active.
    """

    avg_highly_active_dict = {}
 
    for k,v in get_avg_weekly_activities(loader,start_dt,end_dt,participant_ids,return_as_ratio).items():
        if v is None:
            avg_highly_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_highly_active_dict[k] = round(df.loc[df.weekday.isin(range(0,5))].HIGHLY_ACTIVE.mean(),1)

    return avg_highly_active_dict

def get_avg_weekend_sedentary(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """ Get the daily average amount of time (in minutes) spent sedentary
    by participants of interest in a given time frame, during weekends (Sat/Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the 
        average daily amount of minutes spent sedentary, during weekends.
    """

    avg_sedentary_dict = {}
 
    for k,v in get_avg_weekly_activities(loader,start_dt,end_dt,participant_ids,return_as_ratio).items():
        if v is None:
            avg_sedentary_dict[k] = None
        else:
            df = v.reset_index()
            avg_sedentary_dict[k] = round(df.loc[~df.weekday.isin(range(0,5))].SEDENTARY.mean(),1)

    return avg_sedentary_dict

def get_avg_weekend_active(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """ Get the daily average amount of time (in minutes) spent active
    by participants of interest in a given time frame, for weekends (Sat/Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the 
        average daily amount of minutes spent active, during weekends.
    """

    avg_active_dict = {}
 
    for k,v in get_avg_weekly_activities(loader,start_dt,end_dt,participant_ids,return_as_ratio).items():
        if v is None:
            avg_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_active_dict[k] = round(df.loc[~df.weekday.isin(range(0,5))].ACTIVE.mean(),1)

    return avg_active_dict

def get_avg_weekend_highly_active(loader, start_dt=None, end_dt=None, participant_ids="all",return_as_ratio=False):
    """ Get the daily average amount of time (in minutes) spent highly active
    by participants of interest in a given time frame, for weekends (Sat/Sun)

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list): List of participants of interest. Defaults to "all".
        return_as_ratio (bool): Whather to return the amount of time as ratio or minutes. Defaults to False.

    Returns:
        dict: Dictionary reporting for every participant of interest the 
        average daily amount of minutes spent highly active, during weekends.
    """

    avg_highly_active_dict = {}
 
    for k,v in get_avg_weekly_activities(loader,start_dt,end_dt,participant_ids,return_as_ratio).items():
        if v is None:
            avg_highly_active_dict[k] = None
        else:
            df = v.reset_index()
            avg_highly_active_dict[k] = round(df.loc[~df.weekday.isin(range(0,5))].HIGHLY_ACTIVE.mean(),1)

    return avg_highly_active_dict