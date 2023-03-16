"""
This module contains all the functions related to handling of data from Labfront.
"""
import utils


_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'

_LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-heart-rate'
_LABFRONT_GARMIN_CONNECT_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-pulse-ox'
_LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-pulse-ox'

_LABFRONT_GARMIN_DEVICE_HEART_RATE_KEY = _LABFRONT_GARMIN_DEVICE_STRING + '-heart-rate'

def load_garmin_connect_heart_rate(data_path, participant_id, start_date=None, end_date=None):
    data = utils.get_data_from_datetime(data_path, participant_id, _LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING, 
                                            start_date, end_date)
    return data

def load_garmin_connect_pulse_ox():
    pass