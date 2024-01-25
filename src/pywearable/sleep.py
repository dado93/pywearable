"""
This module contains all the functions related to analysis
of sleep data.
"""

import datetime
from collections import OrderedDict
from typing import Union

import numpy as np
import pandas as pd
import warnings

from . import constants, utils
from .loader.base import BaseLoader

_SLEEP_METRIC_TIB = "TIB"
_SLEEP_METRIC_TST = "TST"
_SLEEP_METRIC_WASO = "WASO"
_SLEEP_METRIC_SPT = "SPT"
_SLEEP_METRIC_N1_DURATION = "N1"
_SLEEP_METRIC_N2_DURATION = "N2"
_SLEEP_METRIC_N3_DURATION = "N3"
_SLEEP_METRIC_NREM_DURATION = "NREM"
_SLEEP_METRIC_REM_DURATION = "REM"
_SLEEP_METRIC_AWAKE_DURATION = "AWAKE"
_SLEEP_METRIC_UNMEASURABLE_DURATION = "UNMEASURABLE"
_SLEEP_METRIC_SOL = "SOL"
_SLEEP_METRIC_N1_LATENCY = "Lat_N1"
_SLEEP_METRIC_N2_LATENCY = "Lat_N2"
_SLEEP_METRIC_N3_LATENCY = "Lat_N3"
_SLEEP_METRIC_REM_LATENCY = "Lat_REM"
_SLEEP_METRIC_N1_PERCENTAGE = "%N1"
_SLEEP_METRIC_N2_PERCENTAGE = "%N2"
_SLEEP_METRIC_N3_PERCENTAGE = "%N3"
_SLEEP_METRIC_NREM_PERCENTAGE = "%NREM"
_SLEEP_METRIC_REM_PERCENTAGE = "%REM"
_SLEEP_METRIC_SE = "SE"
_SLEEP_METRIC_SME = "SME"
_SLEEP_METRIC_SLEEP_SCORE = "SCORE"
_SLEEP_METRIC_AWAKE_COUNT = "countAwake"
_SLEEP_METRIC_N1_COUNT = "countN1"
_SLEEP_METRIC_N2_COUNT = "countN2"
_SLEEP_METRIC_N3_COUNT = "countN3"
_SLEEP_METRIC_REM_COUNT = "countREM"
_SLEEP_METRIC_BEDTIME = "bedTime"
_SLEEP_METRIC_WAKEUP_TIME = "wakeupTime"
_SLEEP_METRIC_MIDPOINT = "midpoint"
_SLEEP_METRIC_CPD_MIDPOINT = "CPD_midpoint"
_SLEEP_METRIC_CPD_DURATION = "CPD_duration"
_SLEEP_DATETIME_METRICS = [_SLEEP_METRIC_BEDTIME,
                          _SLEEP_METRIC_MIDPOINT,
                          _SLEEP_METRIC_WAKEUP_TIME]

_SLEEP_KIND_MAPPING = {
    "mean":{
        _SLEEP_METRIC_BEDTIME : utils.mean_time,
        _SLEEP_METRIC_WAKEUP_TIME : utils.mean_time,
        _SLEEP_METRIC_MIDPOINT : utils.mean_time,
        "default" : np.nanmean
    },
    "std":{
        _SLEEP_METRIC_BEDTIME : utils.std_time,
        _SLEEP_METRIC_WAKEUP_TIME : utils.std_time,
        _SLEEP_METRIC_MIDPOINT : utils.std_time,
        "default" : np.nanstd
    },
    "min":{
        _SLEEP_METRIC_BEDTIME : utils.get_earliest_bedtime,
        _SLEEP_METRIC_WAKEUP_TIME : utils.get_earliest_wakeup_time,
        _SLEEP_METRIC_MIDPOINT : utils.get_earliest_wakeup_time, # TODO probably to change
        "default" : np.nanmin
    },
    "max":{
        _SLEEP_METRIC_BEDTIME : utils.get_latest_bedtime,
        _SLEEP_METRIC_WAKEUP_TIME : utils.get_latest_wakeup_time,
        _SLEEP_METRIC_MIDPOINT : utils.get_latest_wakeup_time, # TODO probably to change
        "default" : np.nanmax
    }
}

