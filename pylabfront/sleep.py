"""
This module contains all the functions related to analysis
of Labfront sleep data.
"""

import data
import utils

_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_DEEP_SLEEP_MS_COL = 'deepSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_LIGHT_SLEEP_MS_COL = 'lightSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_AWAKE_SLEEP_MS_COL = 'awakeDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_SLEEP_QUALITY_COL = 'overallSleepScore'

def get_rem_sleep(data_path, start_dt, end_dt, participant_id="all"):
    """Get REM sleep time for each day.

    This function returns the absolute time spent in REM stage for
    the given participant(s).

    Args:
        data_path (_type_): Path to data folder.
        start_dt (_type_): _description_
        end_dt (_type_): _description_
        participant_id (str, optional): _description_. Defaults to "all".
    """
    rem_dict = {}
    if participant_ids == "all":
        # Get all participant ids automatically
        participant_ids = [k+"_"+v for k,v in utils.get_ids(data_path,return_dict=True).items()]

    for participant in participant_id:
        # Load sleep summary data
        # Get REM 
        pass