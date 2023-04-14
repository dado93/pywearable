"""
This module contains all the functions related to analysis
of Labfront sleep data.
"""

import pylabfront.data
import pylabfront.utils
import pandas as pd

_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_DEEP_SLEEP_MS_COL = 'deepSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_LIGHT_SLEEP_MS_COL = 'lightSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_AWAKE_SLEEP_MS_COL = 'awakeDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_SLEEP_QUALITY_COL = 'overallSleepScore'

_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL = 'calendarDate'


def get_rem_sleep(data_path, start_dt, end_dt, participant_id="all"):
    """Get REM sleep time for each day.

    This function returns the absolute time spent in REM stage for
    the given participant(s) for each given day from start_dt to
    end_dt.

    Args:
        data_path (_type_): Path to data folder.
        start_dt (_type_): _description_
        end_dt (_type_): _description_
        participant_id (str, optional): _description_. Defaults to "all".
    """
    rem_dict = {}
    if participant_id == "all":
        # Get all participant ids automatically
        participant_id = [k+"_"+v for k,v in pylabfront.utils.get_ids(data_path,return_dict=True).items()]
    
    for participant in participant_id: 
        # Load sleep summary data
        participant_sleep_summary = pylabfront.data.load_garmin_connect_sleep_summary(data_path, participant,
                                                                          start_dt, end_dt)
        # Get REM 
        if len(participant_sleep_summary) > 0:
            rem_dict[participant] = pd.Series(participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL].values, 
                                              index=participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL]).to_dict()
        
    return rem_dict