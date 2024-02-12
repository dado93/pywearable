"""
This module contains all the functions related to the analysis 
of cardiac data, mostly for heart rate (HR) and heart rate
variability (HRV).
"""

import datetime
from typing import Union

import numpy as np
import pandas as pd
from scipy import interpolate, signal

from . import constants, sleep, utils
from .loader.base import BaseLoader

_CARDIAC_METRIC_RESTING_HEART_RATE = "restHR"
_CARDIAC_METRIC_MAXIMUM_HEART_RATE = "maxHR"
_CARDIAC_METRIC_MINIMUM_HEART_RATE = "minHR"
_CARDIAC_METRIC_AVERAGE_HEART_RATE = "avgHR"
_CARDIAC_METRIC_ROOT_MEAN_SQUARED_SUCCESSIVE_DIFFERENCES = "RMSSD"
_CARDIAC_METRIC_STANDARD_DEVIATION_NORMAL_TO_NORMAL = "SDNN"
_CARDIAC_METRIC_LOW_FREQUENCY = "LF"
_CARDIAC_METRIC_HIGH_FREQUENCY = "HF"
_CARDIAC_METRIC_LOW_HIGH_FREQUENCY_RATIO = "LFHF"

_CARDIAC_HR_STATISTICS = [
    _CARDIAC_METRIC_RESTING_HEART_RATE,
    _CARDIAC_METRIC_MAXIMUM_HEART_RATE,
    _CARDIAC_METRIC_MINIMUM_HEART_RATE,
    _CARDIAC_METRIC_AVERAGE_HEART_RATE,
]

_CARDIAC_HRV_TIME_DOMAIN_STATISTICS = [
    _CARDIAC_METRIC_ROOT_MEAN_SQUARED_SUCCESSIVE_DIFFERENCES,
    _CARDIAC_METRIC_STANDARD_DEVIATION_NORMAL_TO_NORMAL,
]

_CARDIAC_HRV_FREQUENCY_DOMAIN_STATISTICS = [
    _CARDIAC_METRIC_LOW_FREQUENCY,
    _CARDIAC_METRIC_HIGH_FREQUENCY,
    _CARDIAC_METRIC_LOW_HIGH_FREQUENCY_RATIO,
]

_CARDIAC_HRV_STATISTICS = (
    _CARDIAC_HRV_TIME_DOMAIN_STATISTICS + _CARDIAC_HRV_FREQUENCY_DOMAIN_STATISTICS
)


def get_rest_heart_rate(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    kind_args=(),
    kind_kwargs={},
    loader_kwargs={},
    return_df: bool = True,
    return_multi_index: bool = True,
) -> Union[dict, pd.DataFrame]:
    """Get resting heart rate (RHR) cardiac metric.

    This function computes the resting heart rate metric.
    Depending on the value of the ``kind`` parameter, this function
    returns RHR for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which RHR must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform RHR over days, or to return the value for each day, by default None.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and RHR as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `RHR`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_heart_rate_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_RESTING_HEART_RATE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_max_heart_rate(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args=(),
    kind_kwargs={},
    loader_kwargs={},
    return_df: bool = True,
    return_multi_index: bool = True,
) -> Union[dict, pd.DataFrame]:
    """Get maximum heart rate (MHR) cardiac metric.

    This function computes the maximum heart rate metric.
    Depending on the value of the ``kind`` parameter, this function
    returns MHR for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which MHR must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform MHR over days, or to return the value for each day, by default None.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and MHR as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `MHR`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_cardiac_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_MAXIMUM_HEART_RATE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_min_heart_rate(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args=(),
    kind_kwargs={},
    loader_kwargs={},
    return_df: bool = True,
    return_multi_index: bool = True,
) -> dict:
    """Get minimum heart rate (minHR) cardiac metric.

    This function computes the minimum heart rate metric.
    Depending on the value of the ``kind`` parameter, this function
    returns minHR for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which minHR must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform minHR over days, or to return the value for each day, by default None.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and minHR as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `minHR`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_heart_rate_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_MINIMUM_HEART_RATE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_avg_heart_rate(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args=(),
    kind_kwargs={},
    loader_kwargs={},
    return_df: bool = True,
    return_multi_index: bool = True,
) -> dict:
    """Get average heart rate (avgHR) cardiac metric.

    This function computes the average heart rate metric.
    Depending on the value of the ``kind`` parameter, this function
    returns avgHR for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which avgHR must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform avgHR over days, or to return the value for each day, by default None.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and avgHR as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `avgHR`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_heart_rate_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_AVERAGE_HEART_RATE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def _compute_resting_heart_rate(daily_summary: pd.DataFrame, **kwargs) -> dict:
    """Compute RHR from daily summaries.

    Parameters
    ----------
    daily_summary : :class:`pd.DataFrame`
        Daily summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_daily_summary`.

    Returns
    -------
    :class:`dict`
        A dictionary with daily RHR as values, and calendar dates as keys.
    """
    return _compute_hr_statistic(
        daily_summary=daily_summary, metric=_CARDIAC_METRIC_RESTING_HEART_RATE
    )


