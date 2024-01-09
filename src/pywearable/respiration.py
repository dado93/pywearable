"""
This module contains all the functions related to analysis
of Labfront respiration data.
"""
import datetime
from typing import Union

import numpy as np
import pandas as pd

from . import constants, loader, utils

_RESPIRATION_DAY = "DAY"
_RESPIRATION_NIGHT = "NIGHT"

_RESPIRATION_METRIC_MEAN_PULSE_OX = "meanPulseOx"
_RESPIRATION_METRIC_P10_PULSE_OX = "p10PulseOx"
_RESPIRATION_METRIC_P20_PULSE_OX = "p20PulseOx"
_RESPIRATION_METRIC_P30_PULSE_OX = "p30PulseOx"
_RESPIRATION_METRIC_WAKING_BREATHS_PER_MINUTE = "meanWakingBreathsPerMinute"
_RESPIRATION_METRIC_REST_BREATHS_PER_MINUTE = "meanRestBreathsPerMinute"


def get_mean_rest_pulse_ox(
    loader: loader.BaseLoader,
    user_id: Union[str, list, None] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    args=(),
):
    """Get mean pulse ox value at rest.

    This function computes the mean pulse ox value during
    resting periods (i.e., sleep) for the given ``user_id``
    and for the required time interval from ``start_date`` to
    ``end_date``. It is possible to perform a
    transformation of the retrieved mean pulse ox values
    by setting the ``kind`` parameters. For example, it is
    possible to obtain the mean of the mean values by
    setting the ``kind`` parameter to ``"mean``. If this
    following transformation requires additional
    arguments, then it is possible to set them in the
    ``args`` argument.

    Parameters
    ----------
    loader : :class:`loader.BaseLoader`
        An initialized data loader.
    user_id : Union[str, list, None], optional
        _description_, by default "all"
    start_date : Union[datetime.datetime, datetime.date, str, None], optional
        _description_, by default None
    end_date : Union[datetime.datetime, datetime.date, str, None], optional
        _description_, by default None
    kind : Union[str, None], optional
        _description_, by default None
    args : tuple, optional
        _description_, by default ()

    Returns
    -------
    _type_
        _description_
    """
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_MEAN_PULSE_OX,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        aggregate="mean",
        kind=kind,
        kind_args=args,
    )


def get_p10_rest_pulse_ox(
    loader: loader.BaseLoader,
    user_id: Union[str, list, None] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    args=(),
):
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_P10_PULSE_OX,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        aggregate=np.percentile,
        aggregate_args=(10),
        kind=kind,
        kind_args=args,
    )


def get_p20_rest_pulse_ox(
    loader: loader.BaseLoader,
    user_id: Union[str, list, None] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    args=(),
):
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_P20_PULSE_OX,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        aggregate=np.percentile,
        aggregate_args=(20),
        kind=kind,
        kind_args=args,
    )


def get_p30_rest_pulse_ox(
    loader: loader.BaseLoader,
    user_id: Union[str, list, None] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    args=(),
):
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_P30_PULSE_OX,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        aggregate=np.percentile,
        aggregate_args=(30),
        kind=kind,
        kind_args=args,
    )


def get_rest_pulse_ox_statistic(
    loader: loader.BaseLoader,
    metric: str,
    user_id: Union[str, list, None] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    aggregate: str = "mean",
    aggregate_args: Union[tuple, list] = (),
    kind: Union[str, None] = None,
    kind_args: Union[tuple, list] = (),
):
    """Get pulse ox during sleep.

    This function returns a rest pulse ox statistic for each day. Depending on the value
    of the ``kind`` parameter, the function returns a statistic for rest pulse ox data.
    The value of the ``kind`` parameter can be any value that is accepted by
    a transform operation by pandas. By default, the function returns the ``mean``
    pulse ox at rest.

    Parameters
    ----------
    loader: :class:`pywearable.loader.BaseLoader`
        Instance of a data loader.
    user_id: :class:`str`, optional
        Unique identifier of the user for which pulse ox must be computed, by default ``"all"``.
        If the parameter is set to ``all``, then the function is applied to all the
        users for which the ``loader`` has data.
    start_date: :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date from which rest pulse ox must be computed, by default None.
        If set to ``None``, then the function relies on the implementation of the ``loader``
        to appropriately handle it.
    end_date: :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date to which rest rest pulse ox must be computed, by default None.
        If set to ``None``, then the function relies on the implementation of the ``loader``
        to appropriately handle it.
    kind: function or :class:'str', optional
        The transform operation to compute on the rest pulse ox data, by default ``mean``.

    Returns
    -------
    :class:`dict`
        The ouput dictionary is a nested dictionary that always contains
        the ``user_id`` values as primary keys.
        For each ``user_id``, the nested dictionary contains
        ``metric`` and ``"days"``as secondary keys. The value of the ``metric`` is the
        result of the transformation applied to rest pulse ox,
        while the value of the ``"days"`` key contains the list of
        days over which this transformation was computed.
    """
    # Get user id from the loader
    user_id = utils.get_user_ids(loader, user_id)
    # Convert to datetime
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)
    # Extend range to account for sleep start in prev day and ending next day
    if not (start_date is None):
        ext_start_date = start_date - datetime.timedelta(days=1)
    else:
        ext_start_date = None
    if not (end_date is None):
        ext_end_date = end_date + datetime.timedelta(days=1)
    else:
        ext_end_date = None
    data_dict = {}

    for user in user_id:
        data_dict[user] = {}
        pulse_ox_data = loader.load_pulse_ox(
            user_id=user, start_date=ext_start_date, end_date=ext_end_date
        )
        if len(pulse_ox_data) > 0:
            # Get the data only when sleeping and reset index
            pulse_ox_data = pulse_ox_data[
                pulse_ox_data[constants._IS_SLEEPING_COL] == True
            ].reset_index(drop=True)
            # Get only data with calendar day between start and end date and reset index
            if not (start_date is None):
                pulse_ox_data = pulse_ox_data[
                    pulse_ox_data[constants._CALENDAR_DATE_COL] >= start_date.date()
                ].reset_index(drop=True)
            if not (end_date is None):
                pulse_ox_data = pulse_ox_data[
                    pulse_ox_data[constants._CALENDAR_DATE_COL] <= end_date.date()
                ].reset_index(drop=True)
            if not (kind is None):
                # Apply double transformation
                transformed_series = pulse_ox_data.groupby(
                    pulse_ox_data[constants._CALENDAR_DATE_COL]
                )[constants._SPO2_SPO2_COL].aggregate(aggregate, aggregate_args)
                data_dict[user][metric] = transformed_series.apply(kind, kind_args)
                data_dict[user]["days"] = transformed_series.index.values.tolist()
            else:
                data_dict[user] = (
                    pulse_ox_data.groupby(pulse_ox_data[constants._CALENDAR_DATE_COL])[
                        constants._SPO2_SPO2_COL
                    ]
                    .aggregate(aggregate, aggregate_args)
                    .to_dict()
                )

    return data_dict


def get_breaths_per_minute(
    loader: loader.BaseLoader,
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
    loader: loader.BaseLoader,
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
    loader: loader.BaseLoader,
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


def get_respiration_statistic():
    pass


def get_respiration_statistics():
    pass
