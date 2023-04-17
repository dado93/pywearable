"""
This module contains all the functions related to analysis
of Labfront respiration data.
"""

import numpy as np

def get_breaths_per_minute_per_day(loader, day_or_night=None, start_date=None, end_date=None, participant_id="all"):
    """Get average breaths per minute per day/night.

    This function returns the average breaths per minute computed per 
    each day or night. Depending on whether the `day_or_night` parameter
    is set to 'DAY' or 'NIGHT', the average value is computed for daily
    data or for sleep data, respectively.

    Args:
        loader (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        day_or_night (str, option): If 'DAY', compute average breaths per minute in waking state. 
                                    If 'NIGHT', compute average breaths per minute in rest state.
                                    If None, compute average breaths per minute across waking and rest states.
                                    Defaults to None.
        start_date (class:`datetime.datetime`, optional): Start date from which breaths per minute must be computed. Defaults to None.
        end_date (class:`datetime.datetime`, optional): End date to which breaths per minute must be computed. Defaults to None.
        participant_id (str, optional): ID of the participant for which breaths per minute must be computed. Defaults to "all".

    Returns:
        dict: Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """

    data_dict = {}
    if participant_id == "all":
        # get all participant ids automatically
        participant_id = loader.get_user_ids()

    if isinstance(participant_id, str):
        participant_id = [participant_id]

    for participant in participant_id: 
        try:
            respiratory_data = loader.load_garmin_connect_respiration(participant, start_date, end_date)
            if day_or_night == "DAY":
                respiratory_data = respiratory_data[respiratory_data.sleep == 0]
            elif day_or_night == "NIGHT":
                respiratory_data = respiratory_data[respiratory_data.sleep == 1]
            if len(respiratory_data) > 0:
                data_dict[participant] = respiratory_data.groupby(respiratory_data[loader.date_column].dt.date)[loader.respiratorion_column].mean().to_dict()
        except:
            data_dict[participant] = None
    return data_dict

def get_average_breaths_per_minute(loader, day_or_night=None, start_date=None, end_date=None, participant_id="all"):
    """"Get average breaths per minute across timerange.

    This function returns the average breaths per minute computed per 
    each day or night. Depending on whether the `day_or_night` parameter
    is set to 'DAY' or 'NIGHT', the average value is computed for daily
    data or for sleep data, respectively.

    Args:
        loader (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        day_or_night (str, optional): If 'DAY', compute average breaths per minute in waking state. 
                                    If 'NIGHT', compute average breaths per minute in rest state.
                                    If None, compute average breaths per minute across waking and rest states.
                                    Defaults to None.
        start_date (class:`datetime.datetime`, optional): Start date from which breaths per minute must be computed. Defaults to None.
        end_date (class:`datetime.datetime`, optional): End date to which breaths per minute must be computed. Defaults to None.
        participant_id (str, optional): ID of the participant for which breaths per minute must be computed. Defaults to "all".

    Returns:
        dict: Dictionary with participant id as key, and average breaths per minute as value.
    """
    data_dict = get_breaths_per_minute_per_day(loader, day_or_night, start_date, end_date, participant_id)
    average_dict = {}
    for participant in data_dict.keys():
        average_dict[participant] = np.array(list(data_dict[participant].values())).mean()
    return average_dict

def get_average_rest_breaths_per_minute_per_night(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average rest breaths per minute per night.

    This function computes the average breaths per minute per each night from 
    `start_date` to `end_date` and returns the average computed per
    each night. If no data are found for the `participant_id`, then the
    value is set to None.

    Args:
        loader (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (class:`datetime.datetime`, optional): Start date from which breaths per minute must be computed. Defaults to None.
        end_date (class:`datetime.datetime`, optional): End date to which breaths per minute must be computed. Defaults to None.
        participant_id (str, optional): ID of the participant for which breaths per minute must be computed. Defaults to "all".

    Returns:
        dict: Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """
    return get_breaths_per_minute_per_day(loader, day_or_night="NIGHT", start_date=start_date, end_date=end_date, participant_id=participant_id)

def get_average_waking_breaths_per_minute_per_day(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average rest breaths per minute per day.

    This function computes the average breaths per minute per each day from 
    `start_date` to `end_date` and returns the average computed per
    each day. This function does not consider sleep data for the 
    computaiton. If no data are found for the `participant_id`, then the
    value is set to None.

    Args:
        loader (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (class:`datetime.datetime`, optional): Start date from which breaths per minute must be computed. Defaults to None.
        end_date (class:`datetime.datetime`, optional): End date to which breaths per minute must be computed. Defaults to None.
        participant_id (str, optional): ID of the participant for which breaths per minute must be computed. Defaults to "all".

    Returns:
        dict: Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """
    return get_breaths_per_minute_per_day(loader, day_or_night="DAY", start_date=start_date, end_date=end_date, participant_id=participant_id)

def get_average_rest_breaths_per_minute(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average rest breaths per minute across timerange.

    Args:
        loader (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (class:`datetime.datetime`, optional): Start date from which breaths per minute must be computed. Defaults to None.
        end_date (class:`datetime.datetime`, optional): End date to which breaths per minute must be computed. Defaults to None.
        participant_id (str, optional): ID of the participant for which breaths per minute must be computed. Defaults to "all".

    Returns:
        dict: Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """
    return get_average_breaths_per_minute(loader, day_or_night="NIGHT", start_date=start_date, end_date=end_date, participant_id=participant_id)

def get_average_waking_breaths_per_minute(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average waking breaths per minute across timerange.

    Args:
        loader (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (class:`datetime.datetime`, optional): Start date from which breaths per minute must be computed. Defaults to None.
        end_date (class:`datetime.datetime`, optional): End date to which breaths per minute must be computed. Defaults to None.
        participant_id (str, optional): ID of the participant for which breaths per minute must be computed. Defaults to "all".

    Returns:
        dict: Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """
    return get_average_breaths_per_minute(loader, day_or_night="DAY", start_date=start_date, end_date=end_date, participant_id=participant_id)