def _compute_maximum_heart_rate(daily_summary: pd.DataFrame, **kwargs) -> dict:
    """Compute MHR from daily summaries.

    Parameters
    ----------
    daily_summary : :class:`pd.DataFrame`
        Daily summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_daily_summary`.

    Returns
    -------
    :class:`dict`
        A dictionary with daily MHR as values, and calendar dates as keys.
    """
    return _compute_hr_statistic(
        daily_summary=daily_summary, metric=_CARDIAC_METRIC_MAXIMUM_HEART_RATE
    )


def _compute_minimum_heart_rate(daily_summary: pd.DataFrame, **kwargs) -> dict:
    """Compute minHR from daily summaries.

    Parameters
    ----------
    daily_summary : :class:`pd.DataFrame`
        Daily summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_daily_summary`.

    Returns
    -------
    :class:`dict`
        A dictionary with daily minHR as values, and calendar dates as keys.
    """
    return _compute_hr_statistic(
        daily_summary=daily_summary, metric=_CARDIAC_METRIC_MINIMUM_HEART_RATE
    )


def _compute_average_heart_rate(daily_summary: pd.DataFrame, **kwargs) -> dict:
    """Compute avgHR from daily summaries.

    Parameters
    ----------
    daily_summary : :class:`pd.DataFrame`
        Daily summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_daily_summary`.

    Returns
    -------
    :class:`dict`
        A dictionary with daily avgHR as values, and calendar dates as keys.
    """
    return _compute_hr_statistic(
        daily_summary=daily_summary, metric=_CARDIAC_METRIC_AVERAGE_HEART_RATE
    )


_HEART_RATE_STATISTICS_DICT = {
    _CARDIAC_METRIC_RESTING_HEART_RATE: _compute_resting_heart_rate,
    _CARDIAC_METRIC_MAXIMUM_HEART_RATE: _compute_maximum_heart_rate,
    _CARDIAC_METRIC_MINIMUM_HEART_RATE: _compute_minimum_heart_rate,
    _CARDIAC_METRIC_AVERAGE_HEART_RATE: _compute_average_heart_rate,
}


