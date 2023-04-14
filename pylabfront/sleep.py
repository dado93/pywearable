"""
This module contains all the functions related to analysis
of Labfront sleep data.
"""
import numpy as np
import pandas as pd

_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_DEEP_SLEEP_MS_COL = 'deepSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_LIGHT_SLEEP_MS_COL = 'lightSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_AWAKE_SLEEP_MS_COL = 'awakeDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_SLEEP_QUALITY_COL = 'overallSleepScore'

_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_LIGHT_SLEEP_MS_COL = 'lightSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_DEEP_SLEEP_MS_COL = 'deepSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_SLEEP_MS_COL = 'awakeDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_MS_COL = 'unmeasurableSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL = 'durationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SCORE_COL = 'overallSleepScore'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL = 'calendarDate'

def get_sleep_summary_stage_by_day(loader, metric, start_date=None, end_date=None, participant_id="all"):
    """Get REM sleep time for each day.

    This function returns the absolute time spent in REM stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    data_dict = {}
    if participant_id == "all":
        # get all participant ids automatically
        participant_id = loader.get_user_ids()

    if isinstance(participant_id, str):
        participant_id = [participant_id]

    if not isinstance(participant_id, list):
        raise TypeError("participant_ids has to be a list.")
    if metric == 'REM':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL
    elif metric == 'LIGHT_SLEEP':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_LIGHT_SLEEP_MS_COL
    elif metric == 'DEEP_SLEEP':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_DEEP_SLEEP_MS_COL
    elif metric == 'AWAKE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_SLEEP_MS_COL
    elif metric == 'UNMEASURABLE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_MS_COL
    elif metric == 'DURATION':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL
    elif metric == 'SLEEP_SCORE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SCORE_COL
    else:
        raise ValueError("Invalid metric")

    for participant in participant_id: 
        # Load sleep summary data
        participant_sleep_summary = loader.load_garmin_connect_sleep_summary(participant, start_date, end_date)
        if len(participant_sleep_summary) > 0:
            data_dict[participant] = pd.Series(participant_sleep_summary[column].values, 
                                              index=participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL]).to_dict()
        
    return data_dict

def get_sleep_summary_stage_average(loader, metric, start_date=None, end_date=None, participant_id="all"):
    data_dict = get_sleep_summary_stage_by_day(loader, metric, start_date, end_date, participant_id="all")
    average_dict = {}
    for participant in data_dict.keys():
        average_dict[participant] = np.array(list(data_dict[participant].values())).mean()
    return average_dict

def get_rem_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get REM sleep time for each day.

    This function returns the absolute time spent in REM stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "REM", start_date, end_date, participant_id)

def get_average_rem_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average REM sleep time across time range.

    This function returns the average time spent in REM stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_average(loader, "REM", start_date, end_date, participant_id)

def get_light_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get light sleep time for each day.

    This function returns the absolute time spent in light stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "LIGHT_SLEEP", start_date, end_date, participant_id)

def get_average_light_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average light sleep time across time range.

    This function returns the average time spent in light sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_average(loader, "LIGHT_SLEEP", start_date, end_date, participant_id)

def get_deep_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get deep sleep time for each day.

    This function returns the absolute time spent in deep sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "DEEP_SLEEP", start_date, end_date, participant_id)

def get_average_deep_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average deep sleep time across time range.

    This function returns the average time spent in deep sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which deep sleep data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which deep sleep data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_average(loader, "DEEP_SLEEP", start_date, end_date, participant_id)

def get_awake_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get awake sleep time for each day.

    This function returns the absolute time spent in awake stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which awake sleep data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which awake sleep data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "AWAKE", start_date, end_date, participant_id)

def get_average_awake_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average wake sleep time across time range.

    This function returns the average time spent in deep sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which awake sleep data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which awake sleep data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    
    Return:
        dict: average awake sleep.
    """
    return get_sleep_summary_stage_average(loader, "AWAKE", start_date, end_date, participant_id)

def get_sleep_duration(loader, start_date=None, end_date=None, participant_id="all"):
    """Get sleep duration for each day.

    This function returns the total sleep duration for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which total sleep duration should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which total sleep duration should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Total sleep duration by participant and by day.
    """
    return get_sleep_summary_stage_by_day(loader, "DURATION", start_date, end_date, participant_id)

def get_average_sleep_duration(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average sleep duration across time range.

    This function returns the average sleep duration for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep duration should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep duration should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    
    Return:
        dict: average awake sleep.
    """
    return get_sleep_summary_stage_average(loader, "DURATION", start_date, end_date, participant_id)

def get_sleep_score(loader, start_date=None, end_date=None, participant_id="all"):
    """Get sleep score for each day.

    This function returns the sleep score for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep score should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep score should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Sleep score by participant and by day.
    """
    return get_sleep_summary_stage_by_day(loader, "SLEEP_SCORE", start_date, end_date, participant_id)

def get_average_sleep_score(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average sleep score across time range.

    This function returns the average sleep score for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep score should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep score should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    
    Return:
        dict: Average sleep score by participant.
    """
    return get_sleep_summary_stage_average(loader, "SLEEP_SCORE", start_date, end_date, participant_id)