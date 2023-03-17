"""
This module contains all the functions related to handling of data from Labfront.
"""
import pandas as pd

import utils


_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'

_LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-heart-rate'
_LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-pulse-ox'
_LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-pulse-ox'

_LABFRONT_GARMIN_DEVICE_HEART_RATE_KEY = _LABFRONT_GARMIN_DEVICE_STRING + '-heart-rate'

def load_garmin_connect_heart_rate(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect heart rate data.

    This function loads Garmin Connect heart rate data from a given
    participant and withing a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (_type_, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect heart rate data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_connect_pulse_ox(data_path, participant_id, start_date=None, end_date=None):
    # We need to load both sleep and daily pulse ox (?)
    daily_data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING, 
                                            start_date, end_date).reset_index(drop=True)
    # Add sleep label to sleep pulse ox
    sleep_data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING, 
                                            start_date, end_date).reset_index(drop=True)
    sleep_data.loc[:,'sleep'] = 1
    # Merge dataframes
    merged_data = pd.merge(daily_data, sleep_data, on=utils._LABFRONT_ISO_DATE_KEY, how='left')
    merged_data.loc[:,'spo2'] = merged_data['spo2_x']
    merged_data = merged_data.drop(['spo2_x','spo2_y'], axis=1)
    return merged_data