def get_heart_rate_statistic(
    loader: BaseLoader,
    statistic: str,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
    return get_heart_rate_statistics(
        loader=loader,
        statistic=statistic,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_heart_rate_statistics(
    loader: BaseLoader,
    statistic: Union[str, list, tuple, None] = None,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
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
    # Check metrics
    if statistic is None:
        # Consider all metrics
        statistics = list(_HEART_RATE_STATISTICS_DICT.keys())
    elif type(statistic) == str:
        statistics = [statistic]

    # Check args and kwargs
    if type(kind_args) != list:
        raise ValueError(f"kind_args must be an iterable, not {type(kind_args)}")
    if type(kind_kwargs) != dict:
        raise ValueError(f"kind_kwargs must be of type dict, not {type(kind_kwargs)}")
    if type(loader_kwargs) != dict:
        raise ValueError(
            f"loader_kwargs must be of type dict, not {type(loader_kwargs)}"
        )
    both_dates_valid = False
    if (not (start_date is None)) and (not (end_date is None)):
        # Let's set up a dataframe in which we will store all the data
        date_periods = pd.date_range(start_date, end_date, freq="D")
        multi_index = pd.MultiIndex.from_product(
            [user_id, date_periods],
            names=[constants._USER_COL, constants._CALENDAR_DATE_COL],
        )
        heart_rate_stats_df = pd.DataFrame(index=multi_index, columns=metrics)
        both_dates_valid = True
    else:
        # Set up a standard df and we will populate it later with indexes
        heart_rate_stats_df = pd.DataFrame()
    for user in user_id:
        if not (both_dates_valid):
            user_heart_rate_stats_df = pd.DataFrame()
        daily_summary = loader.load_daily_summary(
            user_id=user,
            start_date=ext_start_date,
            end_date=ext_end_date,
            **loader_kwargs,
        )
        if len(daily_summary) > 0:
            # Get only data with calendar date between start and end date and reset index
            if not (start_date is None):
                daily_summary = daily_summary[
                    daily_summary[constants._CALENDAR_DATE_COL] >= start_date
                ].reset_index(drop=True)
            if not (end_date is None):
                daily_summary = daily_summary[
                    daily_summary[constants._CALENDAR_DATE_COL] <= end_date
                ].reset_index(drop=True)
            for statistic in statistics:
                # Get series with metrics by calendarDate
                ser = _HEART_RATE_STATISTICS_DICT[statistic](
                    daily_summary=daily_summary
                )
                if both_dates_valid:
                    heart_rate_stats_df.loc[(user, ser.index), statistic] = ser.values
                else:
                    if len(ser) > 0:
                        min_date = ser.index.min() if start_date is None else start_date
                        max_date = ser.index.max() if end_date is None else end_date
                        user_date_range = pd.date_range(min_date, max_date, freq="D")
                        ser = ser.reindex(user_date_range)
                        # We have different dates based on user
                        ser = ser.set_axis(
                            pd.MultiIndex.from_product(
                                [[user], user_date_range],
                                names=[
                                    constants._USER_COL,
                                    constants._CALENDAR_DATE_COL,
                                ],
                            )
                        ).rename(statistic)
                        if len(user_heart_rate_stats_df) == 0:
                            # Empty df, first metric
                            user_heart_rate_stats_df = ser.to_frame()
                        else:
                            user_heart_rate_stats_df = pd.merge(
                                user_heart_rate_stats_df,
                                ser,
                                left_index=True,
                                right_index=True,
                                how="outer",
                            )
            if not both_dates_valid:
                heart_rate_stats_df = pd.concat(
                    (heart_rate_stats_df, user_heart_rate_stats_df)
                )
    # Perform kind operation by user
    if not (kind is None):
        heart_rate_stats_df = heart_rate_stats_df.groupby(
            level=constants._USER_COL
        ).agg(kind, *kind_args, **kind_kwargs)
        if return_df:
            return heart_rate_stats_df
        else:
            return heart_rate_stats_df.to_dict(orient="index")
    # Return based on settings
    return utils.return_multiindex_df(
        heart_rate_stats_df, return_df, return_multi_index
    )


def get_night_rmssd(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    coverage: float = 0.7,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
) -> dict:
    """Computes RMSSD metric considering night data.

    This function computes the root mean squared successive difference (RMSSD),
    taking in consideration only periods where the user was asleep.
    Depending on the value of the ``kind`` parameter, this function
    returns the mean of RMSSD short-term (5 mins) computations overnight
    for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which RMSSD must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.
    kind : :class:`str` or None, optional
        Whether to transform RMSSD over days, or to return the value for each day, by default None.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and RMSSD as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `RMSSD`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_hrv_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_ROOT_MEAN_SQUARED_SUCCESSIVE_DIFFERENCES,
        start_date=start_date,
        end_date=end_date,
        coverage=coverage,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_night_sdnn(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    coverage: float = 0.7,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
) -> dict:
    """Computes SDNN metric considering night data.

    This function computes the standard deviation of normal to normal (SDNN) intervals,
    taking in consideration only periods where the user was asleep.
    Depending on the value of the ``kind`` parameter, this function
    returns the mean of SDNN short term computations (5 mins) overnight
    for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which SDNN must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.
    kind : :class:`str` or None, optional
        Whether to transform SDNN over days, or to return the value for each day, by default None.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and SDNN as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `SDNN`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_hrv_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_STANDARD_DEVIATION_NORMAL_TO_NORMAL,
        start_date=start_date,
        end_date=end_date,
        coverage=coverage,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_night_lf(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    coverage: float = 0.7,
) -> dict:
    """Compute LF power metrics considering night data.

    This function computes the low frequency (LF, 0.04Hz - 0.15Hz) power,
    taking in consideration only periods where the user was asleep.
    Depending on the value of the ``kind`` parameter, this function
    returns the mean of LF short-term (5 mins) computations overnight
    for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which LF must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.
    kind : :class:`str` or None, optional
        Whether to transform LF over days, or to return the value for each day, by default None.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and LF as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `LF`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_hrv_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_LOW_FREQUENCY,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        coverage=coverage,
    )


def get_night_hf(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    coverage: float = 0.7,
) -> dict:
    """Compute HF power metrics considering night data.

    This function computes the low frequency (HF, 0.15Hz - 0.4Hz) power,
    taking in consideration only periods where the user was asleep.
    Depending on the value of the ``kind`` parameter, this function
    returns the mean of HF short-term (5 mins) computations overnight
    for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which HF must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.
    kind : :class:`str` or None, optional
        Whether to transform HF over days, or to return the value for each day, by default None.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and HF as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `HF`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_hrv_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_HIGH_FREQUENCY,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        coverage=coverage,
    )


def get_night_lfhf(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    coverage: float = 0.7,
) -> dict:
    """Compute LF/HF power ratio metrics considering night data.

    This function computes the ratio between low frequency (LF) and high frequency (HF) power,
    taking in consideration only periods where the user was asleep.
    Depending on the value of the ``kind`` parameter, this function
    returns the mean of LFHF short-term (5 mins) computations overnight
    for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which LFHF must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.
    kind : :class:`str` or None, optional
        Whether to transform LFHF over days, or to return the value for each day, by default None.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and LFHF as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `LFHF`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_hrv_statistic(
        loader=loader,
        user_id=user_id,
        metric=_CARDIAC_METRIC_LOW_HIGH_FREQUENCY_RATIO,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        coverage=coverage,
    )


def _compute_hr_statistic(daily_summary: pd.DataFrame, metric: str, **kwargs) -> dict:
    """Computes a HR statistic at a daily level

    This function computes a specific statistic for
    the heart rate data available at daily level.

    Parameters
    ----------
    daily_summary : :class:`pd.DataFrame`
        Daily summary data.
    metric : :class:`str`
        Name of the statistic to be computed

    Returns
    -------
    :class:`dict`
        dictionary with ``user_id`` as primary key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and the cardiac metric as values.

     Raises
    ------
    ValueError
        If `daily_summary` is not a :class:`pd.DataFrame`.
    ValueError
        if `metric` isn't one of "RHR","MHR", "minHR","avgHR".
    """

    if not isinstance(daily_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(daily_summary)} is not a valid type."
        )

    if len(daily_summary) == 0:
        return {}

    if metric == _CARDIAC_METRIC_RESTING_HEART_RATE:
        col = constants._RESTING_HR_COLUMN
    elif metric == _CARDIAC_METRIC_MAXIMUM_HEART_RATE:
        col = constants._MAX_HR_COLUMN
    elif metric == _CARDIAC_METRIC_MINIMUM_HEART_RATE:
        col = constants._MIN_HR_COLUMN
    elif metric == _CARDIAC_METRIC_AVERAGE_HEART_RATE:
        col = constants._AVG_HR_COLUMN
    else:
        raise ValueError(
            f"{metric} is not a valid value. Select among {_CARDIAC_HR_STATISTICS}"
        )
    statistic_dict = pd.Series(
        daily_summary[col].values,
        index=daily_summary[constants._CALENDAR_DATE_COL],
    )

    return statistic_dict


def _compute_hrv_statistic(
    bbi_dict: dict, metric: str, coverage: float = 0.7, **kwargs
) -> dict:
    """Computes a HRV statistic at a per night level

    This function computes a specific statistic for
    the BBI data available for each night.

    Parameters
    ----------
    bbi_dict: :class:`dict`
        Dictionary of BBI night data, already filtered to include only sleep periods.
    metric : :class:`str`
        Name of the statistic to be computed
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        dictionary with ``user_id`` as primary key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and the cardiac metric as values.

     Raises
    ------
    ValueError
        if `metric` isn't one of "RMSSD", "SDNN", "LF", "HF", "LFHF"
    """

    daily_means = {}

    for date, bbi_df in bbi_dict.items():
        bbi_df = bbi_df.set_index(constants._ISODATE_COL)
        # we consider the coverage against the mean bbi in that window
        counts = bbi_df.resample("5min").bbi.count()
        means = bbi_df.resample("5min").bbi.mean()
        coverage_filter = (counts > ((300 / (means / 1000)) * coverage)).values

        # time-domain
        if metric == _CARDIAC_METRIC_ROOT_MEAN_SQUARED_SUCCESSIVE_DIFFERENCES:
            ST_analysis = bbi_df.resample("5min").bbi.apply(
                lambda x: np.sqrt(np.mean(np.diff(x) ** 2)) if x.count() > 5 else 0
            )
        elif metric == _CARDIAC_METRIC_STANDARD_DEVIATION_NORMAL_TO_NORMAL:
            ST_analysis = bbi_df.resample("5min").bbi.apply(
                lambda x: np.std(x, ddof=1) if x.count() > 5 else 0
            )
        # frequency domain
        elif metric in _CARDIAC_HRV_FREQUENCY_DOMAIN_STATISTICS:
            LF_range = (0.04, 0.15)
            HF_range = (0.15, 0.40)

            def calculate_power(bbi, freq_range):
                """Calculates power in freq band between `f1` and `f2` given an array of beat-to-beat intervals"""

                # Resampling (with 4Hz) and interpolate
                # Because RRi are unevenly spaced we must interpolate it for accurate PSD estimation.

                fs = 4
                t = np.cumsum(bbi)
                t -= t.iloc[0]
                f_interpol = interpolate.interp1d(
                    t, bbi, kind="cubic", fill_value="extrapolate"
                )
                t_interpol = np.arange(t.iloc[0], t.iloc[-1], 1000.0 / fs)
                nn_interpol = f_interpol(t_interpol)

                # Subtract mean value from each sample for suppression of DC-offsets
                nn_interpol = nn_interpol - np.mean(nn_interpol)
                # Calculate power spectral density using Welch method
                nfft = 2**12
                if t.max() < 300000:
                    nperseg = min(nfft, len(nn_interpol))
                else:
                    nperseg = 300
                freq, psd = signal.welch(
                    x=nn_interpol,
                    fs=fs,
                    window="hamming",
                    nfft=nfft,
                    nperseg=nperseg,
                    scaling="density",
                )

                f1, f2 = freq_range
                pow = np.trapz(
                    psd[np.logical_and(freq >= f1, freq < f2)],
                    freq[np.logical_and(freq >= f1, freq < f2)],
                )

                return pow

            if metric == _CARDIAC_METRIC_HIGH_FREQUENCY:
                ST_analysis = bbi_df.resample("5min").bbi.apply(
                    lambda x: calculate_power(x, HF_range) if x.count() > 5 else 0
                )
            elif metric == _CARDIAC_METRIC_LOW_FREQUENCY:
                ST_analysis = bbi_df.resample("5min").bbi.apply(
                    lambda x: calculate_power(x, LF_range) if x.count() > 5 else 0
                )
            else:
                # note that here we're computing LFHF ratios over 5 minutes and then getting the average
                # it's not the same as computing the ratio of the mean LF and mean HF over a night
                # if one wants the latter, it should be done as post processing by getting LF and HF overnight metrics
                ST_analysis = bbi_df.resample("5min").bbi.apply(
                    lambda x: (
                        calculate_power(x, LF_range) / calculate_power(x, HF_range)
                        if x.count() > 5
                        else 0
                    )
                )
        else:
            raise ValueError(
                f"{metric} is not a valid value. Select among {_CARDIAC_HRV_STATISTICS}"
            )
        # check coverage
        ST_analysis = ST_analysis.iloc[coverage_filter & (ST_analysis != 0).values]
        # compute the mean overnight
        if len(ST_analysis) > 0:
            daily_mean = ST_analysis.values.mean()
            if daily_mean is not None:
                daily_means[date] = round(daily_mean, 2)

    return daily_means


def _compute_rmssd(bbi_dict: dict, coverage: float = 0.7, **kwargs) -> dict:
    """Compute night RMSSD from BBI data.

    Parameters
    ----------
    bbi_dict: :class:`dict`
        Dictionary of BBI night data, already filtered to include only sleep periods.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        A dictionary with night RMSSD as values, and calendar dates as keys.
    """
    return _compute_hrv_statistic(
        bbi_dict=bbi_dict,
        metric=_CARDIAC_METRIC_ROOT_MEAN_SQUARED_SUCCESSIVE_DIFFERENCES,
        coverage=coverage,
    )


def _compute_sdnn(bbi_dict: dict, coverage: float = 0.7, **kwargs) -> dict:
    """Compute night SDNN from BBI data.

    Parameters
    ----------
    bbi_dict: :class:`dict`
        Dictionary of BBI night data, already filtered to include only sleep periods.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        A dictionary with night SDNN as values, and calendar dates as keys.
    """
    return _compute_hrv_statistic(
        bbi_dict=bbi_dict,
        metric=_CARDIAC_METRIC_STANDARD_DEVIATION_NORMAL_TO_NORMAL,
        coverage=coverage,
    )


def _compute_lf(bbi_dict: dict, coverage: float = 0.7, **kwargs) -> dict:
    """Compute night LF power from BBI data.

    Parameters
    ----------
    bbi_dict: :class:`dict`
        Dictionary of BBI night data, already filtered to include only sleep periods.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        A dictionary with night LF power as values, and calendar dates as keys.
    """
    return _compute_hrv_statistic(
        bbi_dict=bbi_dict, metric=_CARDIAC_METRIC_LOW_FREQUENCY, coverage=coverage
    )


def _compute_hf(bbi_dict: dict, coverage: float = 0.7, **kwargs) -> dict:
    """Compute night HF power from BBI data.

    Parameters
    ----------
    bbi_dict: :class:`dict`
        Dictionary of BBI night data, already filtered to include only sleep periods.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        A dictionary with night HF power as values, and calendar dates as keys.
    """
    return _compute_hrv_statistic(
        bbi_dict=bbi_dict, metric=_CARDIAC_METRIC_HIGH_FREQUENCY, coverage=coverage
    )


def _compute_lfhf(bbi_dict: dict, coverage: float = 0.7, **kwargs) -> dict:
    """Compute night LFHF ratios from BBI data.

    Parameters
    ----------
    bbi_dict: :class:`dict`
        Dictionary of BBI night data, already filtered to include only sleep periods.
    coverage : :class:`float`, optional
        The percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7.

    Returns
    -------
    :class:`dict`
        A dictionary with night LFHF ratios as values, and calendar dates as keys.
    """
    return _compute_hrv_statistic(
        bbi_dict=bbi_dict,
        metric=_CARDIAC_METRIC_LOW_HIGH_FREQUENCY_RATIO,
        coverage=coverage,
    )


def get_hrv_statistic(
    loader: BaseLoader,
    statistic: str,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    coverage: float = 0.7,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
    pass


def get_hrv_statistics(
    loader: BaseLoader,
    statistic: str,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
    pass


_CARDIAC_STATISTIC_DICT = {
    _CARDIAC_METRIC_RESTING_HEART_RATE: _compute_resting_heart_rate,
    _CARDIAC_METRIC_MAXIMUM_HEART_RATE: _compute_maximum_heart_rate,
    _CARDIAC_METRIC_MINIMUM_HEART_RATE: _compute_minimum_heart_rate,
    _CARDIAC_METRIC_AVERAGE_HEART_RATE: _compute_average_heart_rate,
    _CARDIAC_METRIC_ROOT_MEAN_SQUARED_SUCCESSIVE_DIFFERENCES: _compute_rmssd,
    _CARDIAC_METRIC_STANDARD_DEVIATION_NORMAL_TO_NORMAL: _compute_sdnn,
    _CARDIAC_METRIC_LOW_FREQUENCY: _compute_lf,
    _CARDIAC_METRIC_HIGH_FREQUENCY: _compute_hf,
    _CARDIAC_METRIC_LOW_HIGH_FREQUENCY_RATIO: _compute_lfhf,
}


def get_cardiac_statistic(
    loader: BaseLoader,
    user_id: Union[str, list],
    metric: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    **kwargs,
) -> dict:
    """Get a single cardiac summary statistic.

    This function is used by several functions of the module to get a single
    cardiac statistic starting from heart rate data or bbi data.
    If multiple statistics are required, then it is more efficient to
    use the :func:`get_cardiac_statistics` function that computes all the
    statistics by loading only once daily summaries and bbi data.
    The following statistics can be computed:
        - Resting Heart Rate (``metric``="RHR")
        - Maximum Heart Rate (``metric``="MHR")
        - Average Heart Rate (``metric``="avgHR")
        - Minimum Heart Rate (``metric``="minHR")
        - Root Mean Squared Successive Differences (``metric``="RMSSD")
        - Standard Deviation Normal to Normal (``metric``="SDNN")
        - Low Frequency power (``metric``="LF")
        - High Frequency power (``metric``="HF")
        - Low to High Frequency ratio (``metric``="LFHF")

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`
        The id(s) for which the cardiac statistic must be computed.
    metric : :class:`str`
        The name of the cardiac statistic which must be computed.
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to perform a transform of the cardiac statistic over days, by default None.
        If `None`, then the sleep statistic is returned with a value for each day, otherwise
        a transformation is applied. Valid options are:

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and the cardiac metric as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with the name of
        the cardiac metric as key and its transformed value,
        and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    user_id = utils.get_user_ids(loader, user_id)

    data_dict = {}
    if not (kind is None):
        transformed_dict = {}

    for user in user_id:
        if metric in _CARDIAC_HR_STATISTICS:
            daily_summary_data = loader.load_daily_summary(user, start_date, end_date)
            if len(daily_summary_data) > 0:
                daily_summary_data = daily_summary_data.groupby(
                    constants._CALENDAR_DATE_COL
                ).tail(1)
            compute_kwargs = {"daily_summary": daily_summary_data}
        elif metric in _CARDIAC_HRV_STATISTICS:
            sleep_timestamps = sleep.get_sleep_timestamps(
                loader, user, start_date, end_date
            )[user]
            # load the whole bbi history required, with some room (+- 12 hrs at start/end)
            bbi_dict = {}
            bbi_df = loader.load_bbi(
                user_id=user,
                start_date=utils.check_date(start_date) - datetime.timedelta(hours=12),
                end_date=utils.check_date(end_date) + datetime.timedelta(hours=12),
            )
            for date, (start_hour, end_hour) in sleep_timestamps.items():
                night_bbi = bbi_df.loc[
                    (bbi_df[constants._ISODATE_COL] > start_hour)
                    & (bbi_df[constants._ISODATE_COL] < end_hour)
                ]
                filtered_night_bbi = utils.filter_out_awake(
                    loader, user, night_bbi, date, resolution=1
                )
                bbi_dict[date] = filtered_night_bbi
            compute_kwargs = {"bbi_dict": bbi_dict}
        else:
            raise ValueError(
                f"Metric selected not valid. Choose a metric among {_CARDIAC_HR_STATISTICS} and {_CARDIAC_HRV_STATISTICS}"
            )

        data_dict[user] = _CARDIAC_STATISTIC_DICT[metric](**compute_kwargs, **kwargs)

        if not (kind is None):
            cardiac_data_df = pd.DataFrame.from_dict(data_dict[user], orient="index")
            transformed_dict[user] = {}
            if kind == "mean":
                transformed_dict[user][metric] = np.nanmean(
                    np.array(list(data_dict[user].values()))
                )
            elif kind == "std":
                transformed_dict[user][metric] = np.nanstd(
                    np.array(list(data_dict[user].values()))
                )
            elif kind == "min":
                transformed_dict[user][metric] = np.nanmin(
                    np.array(list(data_dict[user].values()))
                )
            elif kind == "max":
                transformed_dict[user][metric] = np.nanmax(
                    np.array(list(data_dict[user].values()))
                )

            transformed_dict[user]["days"] = [
                datetime.datetime.strftime(x, "%Y-%m-%d") for x in cardiac_data_df.index
            ]

    if not (kind is None):
        return transformed_dict
    else:
        return data_dict


def get_cardiac_statistics(
    loader: BaseLoader,
    user_id: Union[str, list],
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    **kwargs,
) -> dict:
    """Get cardiac statistics from daily summary data and beat-to-beat interval data.

    This function is used to get all the
    statistics from cardiac data. It is more efficient than
    :func:`get_cardiac_statistic` when multiple
    statistics are needed as it retrieves cardiac data
    only once to compute all the statistics.

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader()`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`
        The id(s) for which the cardiac statistics must be computed.
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to perform a transform of the cardiac statistics over days, by default None.
        If `None`, then the cardiac statistics are returned with a value for each day, otherwise
        a transformation is applied.

    Returns
    -------
    dict
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and cardiac statistic key:value pairs.
        If ``kind`` is not ``None``, dictionary with ``user_id`` as key, and a nested dictionary with
        ``values`` as key of another nested dictionary with key:value pairs for each cardiac statistic,
        and a ``days`` key that contains an array of all calendar days over which the transformation was computed.
    """

    data_dict = {}
    if not (kind is None):
        transformed_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        # Load daily summary data
        daily_summary_data = loader.load_daily_summary(user, start_date, end_date)
        if len(daily_summary_data) > 0:
            daily_summary_data = daily_summary_data.groupby(
                constants._CALENDAR_DATE_COL
            ).tail(1)
        sleep_timestamps = sleep.get_sleep_timestamps(
            loader, user, start_date, end_date
        )[user]
        # load the whole bbi history required, with some room (+- 12 hrs at start/end)
        bbi_dict = {}
        bbi_df = loader.load_bbi(
            user_id=user,
            start_date=utils.check_date(start_date) - datetime.timedelta(hours=12),
            end_date=utils.check_date(end_date) + datetime.timedelta(hours=12),
        )
        if sleep_timestamps:  # check that at least one night is present
            for date, (start_hour, end_hour) in sleep_timestamps.items():
                night_bbi = bbi_df.loc[
                    (bbi_df[constants._ISODATE_COL] > start_hour)
                    & (bbi_df[constants._ISODATE_COL] < end_hour)
                ]
                filtered_night_bbi = utils.filter_out_awake(
                    loader, user, night_bbi, date, resolution=1
                )
                bbi_dict[date] = filtered_night_bbi

        # get all cardiac metrics in a single DataFrame for the user
        user_cardiac_metrics_df = pd.DataFrame(
            index=pd.Index([], name=constants._CALENDAR_DATE_COL)
        )

        for cardiac_metric in _CARDIAC_STATISTIC_DICT.keys():
            metric_dict = _CARDIAC_STATISTIC_DICT[cardiac_metric](
                daily_summary=daily_summary_data, bbi_dict=bbi_dict, **kwargs
            )
            metric_df = pd.DataFrame(
                metric_dict.items(),
                columns=[constants._CALENDAR_DATE_COL, cardiac_metric],
            ).set_index(constants._CALENDAR_DATE_COL)
            user_cardiac_metrics_df = pd.merge(
                user_cardiac_metrics_df,
                metric_df,
                how="outer",
                on=constants._CALENDAR_DATE_COL,
            )

        data_dict[user] = user_cardiac_metrics_df.to_dict("index")

        if not (kind is None):
            transformed_dict[user] = {}
            transformed_dict[user]["values"] = user_cardiac_metrics_df.apply(
                kind
            ).to_dict()
            transformed_dict[user]["days"] = [
                date for date in user_cardiac_metrics_df.index
            ]

    if not (kind is None):
        return transformed_dict
    else:
        return data_dict
