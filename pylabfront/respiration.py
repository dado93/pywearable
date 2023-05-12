"""
This module contains all the functions related to analysis
of Labfront respiration data.
"""
import datetime
import numpy as np
import pandas as pd

import pylabfront.utils as utils

_LABFRONT_RESPIRATION_COLUMN = "breathsPerMinute"


def get_breaths_per_minute(
    loader,
    day_or_night=None,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False,
    remove_zero=False,
):
    """Get breaths per minute.

    This function returns the breaths per minute computed per
    each day or night. Depending on whether the `day_or_night` parameter
    is set to 'DAY' or 'NIGHT', the average value is computed for daily
    data or for sleep data, respectively.

    Parameters
    ----------
    loader: :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    day_or_night: :class:`str`, optionional
        Whether to compute breath per minute only during waking or rest states, or during both, by default None.
        If set to 'DAY', compute average breaths per minute in waking state.
        If set to 'NIGHT', compute average breaths per minute in rest state.
        If None, compute average breaths per minute across waking and rest states
    start_date: :class:`datetime.datetime`, optional
        Start date from which breaths per minute must be computed, by default None.
    end_date: :class:`datetime.datetime`, optional
        End date to which breaths per minute must be computed, by default None.
    user_id: :class:`str`, optional
        ID of the user for which breaths per minute must be computed, by default "all".
    average: :class:`bool`, option
        Whether to return the average across days/nights or return the average per day/night.
    remove_zero: :class:`bool`, option
        Whether to remove data with breathsPerMinute equal to 0 from the data.

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """

    user_id = utils.get_user_ids(loader, user_id)

    data_dict = {}
    if average:
        average_dict = {}

    for user in user_id:
        try:
            respiratory_data = loader.load_garmin_connect_respiration(
                user, start_date=start_date, end_date=end_date
            )
            if remove_zero:
                respiratory_data = respiratory_data[
                    respiratory_data[_LABFRONT_RESPIRATION_COLUMN] > 0
                ]
            if day_or_night == "DAY":
                respiratory_data = respiratory_data[respiratory_data.sleep == 0]
            elif day_or_night == "NIGHT":
                respiratory_data = respiratory_data[respiratory_data.sleep == 1]
            if len(respiratory_data) > 0:
                data_dict[user] = (
                    respiratory_data.groupby(
                        respiratory_data[loader.date_column].dt.date
                    )[_LABFRONT_RESPIRATION_COLUMN]
                    .mean()
                    .to_dict()
                )
                if average:
                    respiration_data_df = pd.DataFrame.from_dict(
                        data_dict[user], orient="index"
                    )
                    average_dict[user] = {}
                    average_dict[user]["values"] = np.nanmean(
                        np.array(list(data_dict[user].values()))
                    )
                    average_dict[user]["days"] = [
                        datetime.datetime.strftime(x, "%Y-%m-%d")
                        for x in respiration_data_df.index
                    ]
        except:
            data_dict[user] = None
    if average:
        return average_dict
    return data_dict


def get_rest_breaths_per_minute(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False,
    remove_zero=False,
):
    """Get rest breaths per minute.

    Parameters
    ----------
        loader: :class:`pylabfront.loader.LabfrontLoader`
            Instance of `LabfrontLoader`.
        start_date: class:`datetime.datetime`, optional
            Start date from which breaths per minute must be computed, by default None.
        end_date: :class:`datetime.datetime`, optional
            End date to which breaths per minute must be computed, by default to None.
        user_id: :class:`str`
            ID of the user for which breaths per minute must be computed, by default "all".
        average: :class:`bool`, optional
            Whether to average the breaths per minute over the timerange, by default false.
            If set to `True`, then the breaths per minute are averaged across the timerange,
            thus returing a dictionary with the average breaths per minute and the valid days
            over which the average was computed. If set to `False`, the dictionary contains
            the breaths per minute value for each day.
        remove_zero: :class:`bool`, option
            Whether to remove data with breathsPerMinute equal to 0 from the data.

    Returns
    -------
        :class:`dict`
        Dictionary with user id as primary key, calendar days as secondary keys, and breaths per minute as value.
    """
    return get_breaths_per_minute(
        loader,
        day_or_night="NIGHT",
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        average=average,
        remove_zero=remove_zero,
    )


def get_waking_breaths_per_minute(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False,
    remove_zero=False,
):
    """Get average waking breaths per minute across timerange.

    Parameters
    ----------
        loader: :class:`pylabfront.loader.Loader`
            Instance of `LabfrontLoader`.
        start_date: :class:`datetime.datetime`, optional
            Start date from which breaths per minute must be computed, by default None.
        end_date :class:`datetime.datetime`, optional
            End date to which breaths per minute must be computed, by default None.
        participant_id :class:`str`, optional
            ID of the user for which breaths per minute must be computed, by default "all".
        average: :class:`bool`, optional
            Whether to average the breaths per minute over the timerange, by default false.
            If set to `True`, then the breaths per minute are averaged across the timerange,
            thus returing a dictionary with the average breaths per minute and the valid days
            over which the average was computed. If set to `False`, the dictionary contains
            the breaths per minute value for each day.
        remove_zero: :class:`bool`, option
            Whether to remove data with breathsPerMinute equal to 0 from the data.

    Returns:
        dict: Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """
    return get_breaths_per_minute(
        loader,
        day_or_night="DAY",
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        average=average,
        remove_zero=remove_zero,
    )
