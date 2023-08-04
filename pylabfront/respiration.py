"""
This module contains all the functions related to analysis
of Labfront respiration data.
"""
import datetime
import numpy as np
import pandas as pd
from typing import Union

import pylabfront.utils as utils
from . import loader

_RESPIRATION_DAY = "DAY"
_RESPIRATION_NIGHT = "NIGHT"


def get_breaths_per_minute(
    labfront_loader: loader.LabfrontLoader,
    day_or_night: Union[str, None] = None,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
    user_id: Union[str, list] = "all",
    average: bool = False,
    remove_zero: bool = False,
    return_days: bool = False,
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
    average: :class:`bool`, optional
        Whether to return the average across days/nights or return the average per day/night, by default False.
    remove_zero: :class:`bool`, optional
        Whether to remove data with breathsPerMinute equal to 0 from the data, by default False.
    return_days: :class:`bool`, optional
        Whether to return the days over which the average value was computed, by default False.

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """

    user_id = utils.get_user_ids(labfront_loader, user_id)

    data_dict = {}
    if average:
        average_dict = {}

    for user in user_id:
        try:
            respiratory_data = labfront_loader.load_garmin_connect_respiration(
                user, start_date=start_date, end_date=end_date
            )
            if remove_zero:
                respiratory_data = respiratory_data[
                    respiratory_data[loader._LABFRONT_RESPIRATION_COLUMN] > 0
                ]
            if day_or_night == _RESPIRATION_DAY:
                respiratory_data = respiratory_data[respiratory_data.sleep == 0]
            elif day_or_night == _RESPIRATION_NIGHT:
                respiratory_data = respiratory_data[respiratory_data.sleep == 1]

            if len(respiratory_data) > 0:
                if day_or_night == _RESPIRATION_DAY:
                    respiratory_data["Date"] = respiratory_data[
                        labfront_loader.date_column
                    ].dt.date
                    data_dict[user] = (
                        respiratory_data.groupby("Date")[
                            loader._LABFRONT_RESPIRATION_COLUMN
                        ]
                        .mean()
                        .to_dict()
                    )
                else:
                    respiratory_data["Date"] = respiratory_data[
                        loader._LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATE_COL
                    ].dt.date
                    data_dict[user] = (
                        respiratory_data.groupby("Date")[
                            loader._LABFRONT_RESPIRATION_COLUMN
                        ]
                        .mean()
                        .to_dict()
                    )
                if average:
                    respiration_data_df = pd.DataFrame.from_dict(
                        data_dict[user], orient="index"
                    )
                    average_dict[user] = {}
                    if return_days:
                        average_dict[user]["values"] = np.nanmean(
                            np.array(list(data_dict[user].values()))
                        )
                        average_dict[user]["days"] = [
                            datetime.datetime.strftime(x, "%Y-%m-%d")
                            for x in respiration_data_df.index
                        ]
                    else:
                        average_dict[user] = np.nanmean(
                            np.array(list(data_dict[user].values()))
                        )
        except:
            data_dict[user] = None
    if average:
        return average_dict
    return data_dict


def get_rest_breaths_per_minute(
    loader: loader.LabfrontLoader,
    start_date: Union[datetime.datetime, datetime.date, None] = None,
    end_date: Union[datetime.datetime, datetime.date, None] = None,
    user_id: str = "all",
    average: bool = False,
    remove_zero: bool = False,
    return_days: bool = False,
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
        remove_zero: :class:`bool`, optional
            Whether to remove data with breathsPerMinute equal to 0 from the data, by default False.
        return_days: :class:`bool`, optional
            Whether to return the days over which the average value was computed, by default False.

    Returns
    -------
        :class:`dict`
        Dictionary with user id as primary key, calendar days as secondary keys, and breaths per minute as value.
    """
    return get_breaths_per_minute(
        loader,
        day_or_night=_RESPIRATION_NIGHT,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        average=average,
        remove_zero=remove_zero,
        return_days=return_days,
    )


def get_waking_breaths_per_minute(
    loader: loader.LabfrontLoader,
    start_date: Union[datetime.datetime, datetime.date, None] = None,
    end_date: Union[datetime.datetime, datetime.date, None] = None,
    user_id: str = "all",
    average: bool = False,
    remove_zero: bool = False,
    return_days: bool = False,
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
        remove_zero: :class:`bool`, optional
            Whether to remove data with breathsPerMinute equal to 0 from the data, by default False.
        return_days: :class:`bool`, optional
            Whether to return the days over which the average value was computed, by default False.

    Returns:
        dict: Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """
    return get_breaths_per_minute(
        loader,
        day_or_night=_RESPIRATION_DAY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        average=average,
        remove_zero=remove_zero,
        return_days=return_days,
    )
