"""
This module contains all the functions related to handling of data from Labfront.
"""
import pandas as pd

import pylabfront.utils as utils

# Garmin Connect metrics - Labfront folder names
_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_CONNECT_BODY_COMPOSITION_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-body-composition'
_LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-heart-rate'
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-summary'
_LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-pulse-ox'
_LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-pulse-ox'
_LABFRONT_SPO2_COLUMN = 'spo2'
_LABFRONT_GARMIN_CONNECT_DAILY_RESPIRATION_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-respiration'
_LABFRONT_GARMIN_CONNECT_SLEEP_RESPIRATION_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-respiration'
_LABFRONT_RESPIRATION_COLUMN = 'breathsPerMinute'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-stage'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-summary'

# Garmin device metrics - Labfront folder names
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'
_LABFRONT_GARMIN_DEVICE_BBI_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-bbi'
_LABFRONT_GARMIN_DEVICE_HEART_RATE_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-heart-rate'
_LABFRONT_GARMIN_DEVICE_PULSE_OX_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-pulse-ox'
_LABFRONT_GARMIN_DEVICE_RESPIRATION_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-respiration'
_LABFRONT_GARMIN_DEVICE_STEP_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-step'
_LABFRONT_GARMIN_DEVICE_STRESS_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-stress'

def load_garmin_connect_heart_rate(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect heart rate data.

    This function loads Garmin Connect heart rate data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect heart rate data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_connect_pulse_ox(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect pulse ox data.

    This function loads Garmin Connect pulse ox data from a given
    participant and within a specified date and time range. This
    function loads both daily and sleep pulse ox data. The 
    resulting data frame contains an additional column named 'sleep',
    equal to 1 for pulse ox data acquired during sleep.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect pulse ox data.
    """
    # We need to load both sleep and daily pulse ox
    daily_data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING, 
                                            start_date, end_date).reset_index(drop=True)
    # Add sleep label to sleep pulse ox
    sleep_data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING, 
                                            start_date, end_date).reset_index(drop=True)
    if len(sleep_data) > 0:
        sleep_data.loc[:,'sleep'] = 1
    # Merge dataframes
    merged_data = pd.merge(daily_data, sleep_data, on=utils._LABFRONT_ISO_DATE_KEY, how='left')
    merged_data.loc[:,_LABFRONT_SPO2_COLUMN] = merged_data[_LABFRONT_SPO2_COLUMN + '_x']
    merged_data = merged_data.drop([_LABFRONT_SPO2_COLUMN + '_x', _LABFRONT_SPO2_COLUMN + '_y'], axis=1)
    return merged_data

def load_garmin_connect_respiration(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect respiratory data.

    This function loads Garmin Connect respiratory data from a given
    participant and within a specified date and time range. This
    function loads both daily and sleep respiratory data. The 
    resulting data frame contains an additional column named 'sleep',
    equal to 1 for respiratory data acquired during sleep.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect respiration data.
    """
    # We need to load both sleep and daily pulse ox
    daily_data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_DAILY_RESPIRATION_STRING, 
                                            start_date, end_date).reset_index(drop=True)
    # Add sleep label to sleep pulse ox
    sleep_data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_RESPIRATION_STRING, 
                                            start_date, end_date).reset_index(drop=True)
    if len(sleep_data) > 0:
        sleep_data.loc[:,'sleep'] = 1
    # Merge dataframes
    merged_data = pd.merge(daily_data, sleep_data, on=utils._LABFRONT_ISO_DATE_KEY, how='left')
    merged_data.loc[:,_LABFRONT_RESPIRATION_COLUMN] = merged_data[_LABFRONT_RESPIRATION_COLUMN + '_x']
    merged_data = merged_data.drop([_LABFRONT_RESPIRATION_COLUMN + '_x', _LABFRONT_RESPIRATION_COLUMN + '_y'], axis=1)
    return merged_data

def load_garmin_connect_sleep_stage(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect sleep stage data.

    This function loads Garmin Connect sleep stage data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect sleep stage data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_connect_sleep_summary(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect sleep summary data.

    This function loads Garmin Connect sleep summary data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect sleep summary data.
    """
    if _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING in utils.get_available_metrics(data_path, participant_id):
        data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING, 
                                            start_date, end_date)
    else:
        data = pd.DataFrame()
    return data

def load_garmin_connect_stress(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect stress data.

    This function loads Garmin Connect stress data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect stress data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_connect_stress(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect stress data.

    This function loads Garmin Connect stress data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect stress data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_device_heart_rate(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin device heart rate data.

    This function loads Garmin device heart rate data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin device heart rate data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_DEVICE_HEART_RATE_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_device_pulse_ox(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin device pulse ox data.

    This function loads Garmin device pulse ox data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin device pulse ox data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_DEVICE_PULSE_OX_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_device_respiration(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin device respiratory data.

    This function loads Garmin device respiratory data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin device respiratory data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_DEVICE_RESPIRATION_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_device_step(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin device step data.

    This function loads Garmin device step data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin device step data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_DEVICE_STEP_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_device_stress(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin device stress data.

    This function loads Garmin device stress data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin device stress data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_DEVICE_STRESS_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_device_stress(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin device stress data.

    This function loads Garmin device stress data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin device stress data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_DEVICE_STRESS_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_device_bbi(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin device BBI data.

    This function loads Garmin device beat-to-beat interval (BBI) data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin device BBI data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_DEVICE_BBI_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_connect_body_composition(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect body composition data.

    This function loads Garmin Connect body composition data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect body composition data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_BODY_COMPOSITION_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_connect_daily_summary(data_path, participant_id, start_date=None, end_date=None):
    """Load Garmin Connect daily summary data.

    This function loads Garmin Connect daily summary data from a given
    participant and within a specified date and time range.

    Args:
        data_path (str): Path to the folder containing Labfront data.
        participant_id (str): Full ID of the participant
        start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
        end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

    Returns:
        pd.DataFrame: Dataframe containing Garmin Connect daily summary data.
    """
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STRING, 
                                            start_date, end_date)
    return data