def get_time_in_bed(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get time in bed (TIB) sleep metric.

    This function computes time in bed (TIB) metric as the total duration
    of the sleep, given by the sum of all sleep stages and unmeasurable sleep
    as well. The value is reported in minutes.

    Depending on the value of the ``kind`` parameter, this function
    returns TIB for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_time_in_bed(loader, user_id, start_date, end_date, kind=None)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 501.0,
            datetime.date(2023, 9, 10): 514.0,
            datetime.date(2023, 9, 11): 455.0,
            datetime.date(2023, 9, 12): 437.0,
            datetime.date(2023, 9, 13): 437.0,
            datetime.date(2023, 9, 14): 402.0,
            datetime.date(2023, 9, 15): 469.0}

        pywearable.sleep.get_time_in_bed(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'TIB': 463.14285714285717,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15']
                    }
            }


    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which TIB must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform TIB over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and TIB as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `TIB`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_TIB,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_sleep_period_time(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> pd.DataFrame:
    """Get sleep period time (SPT) sleep metric.

    This function computes sleep period time (SPT) metric as the duration from the first to
    the last period of sleep. Depending on the value of the ``kind`` parameter, this function
    returns SPT for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_sleep_period_time(loader, user_id, start_date, end_date, kind=None)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 501.0,
            datetime.date(2023, 9, 10): 514.0,
            datetime.date(2023, 9, 11): 455.0,
            datetime.date(2023, 9, 12): 437.0,
            datetime.date(2023, 9, 13): 437.0,
            datetime.date(2023, 9, 14): 402.0,
            datetime.date(2023, 9, 15): 496.0}

        pywearable.sleep.get_sleep_period_time(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'SPT': 463.14285714285717,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which SPT must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform SPT over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and SPT as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `SPT`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_SPT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_total_sleep_time(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> pd.DataFrame:
    """Get total sleep time (TST) sleep metric.

    This function computes total sleep time (TST) metric as the total duration of
    N1, N2, N3, and REM in SPT (see :func:`get_sleep_period_time`).
    Depending on the value of the ``kind`` parameter, this function
    returns TST for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_total_sleep_time(loader, user_id, start_date, end_date, kind=None)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 497.0,
            datetime.date(2023, 9, 10): 512.0,
            datetime.date(2023, 9, 11): 455.0,
            datetime.date(2023, 9, 12): 435.0,
            datetime.date(2023, 9, 13): 435.0,
            datetime.date(2023, 9, 14): 402.0,
            datetime.date(2023, 9, 15): 494.0}

        pywearable.sleep.get_total_sleep_time(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'TST': 461.42857142857144,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which TST must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform TST over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and TST as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `TST`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_TST,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_sleep_efficiency(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> pd.DataFrame:
    """Get sleep efficiency (SE) sleep metric.

    This function computes sleep efficiency (SE) metric as the ratio
    between TST (see :func:`get_total_sleep_time`) and TIB (see :func:`get_time_in_bed`).
    .. math:: SE = TST / TIB
    Depending on the value of the ``kind`` parameter, this function
    returns SE for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_sleep_efficiency(loader, user_id, start_date, end_date, kind=None)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 99.20159680638723,
            datetime.date(2023, 9, 10): 99.61089494163424,
            datetime.date(2023, 9, 11): 100.0,
            datetime.date(2023, 9, 12): 99.54233409610984,
            datetime.date(2023, 9, 13): 99.54233409610984,
            datetime.date(2023, 9, 14): 100.0,
            datetime.date(2023, 9, 15): 99.59677419354838}

        pywearable.sleep.get_sleep_efficiency(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'SE': 99.64199059054135,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which SE must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform SE over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and SE as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `SE`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_SE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_sleep_maintenance_efficiency(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> pd.DataFrame:
    """Get sleep maintenance efficiency (SME) sleep metric.

    This function computes sleep maintenance efficiency (SME) metric as the ratio
    between TST (see :func:`get_total_sleep_time`) and SPT (see :func:`get_sleep_period_time`).

    .. math:: SME = \\frac{TST}{SPT}

    Depending on the value of the ``kind`` parameter, this function
    returns SME for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_sleep_maintenance_efficiency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 99.20159680638723,
            datetime.date(2023, 9, 10): 99.61089494163424,
            datetime.date(2023, 9, 11): 100.0,
            datetime.date(2023, 9, 12): 99.54233409610984,
            datetime.date(2023, 9, 13): 99.54233409610984,
            datetime.date(2023, 9, 14): 100.0,
            datetime.date(2023, 9, 15): 99.59677419354838}

        pywearable.sleep.get_sleep_maintenance_efficiency(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'SE': 99.64199059054135,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which SME must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform SME over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and SME as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `SME`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_SME,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n1_latency(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get N1 sleep latency.

    This function computes the latency to the first stage of N1 sleep.
    Depending on the value of the ``kind`` parameter, this function
    returns N1 latency for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_n1_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 0.0,
            datetime.date(2023, 9, 10): 0.0,
            datetime.date(2023, 9, 11): 0.0,
            datetime.date(2023, 9, 12): 0.0,
            datetime.date(2023, 9, 13): 0.0,
            datetime.date(2023, 9, 14): 0.0,
            datetime.date(2023, 9, 15): 0.0}

        pywearable.sleep.get_n1_latency(loader, user_id, start_date, end_date, average=True)
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'Lat_N1': 0.0,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which N1 sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform N1 latency over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and N1 latency as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_N1`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N1_LATENCY,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n2_latency(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    """Get N2 sleep latency.

    This function computes the latency to the first stage of N2 sleep.
    Depending on the value of the ``kind`` parameter, this function
    returns N2 latency for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_n2_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 10.0,
            datetime.date(2023, 9, 10): 15.0,
            datetime.date(2023, 9, 11): 20.0,
            datetime.date(2023, 9, 12): 17.0,
            datetime.date(2023, 9, 13): 62.0,
            datetime.date(2023, 9, 14): 33.0,
            datetime.date(2023, 9, 15): 48.0}

        pywearable.sleep.get_n2_latency(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'Lat_N2': 29,285714285714285714285714285714,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which N2 sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform N2 latency over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and N2 latency as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_N2`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N2_LATENCY,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n3_latency(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get N3 sleep latency.

    This function computes the latency to the first stage of N3 sleep.
    Depending on the value of the ``kind`` parameter, this function
    returns N3 latency for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_n3_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 6.0,
            datetime.date(2023, 9, 10): 20.0,
            datetime.date(2023, 9, 11): 32.0,
            datetime.date(2023, 9, 12): 16.0,
            datetime.date(2023, 9, 13): 9.0,
            datetime.date(2023, 9, 14): 19.0,
            datetime.date(2023, 9, 15): 15.0}

        pywearable.sleep.get_n3_latency(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'Lat_N3': 15.0,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which N3 sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform N3 latency over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and N1 latency as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_N3`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N3_LATENCY,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_rem_latency(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get REM sleep latency.

    This function computes the latency to the first stage of REM sleep.
    Depending on the value of the ``kind`` parameter, this function
    returns REM latency for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_rem_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 47.0,
            datetime.date(2023, 9, 10): 119.0,
            datetime.date(2023, 9, 11): 69.0,
            datetime.date(2023, 9, 12): 57.0,
            datetime.date(2023, 9, 13): 79.0,
            datetime.date(2023, 9, 14): 167.0,
            datetime.date(2023, 9, 15): 52.0}

        pywearable.sleep.get_rem_latency(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'Lat_REM': 84.28571428571429,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which REM sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform REM latency over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and REM latency as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_REM`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_REM_LATENCY,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n1_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get N1 sleep duration.

    This function returns the absolute time spent in N1 sleep stage for
    the given user(s). Duration is reported in minutes.
    Depending on the value of the ``kind`` parameter, this function
    returns N1 duration for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_n1_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 280.0,
            datetime.date(2023, 9, 10): 256.0,
            datetime.date(2023, 9, 11): 333.0,
            datetime.date(2023, 9, 12): 312.0,
            datetime.date(2023, 9, 13): 288.0,
            datetime.date(2023, 9, 14): 233.0,
            datetime.date(2023, 9, 15): 295.0}

        pywearable.sleep.get_n1_duration(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'N1': 285.2857142857143,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pywearable.loader.base.BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which N1 sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    kind : :class:`str` or None, optional
        Whether to transform N1 duration over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and N1 duration as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `N1`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N1_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n2_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get N2 sleep duration.

    This function returns the absolute time spent in N2 sleep stage for
    the given user(s). Duration is reported in minutes.
    Depending on the value of the ``kind`` parameter, this function
    returns N2 duration for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_n2_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): nan,
            datetime.date(2023, 9, 10): nan,
            datetime.date(2023, 9, 11): nan,
            datetime.date(2023, 9, 12): nan,
            datetime.date(2023, 9, 13): nan,
            datetime.date(2023, 9, 14): nan,
            datetime.date(2023, 9, 15): nan}

        pywearable.sleep.get_n2_duration(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'N2': nan,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pywearable.loader.base.BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which N2 sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    kind : :class:`str` or None, optional
        Whether to transform N2 duration over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and N2 duration as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `N2`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N2_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n3_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get N3 sleep duration.

    This function returns the absolute time spent in N3 sleep stage for
    the given user(s). Depending on the value of the ``kind`` parameter, this function
    returns N1 duration for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Example::

        pywearable.sleep.get_n3_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 53.0,
            datetime.date(2023, 9, 10): 112.0,
            datetime.date(2023, 9, 11): 37.0,
            datetime.date(2023, 9, 12): 49.0,
            datetime.date(2023, 9, 13): 66.0,
            datetime.date(2023, 9, 14): 76.0,
            datetime.date(2023, 9, 15): 83.0}

        pywearable.sleep.get_n3_duration(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'N3': 68.0,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pywearable.loader.base.BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which N3 sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    kind : :class:`str` or None, optional
        Whether to transform N3 duration over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and N2 duration as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `N3`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N3_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_rem_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get REM sleep duration.

    This function returns the absolute time spent in REM sleep stage for
    the given user(s). Depending on the value of the ``kind`` parameter, this function
    returns REM duration for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Duration is reported in minutes.

    Example::

        pylabfront.sleep.get_rem_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 164.0,
            datetime.date(2023, 9, 10): 144.0,
            datetime.date(2023, 9, 11): 85.0,
            datetime.date(2023, 9, 12): 74.0,
            datetime.date(2023, 9, 13): 81.0,
            datetime.date(2023, 9, 14): 93.0,
            datetime.date(2023, 9, 15): 116.0}

        pylabfront.sleep.get_rem_duration(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'REM': 108.14285714285714,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pywearable.loader.base.BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which REM sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    kind : :class:`str` or None, optional
        Whether to transform REM duration over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and REM duration as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `REM`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_REM_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_nrem_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get NREM sleep duration.

    This function returns the absolute time spent in NREM sleep stage for
    the given user(s). Depending on the value of the ``kind`` parameter, this function
    returns N1 duration for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Duration is reported in minutes.

    Example::

        pywearable.sleep.get_nrem_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 333.0,
            datetime.date(2023, 9, 10): 368.0,
            datetime.date(2023, 9, 11): 370.0,
            datetime.date(2023, 9, 12): 361.0,
            datetime.date(2023, 9, 13): 354.0,
            datetime.date(2023, 9, 14): 309.0,
            datetime.date(2023, 9, 15): 433.0}

        pywearable.sleep.get_nrem_duration(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'NREM': 361.14285714285717,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pywearable.loader.base.BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which sleep data have to be extracted, by default "all".
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data.
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data.
        for the given ``user_id``, by default None
    kind : :class:`str` or None, optional
        Whether to transform NREM duration over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and NREM duration as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `NREM`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_NREM_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_awake_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get awake sleep duration.

    This function returns the absolute time spent in awake stage for
    the given user(s). Depending on the value of the ``kind`` parameter, this function
    returns awake duration for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Duration is reported in minutes.

    Example::

        pywearable.sleep.get_awake_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 4.0,
            datetime.date(2023, 9, 10): 2.0,
            datetime.date(2023, 9, 11): 0.0,
            datetime.date(2023, 9, 12): 2.0,
            datetime.date(2023, 9, 13): 2.0,
            datetime.date(2023, 9, 14): 0.0,
            datetime.date(2023, 9, 15): 5.0}

        pywearable.sleep.get_awake_duration(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'AWAKE': 2.142857142857143,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pywearable.loader.base.BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    kind : :class:`str` or None, optional
        Whether to transform awake duration over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and awake duration as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `AWAKE`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_AWAKE_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_unmeasurable_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    """Get unmeasurable sleep duration.

    This function returns the absolute time spent in unmeasurable sleep stage for
    the given user(s). Depending on the value of the ``kind`` parameter, this function
    returns unmeasurable sleep duration for each calendar day (``kind=None``)
    from ``start_date`` to ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Duration is reported in minutes.

    Example::

        pywearable.sleep.get_unmeasurable_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 0.0,
            datetime.date(2023, 9, 10): 0.0,
            datetime.date(2023, 9, 11): 0.0,
            datetime.date(2023, 9, 12): 0.0,
            datetime.date(2023, 9, 13): 0.0,
            datetime.date(2023, 9, 14): 0.0,
            datetime.date(2023, 9, 15): 0.0}

        pywearable.sleep.get_unmeasurable_duration(loader, user_id, start_date, end_date, kind='mean')
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'UNMEASURABLE': 0.0,
                        'days': ['2023-09-09',
                                    '2023-09-10',
                                    '2023-09-11',
                                    '2023-09-12',
                                    '2023-09-13',
                                    '2023-09-14',
                                    '2023-09-15'
                                ]
                    }
            }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        Initialized instance of :class:`pywearable.loader.base.BaseLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    kind : :class:`str` or None, optional
        Whether to transform unmeasurable sleep duration over days, or to return the value for each day, by default None.
        Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and unmeasurable sleep duration as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `UNMEASURABLE`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_UNMEASURABLE_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n1_percentage(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N1_PERCENTAGE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n2_percentage(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N2_PERCENTAGE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n3_percentage(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N3_PERCENTAGE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_rem_percentage(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_REM_PERCENTAGE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_nrem_percentage(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_NREM_PERCENTAGE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_wake_after_sleep_onset(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_WASO,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_sleep_onset_latency(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_SOL,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_sleep_score(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_SLEEP_SCORE,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_sleep_timestamps(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
):
    """Get the timestamps of the beginning and the end of sleep occurrences.

    Returns for every day, the time when the user fell asleep and when he woke up
    The information is based on the sleep summaries of the user

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which sleep timestamps are computed, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.

    Returns
    -------
    :class:`dict`
        Dictionary with user ids as primary keys, calendar dates as secondary keys, 
        and sleep timestamps (bedtime, wakeup_time) as values
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        try:
            bedtime_dict = get_bedtime(loader,
                    user,
                    start_date,
                    end_date)[user]

            wakeup_time_dict = get_wakeup_time(loader,
                    user,
                    start_date,
                    end_date)[user]
            data_dict[user] = {k:(bedtime_dict.get(k, None), 
                              wakeup_time_dict.get(k, None)) for k in bedtime_dict.keys()}
        except:
            pass

    return data_dict


def get_bedtime(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_BEDTIME,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_wakeup_time(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_WAKEUP_TIME,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_sleep_midpoint(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
) -> dict:
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_MIDPOINT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_awake_count(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    """Get the number of awakenings

    Returns the number of times the user(s) of interest woke up during the night.
    Depending on the value of the ``kind`` parameter, this function
    returns the count of awake stages for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user_id : :class:`str`, optional
        ID of the user for which awakenings are computed, by default "all".
    start_date : :class:`datetime.datetime`, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime`, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform count of awake stages over days, or to return the value for each
        day, by default None. Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and count of awake stages as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `countAwake`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_AWAKE_COUNT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n1_count(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    """Get the number of N1 sleep stages.

    Returns the number of N1 sleep stages for the user(s) of interest.
    This is checked. If ``average`` is set to True, the average number of
    awakenings per night during the period between ``start_date`` and ``end_date`` is returned.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user_id : :class:`str`, optional
        ID of the user for which awakenings are computed, by default "all".
    start_date : :class:`datetime.datetime`, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime`, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to return only the average number of awakenings per night for the user, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with user ids as primary keys, dates as secondary keys, and number of awakenings as values.
        If `average` is set to True, the average and the dates used for its calculation are returned as values.
    """

    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N1_COUNT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n2_count(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    """Get the number of N2 sleep stages.

    Returns the number of N2 sleep stages for the user(s) of interest.
    Depending on the value of the ``kind`` parameter, this function
    returns the count of N2 stages for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user_id : :class:`str`, optional
        ID of the user for which awakenings are computed, by default "all".
    start_date : :class:`datetime.datetime`, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime`, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform count of N2 stages over days, or to return the value for each
        day, by default None. Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and count of N2 stages as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `countN2`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N2_COUNT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_n3_count(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    """Get the number of N3 sleep stages.

    Returns the number of N3 sleep stages for the user(s) of interest.
    Depending on the value of the ``kind`` parameter, this function
    returns the count of N3 stages for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user_id : :class:`str`, optional
        ID of the user for which awakenings are computed, by default "all".
    start_date : :class:`datetime.datetime`, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime`, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform count of N3 stages over days, or to return the value for each
        day, by default None. Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and count of N3 stages as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `countN3`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_N3_COUNT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_rem_count(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
):
    """Get the number of REM sleep stages.

    Returns the number of REM sleep stages for the user(s) of interest.
    Depending on the value of the ``kind`` parameter, this function
    returns the count of REM stages for each calendar day (``kind=None``) from ``start_date`` to
    ``end_date`` or the transformed value across all days. The applied
    transformation depends on the value of the ``kind`` parameter:

        - `mean`: computes the average across days
        - `std`: computes the standard deviation across days
        - `min`: computes the minimum value across days
        - `max`: computes the maximum value across days

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user_id : :class:`str`, optional
        ID of the user for which awakenings are computed, by default "all".
    start_date : :class:`datetime.datetime`, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime`, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to transform count of REM stages over days, or to return the value for each
        day, by default None. Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and count of REM stages as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `countREM`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """

    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_REM_COUNT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
    )


def get_cpd_midpoint(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    chronotype_dict: dict = {},
):
    """Computes composite phase deviation (CPD)

    Returns a measure of sleep regularity, in terms of stability of rest midpoints.
    The measure is computed for the period between `start_date` and `end_date`
    for every user_id of interest.

    Parameters
    ----------
    loader : `pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which CPD must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to compute a transformation of CPD over days, or to return the value for each
        day, by default None. Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    chronotype_dict : :class:`dict`, optional
        dictionary specifying for every user his usual sleeping time and waking time in format HH:MM, as a tuple

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and CPD midpoints as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `CPD_midpoint`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_CPD_MIDPOINT,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        chronotype_dict=chronotype_dict,
    )


def get_cpd_duration(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    chronotype_dict: dict = {},
):
    """Computes composite phase deviation (CPD)

    Returns a measure of sleep regularity, in terms of sleep duration.
    The measure is computed for the period between `start_date` and `end_date`
    for every user_id of interest.

    Parameters
    ----------
    loader : `pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which CPD must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to compute a transformation of CPD over days, or to return the value for each
        day, by default None. Valid options are:

            - `mean`
            - `std`
            - `min`
            - `max`

    chronotype_dict : :class:`dict`, optional
        dictionary specifying for every user his usual sleeping time and waking time in format HH:MM, as a tuple

    Returns
    -------
    :class:`dict`
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (:class:`datetime.date`) as keys and CPD midpoints as values.
        If ``kind!=None``, dictionary with ``user_id`` as key, and a nested dictionary with `CPD_midpoint`
        as key and its transformed value, and an additional `days` keys that contains an array of all
        calendar days over which the transformation was computed.
    """
    return get_sleep_statistic(
        loader=loader,
        user_id=user_id,
        metric=_SLEEP_METRIC_CPD_DURATION,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        chronotype_dict=chronotype_dict,
    )


def _compute_sleep_score(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Retrieves sleep score from a sleep summary

    This function retrieves, if available, the sleep scores
    given sleep summary data.

    Parameters
    ----------
    sleep_summary : :class:`pandas.DataFrame`
        Sleep summary data.

    Returns
    -------
    pd.Series
        Sleep score data.

    Raises
    ------
    ValueError
        If `sleep_summary` is not a :class:`pandas.DataFrame` .
    """
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    if constants._SLEEP_SUMMARY_OVERALL_SLEEP_SCORE_COL in sleep_summary.columns:
        sleep_score = sleep_summary[constants._SLEEP_SUMMARY_OVERALL_SLEEP_SCORE_COL]
    else:
        sleep_score = pd.Series()
    return sleep_score


def _compute_time_in_bed(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute Time in Bed (TIB) metric for sleep data.

    This function computes the TIB as the total duration of the sleep,
    considering both awake and unmeasurable sleep stages.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        TIB data.

    Raises
    ------
    ValueError
        If `sleep_summary` is not a :class:`pd.DataFrame`.
    """
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    # TIB = SLEEP_DURATION + AWAKE_DURATION in minutes
    if (constants._SLEEP_SUMMARY_DURATION_IN_MS_COL in sleep_summary.columns) and (
        constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL in sleep_summary.columns
    ):
        tib = (
            sleep_summary[constants._SLEEP_SUMMARY_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL]
        ) / (
            1000 * 60
        )  # convert from ms to seconds, and then to minutes
    else:
        tib = pd.Series()
    return tib


def _compute_total_sleep_time(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute Total Sleep Time (TST) metric for sleep data.

    This function computes the TST as the total duration of the N1, N2, N3,
    and REM sleep stages within sleep period time (SPT).

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        TST data.

    Raises
    ------
    ValueError
        If `sleep_summary` is not a :class:`pd.DataFrame`.
    """
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    # TST = N1+N2+N3+REM
    if (
        (constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL in sleep_summary.columns)
        and (
            constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
    ):
        tst = (
            sleep_summary[constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL].fillna(
                0
            )
            + sleep_summary[
                constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
            + sleep_summary[
                constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
            + sleep_summary[
                constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
        ) / (
            1000 * 60
        )  # convert from ms to seconds, and then to minutes
    else:
        tst = pd.Series()
    return tst


def _compute_sleep_efficiency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Compute Sleep Efficiency (SE) metric for sleep data.

    This function computes the SE as the ratio between Total Sleep Time (TST)
    and Time in Bed (TIB).

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        SE data.

    Raises
    ------
    ValueError
        If `sleep_summary` is not a :class:`pd.DataFrame`.
    """
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    # SE = SLEEP_DURATION / (SLEEP_DURATION + AWAKE_DURATION) * 100
    tst = _compute_total_sleep_time(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    tib = _compute_time_in_bed(sleep_summary=sleep_summary, sleep_stages=sleep_stages)
    se = tst / tib * 100
    return se


def _compute_sleep_maintenance_efficiency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Compute Sleep Maintenance efficiency (SME) metric for sleep data.

    This function computes the SME as the ratio between
    the sum of all non-wake sleep stages (N1+N2+N2+REM)
    and Sleep Period Time (SPT).

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages data.

    Returns
    -------
    :class:`pd.Series`
        SME data.

    Raises
    ------
    ValueError
        If `sleep_summary` is not a :class:`pd.DataFrame`.
    """
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    # SME = (N1+N2+N3+REM) / (SPT) * 100
    tst = _compute_total_sleep_time(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    spt = _compute_sleep_period_time(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    sme = tst / spt * 100
    return sme


def _compute_sleep_stage_percentage(
    sleep_summary: pd.DataFrame, sleep_stage: str, **kwargs
) -> pd.Series:
    """Compute the percentage of time spent in a sleep stage.

    This function computes the percentage of time in a sleep stage
    as the ratio between the time spent in it and the
    total sleep time.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.
    sleep_stage : :class:`str`
        Name of the sleep stage of interest.

    Returns
    -------
    :class:`pd.Series`
        Percentage of time spent in `sleep_stage` per night.

    Raises
    ------
    ValueError
        If `sleep_summary` is not a :class:`pd.DataFrame`.
    ValueError
        if `sleep_stage` isn't one of "N1","N3","REM","NREM".
    """
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    if (
        (constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL in sleep_summary.columns)
        and (
            constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
    ):
        tot_duration = (
            sleep_summary[constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL].fillna(
                0
            )
            + sleep_summary[
                constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
            + sleep_summary[
                constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
            + sleep_summary[
                constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
        )
        if sleep_stage == "NREM":
            perc = (
                (
                    tot_duration
                    - sleep_summary[
                        constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
                    ].fillna(0)
                )
                / tot_duration
                * 100
            )
        else:
            if sleep_stage == "N1":
                col = constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL
            elif sleep_stage == "N2":
                col = constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
            elif sleep_stage == "N3":
                col = constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL
            elif sleep_stage == "REM":
                col = constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            else:
                raise ValueError(
                    f"{sleep_stage} is not a valid value. Select among [N1, N2, N3, REM, NREM]"
                )
            perc = (sleep_summary[col]) / tot_duration * 100
    else:
        perc = pd.Series()
    return perc


def _compute_n1_percentage(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the percentage of time spent in the N1 sleep stage.

    This function computes the percentage of time in N1
    as the ratio between the time spent in it and the sum of the
    time spent sleeping.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Percentage of time spent in N1 per night.
    """
    return _compute_sleep_stage_percentage(sleep_summary, "N1")


def _compute_n2_percentage(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the percentage of time spent in the N2 sleep stage.

    This function computes the percentage of time in N2
    as the ratio between the time spent in it and the sum of the
    time spent sleeping.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Percentage of time spent in N2 per night.
    """
    return _compute_sleep_stage_percentage(sleep_summary, "N2")


def _compute_n3_percentage(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the percentage of time spent in the N3 sleep stage.

    This function computes the percentage of time in N3
    as the ratio between the time spent in it and the sum of the
    time spent sleeping.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Percentage of time spent in N3 per night.
    """
    return _compute_sleep_stage_percentage(sleep_summary, "N3")


def _compute_rem_percentage(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the percentage of time spent in the REM sleep stage.

    This function computes the percentage of time in REM
    as the ratio between the time spent in it and the sum of the
    time spent sleeping.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Percentage of time spent in REM per night.
    """
    return _compute_sleep_stage_percentage(sleep_summary, "REM")


def _compute_nrem_percentage(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the percentage of time spent in the NREM sleep stage.

    This function computes the percentage of time in NREM
    as the ratio between the time spent in it and the sum of the
    time spent sleeping.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Percentage of time spent in NREM per night.
    """
    return _compute_sleep_stage_percentage(sleep_summary, "NREM")


def _compute_sleep_stage_duration(
    sleep_summary: pd.DataFrame, sleep_stage: str, **kwargs
) -> pd.Series:
    """Compute the duration of a specified sleep stage.

    This function computes the time spent (in minutes)
    in a specific sleep stage.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.
    sleep_stage : :class:`str`
        Name of a sleep stage.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes spent in `sleep_stage` per night.

    Raises
    ------
    ValueError
        If `sleep_summary` is not a :class:`pd.DataFrame`.
    ValueError
        if `sleep_stage` isn't one of "N1","N2", "N3","REM","NREM","AWAKE","UNMEASURABLE".
    """
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    if sleep_stage == "NREM":
        tot_duration = (
            sleep_summary[constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL].fillna(
                0
            )
            + sleep_summary[
                constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
            + sleep_summary[
                constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
            + sleep_summary[
                constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
        )
        dur = (
            tot_duration
            - sleep_summary[
                constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            ].fillna(0)
        ) / (1000 * 60)
    else:
        if sleep_stage == "N1":
            col = constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL
        elif sleep_stage == "N2":
            col = constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
        elif sleep_stage == "N3":
            col = constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL
        elif sleep_stage == "REM":
            col = constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
        elif sleep_stage == "AWAKE":
            col = constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL
        elif sleep_stage == "UNMEASURABLE":
            col = constants._SLEEP_SUMMARY_UNMEASURABLE_SLEEP_DURATION_IN_MS_COL
        else:
            raise ValueError(
                f"{sleep_stage} is not a valid value. Select among [N1, N2, N3, REM, NREM, AWAKE, UNMEASURABLE]"
            )
        dur = (sleep_summary[col]) / (1000 * 60)
    return dur


def _compute_n1_duration(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the duration of the N1 sleep stage.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes spent in N1 per night.
    """
    return _compute_sleep_stage_duration(sleep_summary, "N1")


def _compute_n2_duration(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the duration of the N2 sleep stage.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes spent in N2 per night.
    """
    return _compute_sleep_stage_duration(sleep_summary, "N2")


def _compute_n3_duration(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the duration of the N3 sleep stage.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes spent in N3 per night.
    """
    return _compute_sleep_stage_duration(sleep_summary, "N3")


def _compute_rem_duration(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the duration of the REM sleep stage.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes spent in REM per night.
    """
    return _compute_sleep_stage_duration(sleep_summary, "REM")


def _compute_nrem_duration(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the duration of the NREM sleep stages.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes spent in NREM per night.
    """
    return _compute_sleep_stage_duration(sleep_summary, "NREM")


def _compute_awake_duration(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the amount of time spent awake during the night

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes spent in awake per night.
    """
    return _compute_sleep_stage_duration(sleep_summary, "AWAKE")


def _compute_unmeasurable_duration(sleep_summary: pd.DataFrame, **kwargs) -> pd.Series:
    """Compute the duration of unmeasurable sleep in a night.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summary data.

    Returns
    -------
    :class:`pd.Series`
        Amount of minutes where sleep was unmeasurable per night.
    """
    return _compute_sleep_stage_duration(sleep_summary, "UNMEASURABLE")


def _compute_sleep_period_time(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Compute sleep period time.

    This function computes sleep period time, that is the
    duration from first to last period of sleep.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    :class:`pd.Series`
        Series with sleep period time as values, and sleep summary ids as index.
    """
    # Check inputs
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    sleep_stages = utils.check_is_df(sleep_stages, "sleep_stages")
    if len(sleep_summary) == 0:
        return pd.Series()
    if len(sleep_stages) == 0:
        return pd.Series(index=sleep_summary.index)

    def sleep_diff(group):
        start = group[constants._UNIXTIMESTAMP_IN_MS_COL]
        duration = group[constants._SLEEP_STAGE_DURATION_IN_MS_COL]
        return (start.iloc[-1] + duration.iloc[-1] - start.iloc[0]) / (1000 * 60)

    # Get only sleep stages of interest
    filtered_sleep_stages = sleep_stages[
        sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
            sleep_summary.index
        )
    ].reset_index(drop=True)
    spt = pd.Series(
        filtered_sleep_stages[
            filtered_sleep_stages[constants._SLEEP_STAGE_SLEEP_TYPE_COL]
            != constants._SLEEP_STAGE_AWAKE_STAGE_VALUE
        ]
        .reset_index(drop=True)
        .groupby(constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL)
        .apply(sleep_diff),
        index=sleep_summary.index,
    )
    return spt


def _compute_sleep_onset_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Compute sleep onset latency.

    This function computes the latency to the
    first sleep stage.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    :class:`pd.Series`
        Series with sleep onset latency.
    """
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    sleep_stages = utils.check_is_df(sleep_stages, "sleep_stages")
    if len(sleep_summary) == 0:
        return pd.Series()
    if len(sleep_stages) == 0:
        return pd.Series(index=sleep_summary.index)
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    # Remove awake latency
    if constants._SLEEP_STAGE_AWAKE_STAGE_VALUE in latencies.columns:
        latencies = latencies.drop([constants._SLEEP_STAGE_AWAKE_STAGE_VALUE], axis=1)
    # Remove unmeasurable latency in case it is there
    if constants._SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE in latencies.columns:
        latencies = latencies.drop(
            [constants._SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE], axis=1
        )
    # Return minimum latency
    return latencies.min(axis=1)


def _compute_wake_after_sleep_onset(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Compute wake after sleep onset.

    This function returns the total number of minutes
    spent awake after the sleep onset.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    :class:`pd.Series`
        Series with wake after sleep onset data.
    """
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    sleep_stages = utils.check_is_df(sleep_stages, "sleep_stages")
    if len(sleep_summary) == 0:
        return pd.Series()
    if len(sleep_stages) == 0:
        return pd.Series(index=sleep_summary.index)

    # Get only sleep stages belonging to the sleep summaries of interest
    filtered_sleep_stages = sleep_stages[
        sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
            sleep_summary.index
        )
    ].reset_index(drop=True)
    # Get first sleep stages that are awake and remove them
    first_sleep_stages = filtered_sleep_stages.drop_duplicates(
        subset=[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL], keep="first"
    )
    first_sleep_stages = first_sleep_stages[
        first_sleep_stages[constants._SLEEP_STAGE_SLEEP_TYPE_COL]
        == constants._SLEEP_STAGE_AWAKE_STAGE_VALUE
    ]
    filtered_sleep_stages = filtered_sleep_stages[
        ~filtered_sleep_stages.index.isin(first_sleep_stages.index)
    ]
    # Get last sleep stages that are awake and remove them
    last_sleep_stages = filtered_sleep_stages.drop_duplicates(
        subset=[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL], keep="last"
    )
    last_sleep_stages = last_sleep_stages[
        last_sleep_stages[constants._SLEEP_STAGE_SLEEP_TYPE_COL]
        == constants._SLEEP_STAGE_AWAKE_STAGE_VALUE
    ]
    filtered_sleep_stages = filtered_sleep_stages[
        ~filtered_sleep_stages.index.isin(last_sleep_stages.index)
    ]
    # Compute WASO with groupby operation
    waso = pd.Series(
        filtered_sleep_stages[
            filtered_sleep_stages[constants._SLEEP_STAGE_SLEEP_TYPE_COL]
            == constants._SLEEP_STAGE_AWAKE_STAGE_VALUE
        ]
        .groupby(constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL)[
            constants._SLEEP_SUMMARY_DURATION_IN_MS_COL
        ]
        .sum(),
        index=sleep_summary.index,
    ) / (1000 * 60)
    # Set values to 0 for sleep summaries with no awake stages
    waso.loc[
        (waso.index.isin(filtered_sleep_stages[constants._SLEEP_SUMMARY_ID_COL]))
        & (waso.isna())
    ] = 0
    return waso


def _compute_n1_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.DataFrame:
    """Compute N1 latency from sleep data.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    :class:`pd.DataFrame`
        A DataFrame with N1 Latency as value, and sleep summary ids as indexes.
    """
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    return pd.Series(latencies[constants._SLEEP_STAGE_N1_STAGE_VALUE])


def _compute_n2_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Compute N2 latency from sleep data.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    :class:`pd.Series`
        A series with N2 Latency as value, and sleep summary ids as indexes.
    """
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    return pd.Series(latencies[constants._SLEEP_STAGE_N2_STAGE_VALUE])


def _compute_n3_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.DataFrame:
    """Compute N3 latency from sleep data.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    :class:`pd.Series`
        A series with N3 Latency as value, and sleep summary ids as indexes.
    """
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    return pd.Series(latencies[constants._SLEEP_STAGE_N3_STAGE_VALUE])


def _compute_rem_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Computes REM Latency from sleep data.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    :class:`pd.Series`
        A series with REM Latency as value, and sleep summary ids as index.
    """
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    return pd.Series(latencies[constants._SLEEP_STAGE_REM_STAGE_VALUE])


def _compute_latencies(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.DataFrame:
    """Compute sleep stages latencies.

    This function computes latencies for each sleep stage
    contained in ``sleep_stages`.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        Sleep summaries, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_summary`.
        The index of the ``sleep_summary`` must be set to the unique `sleepSummaryId`.
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages, that can be extracted using :method:`pywearable.loader.base.BaseLoader.load_sleep_stage`.

    Returns
    -------
    pd.DataFrame
        The returned :class:`pd.DataFrame` has as index the
        values of the ids of the sleep summary to which they
        refer to, and one column for each sleep stage:
        awake, light, deep, and rem.

    Raises
    ------
    ValueError
        If `sleep_summary` or `sleep_stages` are not of type :class:`pd.DataFrame`
    """
    # Check input
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    sleep_stages = utils.check_is_df(sleep_stages, "sleep_stages")
    # Check lenght of input
    if len(sleep_summary) == 0:
        return pd.DataFrame(
            columns=[
                constants._SLEEP_STAGE_AWAKE_STAGE_VALUE,
                constants._SLEEP_STAGE_N1_STAGE_VALUE,
                constants._SLEEP_STAGE_N2_STAGE_VALUE,
                constants._SLEEP_STAGE_N3_STAGE_VALUE,
                constants._SLEEP_STAGE_REM_STAGE_VALUE,
            ]
        )
    if len(sleep_stages) == 0:
        return pd.DataFrame(
            index=sleep_summary.index,
            columns=[
                constants._SLEEP_STAGE_AWAKE_STAGE_VALUE,
                constants._SLEEP_STAGE_N1_STAGE_VALUE,
                constants._SLEEP_STAGE_N2_STAGE_VALUE,
                constants._SLEEP_STAGE_N3_STAGE_VALUE,
                constants._SLEEP_STAGE_REM_STAGE_VALUE,
            ],
        )
    # Get only sleep stages with valid sleepSummaryId
    filtered_sleep_stages = sleep_stages[
        sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
            sleep_summary.index
        )
    ].reset_index(drop=True)
    # Compute latencies by groupby operation
    latencies = (
        filtered_sleep_stages.groupby(
            [
                constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL,
                constants._SLEEP_STAGE_SLEEP_TYPE_COL,
            ]
        )[constants._ISODATE_COL].first()
        - sleep_summary[constants._ISODATE_COL]
    ).dt.total_seconds() / (60)

    # Pivot
    latencies = latencies.rename("latency")
    latencies = latencies.reset_index().pivot(
        columns=constants._SLEEP_STAGE_SLEEP_TYPE_COL,
        index=constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL,
        values="latency",
    )
    # Add columns if they are not there
    for stage in [
        constants._SLEEP_STAGE_AWAKE_STAGE_VALUE,
        constants._SLEEP_STAGE_N1_STAGE_VALUE,
        constants._SLEEP_STAGE_N2_STAGE_VALUE,
        constants._SLEEP_STAGE_N3_STAGE_VALUE,
        constants._SLEEP_STAGE_REM_STAGE_VALUE,
    ]:
        if stage not in latencies.columns:
            latencies[stage] = np.nan

    latencies = latencies.rename_axis(None, axis=1)
    # Add missing sleepSummary from sleep_summary index
    latencies = pd.merge(
        left=sleep_summary.loc[:, []],
        right=latencies,
        left_index=True,
        right_index=True,
        how="outer",
    )
    return latencies


def _compute_awake_count(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    """Retrieves awakenings counts score from sleep stages.

    This function retrieves the count of awakenings
    events occured per night.

    Parameters
    ----------
    sleep_summary : :class:`pandas.DataFrame`
        Sleep summary data with sleepSummaryId as index.
    sleep_stages : :class:`pandas.DataFrame`
        Sleep stages.

    Returns
    -------
    pd.Series
        Count of awakenings.

    Raises
    ------
    ValueError
        If parameters are not of :class:`pandas.DataFrame` .
    """
    count_stage = _compute_stage_count(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    if len(count_stage) == 0:
        return pd.Series()
    if constants._SLEEP_STAGE_AWAKE_STAGE_VALUE in count_stage.columns:
        return count_stage[constants._SLEEP_STAGE_AWAKE_STAGE_VALUE]
    else:
        return pd.Series(index=sleep_summary.index)


def _compute_n1_count(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    count_stage = _compute_stage_count(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    if len(count_stage) == 0:
        return pd.Series()
    if constants._SLEEP_STAGE_N1_STAGE_VALUE in count_stage.columns:
        return count_stage[constants._SLEEP_STAGE_N1_STAGE_VALUE]
    else:
        return pd.Series(index=sleep_summary.index)


def _compute_n2_count(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    count_stage = _compute_stage_count(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    if len(count_stage) == 0:
        return pd.Series()
    if constants._SLEEP_STAGE_N2_STAGE_VALUE in count_stage.columns:
        return count_stage[constants._SLEEP_STAGE_N2_STAGE_VALUE]
    else:
        return pd.Series(index=sleep_summary.index)


def _compute_n3_count(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    count_stage = _compute_stage_count(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    if len(count_stage) == 0:
        return pd.Series()
    if constants._SLEEP_STAGE_N3_STAGE_VALUE in count_stage.columns:
        return count_stage[constants._SLEEP_STAGE_N3_STAGE_VALUE]
    else:
        return pd.Series(index=sleep_summary.index)


def _compute_rem_count(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.Series:
    count_stage = _compute_stage_count(
        sleep_summary=sleep_summary, sleep_stages=sleep_stages
    )
    if len(count_stage) == 0:
        return pd.Series()
    if constants._SLEEP_STAGE_REM_STAGE_VALUE in count_stage.columns:
        return count_stage[constants._SLEEP_STAGE_REM_STAGE_VALUE]
    else:
        return pd.Series(index=sleep_summary.index)


def _compute_stage_count(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame, **kwargs
) -> pd.DataFrame:
    # Check is dataframe
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    sleep_stages = utils.check_is_df(sleep_stages, "sleep_stages")
    # Check that we have data
    if len(sleep_summary) == 0:
        return pd.DataFrame()
    if len(sleep_stages) == 0:
        return pd.DataFrame(index=sleep_summary.index)

    # Get only sleep_stages with sleepSummaryId contained in sleep_summary
    filtered_sleep_stages = sleep_stages[
        sleep_stages[constants._SLEEP_SUMMARY_ID_COL].isin(sleep_summary.index)
    ].reset_index(drop=True)

    # Check that we have sleep stages
    if len(filtered_sleep_stages) == 0:
        return pd.Series(index=sleep_summary.index)

    # Count the number of awake sleep stages for each group of sleep stages
    count_df = (
        filtered_sleep_stages.groupby([constants._SLEEP_SUMMARY_ID_COL])[
            constants._SLEEP_STAGE_SLEEP_TYPE_COL
        ]
        .value_counts()
        .reset_index()
        .pivot(
            columns=constants._SLEEP_STAGE_SLEEP_TYPE_COL,
            index=constants._SLEEP_SUMMARY_ID_COL,
            values="count",
        )
    )
    count_df = count_df.fillna(0)
    count_df = pd.merge(
        left=sleep_summary.loc[:, []],
        right=count_df,
        left_index=True,
        right_index=True,
        how="outer",
    )
    for col in [
        constants._SLEEP_STAGE_AWAKE_STAGE_VALUE,
        constants._SLEEP_STAGE_REM_STAGE_VALUE,
        constants._SLEEP_STAGE_N1_STAGE_VALUE,
        constants._SLEEP_STAGE_N3_STAGE_VALUE,
        constants._SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE,
    ]:
        if not col in count_df.columns:
            count_df[col] = np.nan
    return count_df

def _compute_bedtime(
    sleep_summary: pd.DataFrame, **kwargs
) -> pd.Series:
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    if constants._SLEEP_SUMMARY_OVERALL_SLEEP_SCORE_COL in sleep_summary.columns:
        bedtime = sleep_summary[constants._ISODATE_COL]
    else:
        bedtime = pd.Series()
    return bedtime

def _compute_wakeup_time(
    sleep_summary: pd.DataFrame, **kwargs
) -> pd.Series:

    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")

    if np.all([constants._SLEEP_SUMMARY_DURATION_IN_MS_COL in sleep_summary.columns,
               constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL in sleep_summary.columns,
               constants._UNIXTIMESTAMP_IN_MS_COL in sleep_summary.columns,
               constants._TIMEZONEOFFSET_IN_MS_COL in sleep_summary.columns]
            ):
        wakeup_time = pd.to_datetime(
                sleep_summary[constants._UNIXTIMESTAMP_IN_MS_COL]
                + sleep_summary[constants._TIMEZONEOFFSET_IN_MS_COL]
                + sleep_summary[constants._DURATION_IN_MS_COL]
                + sleep_summary[constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL],
                unit="ms",
                utc=True,
            ).dt.tz_localize(None)
    else:
        wakeup_time = pd.Series()
    return wakeup_time

def _compute_sleep_midpoint(
        sleep_summary: pd.DataFrame, **kwargs
) -> pd.Series:
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")
    wakeup_time = _compute_wakeup_time(sleep_summary=sleep_summary, **kwargs)
    bedtime = _compute_bedtime(sleep_summary=sleep_summary, **kwargs)
    if len(wakeup_time) == len(bedtime) and len(wakeup_time) != 0:
       midpoints =  pd.Series(data=[bed + (wake - bed)/2 for bed,wake in zip(bedtime,wakeup_time)], 
                              index=wakeup_time.index)
    else:
        midpoints = pd.Series()
    return midpoints


def _compute_cpd_midpoint(
    sleep_summary: pd.DataFrame, chronotype: Union[tuple, None], **kwargs
):
    # Check is dataframe
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")

    # get midpoints for period of interest
    midpoints = _compute_sleep_midpoint(sleep_summary=sleep_summary, **kwargs)
    midpoints = OrderedDict(zip(sleep_summary[constants._CALENDAR_DATE_COL], 
                                midpoints.dt.to_pydatetime()))

    if (
        chronotype is None
    ):  # if chronotype isn't explicitely given, calculate the midpoint from the available data
        chronotype_midpoint = utils.mean_time(
            [midpoint.strftime("%H:%M") for midpoint in list(midpoints.values())]
        )
    else:  # from specified times
        chronotype_midpoint = utils.mean_time(chronotype)

    previous_midpoint = None  # the first day will have irregularity component 0
    CPDs = []

    if len(midpoints) == 1:
        warnings.warn("Only one day is considered: CPD is only influenced by the mistiming component wrt the chronotype.")

    for calendar_date, midpoint in list(midpoints.items()):
        # mistiming component
        chronotype_daily_midpoint = datetime.datetime(
            calendar_date.year,
            calendar_date.month,
            calendar_date.day,
            hour=int(chronotype_midpoint[:2]),
            minute=int(chronotype_midpoint[3:]),
        )
        # if the expected midpoint is prior to midnight we need to adjust the day
        if 14 < int(chronotype_midpoint[:2]) < 24:
            chronotype_daily_midpoint -= datetime.timedelta(days=1)

        mistiming_component = (chronotype_daily_midpoint - midpoint).total_seconds() / (
            60 * 60
        )

        # irregularity component
        if previous_midpoint is None: 
            irregularity_component = 0
        else:
            previous_day_midpoint_proxy = datetime.datetime(
                calendar_date.year,
                calendar_date.month,
                calendar_date.day,
                hour=previous_midpoint.hour,
                minute=previous_midpoint.minute,
                second=previous_midpoint.second,
            )

            if 14 < previous_day_midpoint_proxy.hour < 24:
                previous_day_midpoint_proxy -= datetime.timedelta(days=1)

            irregularity_component = (
                previous_day_midpoint_proxy - midpoint
            ).total_seconds() / (60 * 60)

        previous_midpoint = midpoint

        cpd = np.sqrt(mistiming_component**2 + irregularity_component**2)
        CPDs.append(cpd)

    return pd.Series(data=CPDs, index=sleep_summary.index)


def _compute_cpd_duration(
    sleep_summary: pd.DataFrame, chronotype: Union[tuple, None], **kwargs
):
    # Check is dataframe
    sleep_summary = utils.check_is_df(sleep_summary, "sleep_summary")

    durations = (sleep_summary[constants._SLEEP_STAGE_DURATION_IN_MS_COL]) / (
        1000 * 60 * 60
    )  # convert from ms to hours

    if chronotype is None:  # from data
        chronotype_sleep_duration = durations.mean()
    else:  # from specified times
        chronotype_start = chronotype[0]
        chronotype_end = chronotype[1]
        chronotype_sleep_duration = (
            datetime.datetime.strptime(chronotype_end, "%H:%M")
            - datetime.datetime.strptime(chronotype_start, "%H:%M")
        ).total_seconds() / (
            60 * 60
        )  # convert to hours
        if chronotype_sleep_duration < 0:  # takes care of sleep-time prior to midnight
            chronotype_sleep_duration += 24

    if len(durations) == 1:
        warnings.warn("Only one day is considered: CPD is only influenced by the mistiming component wrt the chronotype.")

    CPDs = []
    previous_duration = None  # first irregularity component will be 0

    for duration in durations:
        mistiming_component = chronotype_sleep_duration - duration

        if previous_duration is None:
            irregularity_component = 0
        else:
            irregularity_component = previous_duration - duration

        previous_duration = duration

        cpd = np.sqrt(mistiming_component**2 + irregularity_component**2)
        CPDs.append(cpd)

    return pd.Series(data=CPDs, index=sleep_summary.index)


_SLEEP_STATISTICS_DICT = {
    _SLEEP_METRIC_TIB: _compute_time_in_bed,
    _SLEEP_METRIC_TST: _compute_total_sleep_time,
    _SLEEP_METRIC_SE: _compute_sleep_efficiency,
    _SLEEP_METRIC_SME: _compute_sleep_maintenance_efficiency,
    _SLEEP_METRIC_SPT: _compute_sleep_period_time,
    _SLEEP_METRIC_WASO: _compute_wake_after_sleep_onset,
    _SLEEP_METRIC_SOL: _compute_sleep_onset_latency,
    _SLEEP_METRIC_N1_DURATION: _compute_n1_duration,
    _SLEEP_METRIC_N2_DURATION: _compute_n2_duration,
    _SLEEP_METRIC_N3_DURATION: _compute_n3_duration,
    _SLEEP_METRIC_REM_DURATION: _compute_rem_duration,
    _SLEEP_METRIC_NREM_DURATION: _compute_nrem_duration,
    _SLEEP_METRIC_AWAKE_DURATION: _compute_awake_duration,
    _SLEEP_METRIC_UNMEASURABLE_DURATION: _compute_unmeasurable_duration,
    _SLEEP_METRIC_N1_PERCENTAGE: _compute_n1_percentage,
    _SLEEP_METRIC_N2_PERCENTAGE: _compute_n2_percentage,
    _SLEEP_METRIC_N3_PERCENTAGE: _compute_n3_percentage,
    _SLEEP_METRIC_REM_PERCENTAGE: _compute_rem_percentage,
    _SLEEP_METRIC_NREM_PERCENTAGE: _compute_nrem_percentage,
    _SLEEP_METRIC_N1_LATENCY: _compute_n1_latency,
    _SLEEP_METRIC_N2_LATENCY: _compute_n2_latency,
    _SLEEP_METRIC_N3_LATENCY: _compute_n3_latency,
    _SLEEP_METRIC_REM_LATENCY: _compute_rem_latency,
    _SLEEP_METRIC_SLEEP_SCORE: _compute_sleep_score,
    _SLEEP_METRIC_AWAKE_COUNT: _compute_awake_count,
    _SLEEP_METRIC_N1_COUNT: _compute_n1_count,
    _SLEEP_METRIC_N2_COUNT: _compute_n2_count,
    _SLEEP_METRIC_N3_COUNT: _compute_n3_count,
    _SLEEP_METRIC_REM_COUNT: _compute_rem_count,
    _SLEEP_METRIC_BEDTIME: _compute_bedtime,
    _SLEEP_METRIC_WAKEUP_TIME: _compute_wakeup_time,
    _SLEEP_METRIC_MIDPOINT: _compute_sleep_midpoint,
    _SLEEP_METRIC_CPD_MIDPOINT: _compute_cpd_midpoint,
    _SLEEP_METRIC_CPD_DURATION: _compute_cpd_duration,
}


def get_sleep_statistic(
    loader: BaseLoader,
    user_id: Union[str, list],
    metric: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    **kwargs,
) -> dict:
    """Get sleep statistic from sleep data.

    This function is used by several functions of the module to get a single
    sleep statistic starting from sleep data.
    If multiple statistics are required, then it is more efficient to
    use the :func:`get_sleep_statistics` function that computes all the
    statistics by loading only once sleep data. The following statistics
    can be computed:

        - Time in Bed (``metric="TIB"``)
        - Total Sleep Time (``metric="TST"``)
        - Wake After Sleep Onset (``metric="WASO"``)
        - Sleep Onset Latency (``metric="SOL"``)
        - Sleep Period Time (``metric="SPT"``)
        - N1 Sleep Duration (``metric="N1"``)
        - N2 Sleep Duration (``metric="N2"``)
        - N3 Sleep Duration (``metric="N3"``)
        - REM Sleep Duration (``metric="REM"``)
        - NREM Sleep Duration (``metric="NREM"``)
        - Awake Duration (``metric="AWAKE"``)
        - Unmeasurable Sleep Duration (``metric="UNMEASURABLE"``)
        - N1 Sleep Latency (``metric="Lat_N1"``)
        - N2 Sleep Latency (``metric="Lat_N2"``)
        - N3 Sleep Latency (``metric="Lat_N3"``)
        - REM Sleep Latency (``metric="Lat_REM"``)
        - N1 Sleep Percentage (``metric="%N1"``)
        - N2 Sleep Percentage (``metric="%N2"``)
        - N3 Sleep Percentage (``metric="%N3"``)
        - Sleep Efficiency (``metric="SE"``)
        - Sleep Maintenance Efficiency (``metric="SME"``)
        - Sleep Score (``metric="SCORE"``)
        - Number of Awakenings (``metric="Awakenings"``)

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`
        The id(s) for which the sleep statistic must be computed.
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to perform a transform of the sleep statistic over days, by default None.
        If `None`, then the sleep statistic is returned with a value for each day, otherwise
        a transformation is applied. Valid options are:

            - 'mean'
            - 'min'
            - 'max'
            - 'std'

    Returns
    -------
    dict
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and sleep statistic as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with the
        name of the sleep statistic as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    data_dict = {}
    if not (kind is None):
        transformed_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        # Load sleep summary data
        sleep_summary = loader.load_sleep_summary(
            user, start_date, end_date, same_day_filter=True
        )
        if len(sleep_summary) > 0:
            sleep_summary = sleep_summary.set_index(
                constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL
            )
            # Get sleep stages from first to last date of sleep summary
            sleep_summary_start_date = sleep_summary.iloc[0][
                constants._ISODATE_COL
            ].to_pydatetime()
            sleep_summary_end_date = (
                sleep_summary.iloc[-1][constants._ISODATE_COL]
                + datetime.timedelta(
                    milliseconds=int(
                        sleep_summary.iloc[-1][
                            constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL
                        ]
                        + sleep_summary.iloc[-1][
                            constants._SLEEP_SUMMARY_DURATION_IN_MS_COL
                        ]
                    )
                )
            ).to_pydatetime()
            sleep_stages = loader.load_sleep_stage(
                user, sleep_summary_start_date, sleep_summary_end_date
            )

            # Keep only those belonging to sleep summaries
            sleep_stages = sleep_stages[
                sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
                    sleep_summary.index.unique()
                )
            ]
            # Compute metric -> pd.Series with sleepSummaryId as index
            metric_data = pd.DataFrame(
                _SLEEP_STATISTICS_DICT[metric](
                    sleep_summary=sleep_summary,
                    sleep_stages=sleep_stages,
                    chronotype=None
                    if "chronotype_dict" not in kwargs
                    else kwargs["chronotype_dict"].get(user, None),
                ).rename(metric)
            )
            metric_data = pd.merge(
                left=sleep_summary.loc[
                    :,
                    [
                        constants._CALENDAR_DATE_COL,
                    ],
                ],
                right=metric_data,
                left_index=True,
                right_index=True,
                how="outer",
            )
            # Convert it to a pd.Series with calendarDate as index
            # special handling in this step for timestamp metrics
            if metric in _SLEEP_DATETIME_METRICS:
                data_dict[user] = dict(zip(metric_data[constants._CALENDAR_DATE_COL], 
                         metric_data[metric].dt.to_pydatetime()))
            else:
                data_dict[user] = pd.Series(
                    metric_data[metric].values,
                    index=metric_data[constants._CALENDAR_DATE_COL],
                ).to_dict()

            if not (kind is None):
                if metric in _SLEEP_DATETIME_METRICS: # circular means are calculated on HH:MM format
                    data_dict[user] = {date: time.strftime("%H:%M") for date,time in data_dict[user].items()}
                sleep_data_df = pd.DataFrame.from_dict(data_dict[user], orient="index")
                transformed_dict[user] = {}
                if len(sleep_data_df[~sleep_data_df[0].isna()]) > 0:
                    kind_dict = _SLEEP_KIND_MAPPING.get(kind, None)
                    if kind_dict is None: # if the kind function is not among the common ones
                        kind_fn = kind # assume it's something that can be directly applied to metric
                    else: # otherwise get the specific version for the metric
                        kind_fn = kind_dict[metric if metric in _SLEEP_DATETIME_METRICS else "default"]
                    transformed_dict[user][metric] = kind_fn(
                            np.array(list(data_dict[user].values()))
                    )
                else:
                    transformed_dict[user][metric] = np.nan
                # report the days over which kind has been calculated
                transformed_dict[user]["days"] = [
                    datetime.datetime.strftime(x, "%Y-%m-%d")
                    for x in sleep_data_df.index
                ]

    if not (kind is None):
        return transformed_dict
    else:
        return data_dict


def get_sleep_statistics(
    loader: BaseLoader,
    user_id: Union[str, list],
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    **kwargs,
) -> dict:
    """Get sleep statistics from sleep data.

    This function is used by all the functions to get all the
    statistics from sleep data. It is more efficient than
    :func:`get_sleep_statistic` when multiple
    statistics are needed as it retrieves sleep data
    only once to compute all the statistics:

    Example::

        pywearable.sleep.get_sleep_statistics(loader, user_id, start_date, end_date, kind=None)

        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        datetime.date(2023, 9, 9):
                            {
                                'TIB': 501.0,
                                'SPT': 501.0,
                                'WASO': 4.0,
                                'TST': 497.0,
                                'N1': 280.0,
                                'N2': nan,
                                'N3': 53.0,
                                'REM': 164.0,
                                'NREM': 333.0,
                                'Lat_N1': 0.0,
                                'Lat_N2': nan,
                                'Lat_N3': 6.0,
                                'Lat_REM': 47.0,
                                '%N1': 56.33802816901409,
                                '%N2': nan,
                                '%N3': 10.663983903420524,
                                '%REM': 32.99798792756539,
                                '%NREM': 67.0020120724346,
                                'SE': 99.20159680638723,
                                'SME': 99.20159680638723
                            },
                        datetime.date(2023, 9, 10):
                            {
                                ...
                            }
                    }
            }

        pywearable.sleep.get_sleep_statistics(loader, user_id, start_date, end_date, kind='mean')
        >>  {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'values':
                            {
                                'TIB': 470.7142857142857,
                                'SPT': 470.7142857142857,
                                'WASO': 3.0,
                                'TST': 468.57142857142856,
                                'N1': 291.85714285714283,
                                'N2': nan,
                                'N3': 69.28571428571429,
                                'REM': 107.42857142857143,
                                'NREM': 361.14285714285717,
                                'Lat_N1': 0.0,
                                'Lat_N2': nan,
                                'Lat_N3': 15.714285714285714,
                                'Lat_REM': 91.28571428571429,
                                '%N1': 62.58569976756753,
                                '%N2': nan,
                                '%N3': 14.703552998168902,
                                '%REM': 22.710747234263554,
                                '%NREM': 77.28925276573644,
                                'SE': 99.56948758969357,
                                'SME': 99.56948758969357
                            },
                        'days':
                            [
                                datetime.date(2023, 9, 9),
                                datetime.date(2023, 9, 10),
                                datetime.date(2023, 9, 11),
                                datetime.date(2023, 9, 12),
                                datetime.date(2023, 9, 13),
                                datetime.date(2023, 9, 14),
                                datetime.date(2023, 9, 15)
                            ]
                    }
        }

    Parameters
    ----------
    loader : :class:`pywearable.loader.base.BaseLoader()`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`
        The id(s) for which the sleep statistic must be computed.
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    kind : :class:`str` or None, optional
        Whether to perform a transform of the sleep statistic over days, by default None.
        If `None`, then the sleep statistic is returned with a value for each day, otherwise
        a transformation is applied. Valid options are:

            - 'mean'
            - 'min'
            - 'max'
            - 'std'

    Returns
    -------
    dict
        If ``kind==None``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and sleep statistic key:value pairs.
        If ``kind`` is not ``None``, dictionary with ``user_id`` as key, and a nested dictionary with
        ``values`` as key of another nested dictionary with key:value pairs for each sleep statistic,
        and a ``days`` key that contains an array of all calendar days over which the transformation was computed.
    """
    data_dict = {}
    if not (kind is None):
        transformed_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        # Load sleep summary data
        sleep_summary = loader.load_sleep_summary(user, start_date, end_date)
        if len(sleep_summary) > 0:
            sleep_summary = sleep_summary.set_index(
                constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL
            )

            # Drop duplicates of calendar date and keep longest ones
            sleep_summary = sleep_summary.sort_values(
                by=[
                    constants._CALENDAR_DATE_COL,
                    constants._SLEEP_SUMMARY_DURATION_IN_MS_COL,
                ]
            )

            sleep_summary = sleep_summary.drop_duplicates(
                constants._CALENDAR_DATE_COL, keep="last"
            )
            sleep_summary_start_date = sleep_summary.iloc[0][
                constants._ISODATE_COL
            ].to_pydatetime()
            sleep_summary_end_date = (
                sleep_summary.iloc[-1]["isoDate"]
                + datetime.timedelta(
                    milliseconds=int(
                        sleep_summary.iloc[-1][
                            constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL
                        ]
                        + sleep_summary.iloc[-1][
                            constants._SLEEP_SUMMARY_DURATION_IN_MS_COL
                        ]
                    )
                )
            ).to_pydatetime()
            sleep_stages = loader.load_sleep_stage(
                user, sleep_summary_start_date, sleep_summary_end_date
            )
            # Keep only those belonging to sleep summaries
            sleep_stages = sleep_stages[
                sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
                    sleep_summary.index
                )
            ]
            for sleep_metric in _SLEEP_STATISTICS_DICT.keys():
                sleep_summary[sleep_metric] = _SLEEP_STATISTICS_DICT[sleep_metric](
                    sleep_summary=sleep_summary,
                    sleep_stages=sleep_stages,
                    chronotype=None
                    if "chronotype_dict" not in kwargs
                    else kwargs["chronotype_dict"].get(user, None),
                )
            user_sleep_metrics_df = sleep_summary.set_index(
                sleep_summary[constants._CALENDAR_DATE_COL]
            ).loc[
                :,
                [k for k in _SLEEP_STATISTICS_DICT.keys()],
            ]
            data_dict[user] = user_sleep_metrics_df.to_dict("index")

            if not (kind is None):
                transformed_dict[user] = {}
                transformed_dict[user]["values"] = user_sleep_metrics_df.apply(
                    kind
                ).to_dict()
                transformed_dict[user]["days"] = [
                    x for x in user_sleep_metrics_df.index
                ]

    if not (kind is None):
        return transformed_dict
    else:
        return data_dict
