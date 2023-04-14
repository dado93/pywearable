"""
This module contains all the functions related to analysis
of Labfront sleep data.
"""
import pandas as pd

_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_DEEP_SLEEP_MS_COL = 'deepSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_LIGHT_SLEEP_MS_COL = 'lightSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_AWAKE_SLEEP_MS_COL = 'awakeDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_SLEEP_QUALITY_COL = 'overallSleepScore'

_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL = 'calendarDate'


def get_rem_sleep(loader, start_date, end_date, participant_id="all"):
    """Get REM sleep time for each day.

    This function returns the absolute time spent in REM stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`): Start date from which REM data should be extracted.
        end_date (:class:`datetime.datetime`): End date from which REM data should be extracted.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    rem_dict = {}
    if participant_id == "all":
        # get all participant ids automatically
        participant_id = loader.get_user_ids()

    if isinstance(participant_id, str):
        participant_id = [participant_id]

    if not isinstance(participant_id, list):
        raise TypeError("participant_ids has to be a list.")
    
    for participant in participant_id: 
        # Load sleep summary data
        participant_sleep_summary = loader.load_garmin_connect_sleep_summary(participant, start_date, end_date)
        # Get REM 
        if len(participant_sleep_summary) > 0:
            rem_dict[participant] = pd.Series(participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL].values, 
                                              index=participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL]).to_dict()
        
    return rem_dict

def get_average_rem_sleep(loader, start_date, end_date, participant_id="all"):
    """Get average REM sleep time across time range.

    This function returns the average time spent in REM stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`): Start date from which REM data should be extracted.
        end_date (:class:`datetime.datetime`): End date from which REM data should be extracted.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    average_rem_dict = {}
    if participant_id == "all":
        # get all participant ids automatically
        participant_id = loader.get_user_ids()

    if isinstance(participant_id, str):
        participant_id = [participant_id]

    if not isinstance(participant_id, list):
        raise TypeError("participant_ids has to be a list.")
    
    for participant in participant_id: 
        # Load sleep summary data
        participant_sleep_summary = loader.load_garmin_connect_sleep_summary(participant, start_date, end_date)
        # Get average rem 
        if len(participant_sleep_summary) > 0:
            average_rem_dict[participant] = participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL].mean()
    return average_rem_dict