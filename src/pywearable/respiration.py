"""
This module contains all the functions related to analysis
of Labfront respiration data.
"""
import datetime
from typing import Union

import numpy as np
import pandas as pd

from . import constants, utils
from .loader.base import BaseLoader

_RESPIRATION_DAY = "DAY"
_RESPIRATION_NIGHT = "NIGHT"


def get_breaths_per_minute(
    loader: BaseLoader,
    day_or_night: Union[str, None] = None,
    user_id: Union[str, list] = "all",
    start_date: datetime.datetime = None,
    end_date: datetime.datetime = None,
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
    day_or_night: :class:`str`, optional
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
                    respiratory_data[constants._RESPIRATION_BREATHS_PER_MINUTE_COL] > 0
                ]
            if day_or_night == _RESPIRATION_DAY:
                respiratory_data = respiratory_data[respiratory_data.sleep == 0]
            elif day_or_night == _RESPIRATION_NIGHT:
                respiratory_data = respiratory_data[respiratory_data.sleep == 1]

            if len(respiratory_data) > 0:
                if day_or_night == _RESPIRATION_DAY:
                    respiratory_data["Date"] = respiratory_data[
                        constants._ISODATE_COL
                    ].dt.date
                    data_dict[user] = (
                        respiratory_data.groupby("Date")[
                            constants._RESPIRATION_BREATHS_PER_MINUTE_COL
                        ]
                        .mean()
                        .to_dict()
                    )
                else:
                    data_dict[user] = (
                        respiratory_data.groupby(
                            constants._RESPIRATION_CALENDAR_DATE_COL
                        )[constants._RESPIRATION_BREATHS_PER_MINUTE_COL]
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
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, None] = None,
    end_date: Union[datetime.datetime, datetime.date, None] = None,
    average: bool = False,
    remove_zero: bool = False,
    return_days: bool = False,
):
    """Get rest breaths per minute.

    Parameters
    ----------
        loader: :class:`pywearable.loader.base.BaseLoader`
            Instance of `LabfrontLoader`.
        user_id: :class:`str` or :class:`list`, optional
            ID of the user for which breaths per minute must be computed, by default "all".
        start_date: :class:`datetime.datetime`, optional
            Start date from which breaths per minute must be computed, by default None.
        end_date: :class:`datetime.datetime`, optional
            End date to which breaths per minute must be computed, by default to None.
        average: :class:`bool`, optional
            Whether to average the breaths per minute over the time-range, by default false.
            If set to `True`, then the breaths per minute are averaged across the time-range,
            thus returning a dictionary with the average breaths per minute and the valid days
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
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        average=average,
        remove_zero=remove_zero,
        return_days=return_days,
    )


def get_waking_breaths_per_minute(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, None] = None,
    end_date: Union[datetime.datetime, datetime.date, None] = None,
    average: bool = False,
    remove_zero: bool = False,
    return_days: bool = False,
):
    """Get average waking breaths per minute across time-range.

    Parameters
    ----------
        loader: :class:`pylabfront.loader.Loader`
            Instance of `LabfrontLoader`.
        user_id :class:`str` or :class:`list`, optional
            ID of the user for which breaths per minute must be computed, by default "all".
        start_date: :class:`datetime.datetime`, optional
            Start date from which breaths per minute must be computed, by default None.
        end_date :class:`datetime.datetime`, optional
            End date to which breaths per minute must be computed, by default None.
        average: :class:`bool`, optional
            Whether to average the breaths per minute over the time-range, by default false.
            If set to `True`, then the breaths per minute are averaged across the time-range,
            thus returning a dictionary with the average breaths per minute and the valid days
            over which the average was computed. If set to `False`, the dictionary contains
            the breaths per minute value for each day.
        remove_zero: :class:`bool`, optional
            Whether to remove data with breathsPerMinute equal to 0 from the data, by default False.
        return_days: :class:`bool`, optional
            Whether to return the days over which the average value was computed, by default False.

    Returns:
        :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys, and average breaths per minute as value.
    """
    return get_breaths_per_minute(
        loader,
        day_or_night=_RESPIRATION_DAY,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        average=average,
        remove_zero=remove_zero,
        return_days=return_days,
    )


def get_rest_spO2(
    loader : BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    """Get spO2 during sleep.

    This function returns the mean rest spO2 computed for every day.

    Parameters
    ----------
    loader: :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id: :class:`str` or :class:`list`, optional
        The id(s) for which TIB must be retrieved, by default "all"
    start_date: :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date: :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind: :class:`str` or None, optional
        Whether to transform sp02 over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`
    ### TODO DECIDE HERE HOW TO DO IT
    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys, and rest spO2 as value.
    """

    user_id = utils.get_user_ids(loader, user_id)

    data_dict = {}
    if average:
        average_dict = {}

    for user in user_id:
        try:
            spo2_data = loader.load_garmin_connect_pulse_ox(
                user, start_date=start_date, end_date=end_date
            )
            spo2_data = spo2_data[spo2_data.sleep == 1]
            if len(spo2_data) > 0:
                data_dict[user] = (
                    spo2_data.groupby(spo2_data[loader.date_column].dt.date)[
                        constants._SPO2_COLUMN
                    ]
                    .mean()
                    .to_dict()
                )
                if average:
                    spo2_data_df = pd.DataFrame.from_dict(
                        data_dict[user], orient="index"
                    )
                    average_dict[user] = {}
                    average_dict[user]["values"] = np.nanmean(
                        np.array(list(data_dict[user].values()))
                    )
                    average_dict[user]["days"] = [
                        datetime.datetime.strftime(x, "%Y-%m-%d")
                        for x in spo2_data_df.index
                    ]
        except:
            data_dict[user] = None
    if average:
        return average_dict
    return data_dict