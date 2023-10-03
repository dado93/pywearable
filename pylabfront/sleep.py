"""
This module contains all the functions related to analysis
of sleep data.
"""

import datetime
from collections import OrderedDict
from typing import Union

import numpy as np
import pandas as pd

from . import constants, loader, utils

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
_SLEEP_METRIC_LATENCY_SOL = "SOL"
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


def get_time_in_bed(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get time in bed (TIB) sleep metric.

    This function computes time in bed (TIB) metric as the total duration
    of the sleep, given by the sum of all sleep stages and unmeasurable sleep
    as well. The value is reported in minutes.

    .. math:: TIB = N1 + N2 + N3 + REM + UNMEASURABLE + AWAKE

    Depending on the value of the ``average`` parameter, this function
    returns TIB for each calendar day (``average=False``) from ``start_date`` to
    ``end_date`` or the average value across all days (``average=True``).

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_time_in_bed(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 501.0,
            datetime.date(2023, 9, 10): 514.0,
            datetime.date(2023, 9, 11): 455.0,
            datetime.date(2023, 9, 12): 437.0,
            datetime.date(2023, 9, 13): 437.0,
            datetime.date(2023, 9, 14): 402.0,
            datetime.date(2023, 9, 15): 469.0}

        pylabfront.sleep.get_time_in_bed(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which TIB must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average TIB over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and time in bed as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `TIB`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_TIB, start_date, end_date, average
    )


def get_sleep_period_time(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> pd.DataFrame:
    """Get sleep period time (SPT) sleep metric.

    This function computes sleep period time (SPT) metric as the duration from the first to
    the last period of sleep. Depending on the value of the `average` parameter, this function
    returns SPT for each calendar day (``average=False``) from ``start_date`` to
    ``end_date`` or the average value across all days (``average=True``).

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_sleep_period_time(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 501.0,
            datetime.date(2023, 9, 10): 514.0,
            datetime.date(2023, 9, 11): 455.0,
            datetime.date(2023, 9, 12): 437.0,
            datetime.date(2023, 9, 13): 437.0,
            datetime.date(2023, 9, 14): 402.0,
            datetime.date(2023, 9, 15): 496.0}

        pylabfront.sleep.get_sleep_period_time(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which SPT must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average SPT over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and sleep period time as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `SPT`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_SPT, start_date, end_date, average
    )


def get_total_sleep_time(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> pd.DataFrame:
    """Get total sleep time (TST) sleep metric.

    This function computes total sleep time (TST) metric as the total duration of
    N1, N2, N3, and REM in SPT (see :func:`get_sleep_period_time`).
    Depending on the value of the `average` parameter, this function
    returns TST for each calendar day (``average=False``) from ``start_date`` to
    ``end_date`` or the average value across all days (``average=True``).

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_total_sleep_time(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 497.0,
            datetime.date(2023, 9, 10): 512.0,
            datetime.date(2023, 9, 11): 455.0,
            datetime.date(2023, 9, 12): 435.0,
            datetime.date(2023, 9, 13): 435.0,
            datetime.date(2023, 9, 14): 402.0,
            datetime.date(2023, 9, 15): 494.0}

        pylabfront.sleep.get_total_sleep_time(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which TST must be retrieved, by default "all".
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average TST over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and total sleep time as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `TST`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_TST, start_date, end_date, average
    )


def get_sleep_efficiency(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> pd.DataFrame:
    """Get sleep efficiency (SE) sleep metric.

    This function computes sleep efficiency (SE) metric as the ratio
    between TST (see :func:`get_total_sleep_time`) and TIB (see :func:`get_time_in_bed`).
    .. math:: SE = TST / TIB
    Depending on the value of the ``average`` parameter, this function
    returns SE for each calendar day (``average=False``) from ``start_date`` to
    ``end_date`` or the average value across all days (``average=True``).

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_sleep_efficiency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 99.20159680638723,
            datetime.date(2023, 9, 10): 99.61089494163424,
            datetime.date(2023, 9, 11): 100.0,
            datetime.date(2023, 9, 12): 99.54233409610984,
            datetime.date(2023, 9, 13): 99.54233409610984,
            datetime.date(2023, 9, 14): 100.0,
            datetime.date(2023, 9, 15): 99.59677419354838}

        pylabfront.sleep.get_sleep_efficiency(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which SE must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average SE over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and sleep efficiency as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `SE`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_SE, start_date, end_date, average
    )


def get_sleep_maintenance_efficiency(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> pd.DataFrame:
    """Get sleep maintenance efficiency (SME) sleep metric.

    This function computes sleep maintenance efficiency (SME) metric as the ratio
    between TST (see :func:`get_total_sleep_time`) and SPT (see :func:`get_sleep_period_time`).

    .. math:: SME = \\frac{TST}{SPT}

    Depending on the value of the `average` parameter, this function
    returns SME for each calendar day (`average=False`) from `start_date` to
    `end_date` or the average value across all days (`average=True`).

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_sleep_maintenance_efficiency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 99.20159680638723,
            datetime.date(2023, 9, 10): 99.61089494163424,
            datetime.date(2023, 9, 11): 100.0,
            datetime.date(2023, 9, 12): 99.54233409610984,
            datetime.date(2023, 9, 13): 99.54233409610984,
            datetime.date(2023, 9, 14): 100.0,
            datetime.date(2023, 9, 15): 99.59677419354838}

        pylabfront.sleep.get_sleep_maintenance_efficiency(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which SME must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average SME over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and sleep maintenance efficiency as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `SME`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_SME, start_date, end_date, average
    )


def get_n1_latency(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get N1 sleep latency.

    This function computes the latency to the first stage of N1 sleep.
    Depending on the value of the `average` parameter, this function
    returns N1 sleep latency for each calendar day (`average=False`) from `start_date` to
    `end_date` or the average value across all days (`average=True`).
    Latency is reported in minutes.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_n1_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 0.0,
            datetime.date(2023, 9, 10): 0.0,
            datetime.date(2023, 9, 11): 0.0,
            datetime.date(2023, 9, 12): 0.0,
            datetime.date(2023, 9, 13): 0.0,
            datetime.date(2023, 9, 14): 0.0,
            datetime.date(2023, 9, 15): 0.0}

        pylabfront.sleep.get_n1_latency(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which N1 sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average N1 sleep latency over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and N1 sleep latency as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_N1`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N1_LATENCY, start_date, end_date, average
    )


def get_n2_latency(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    """Get N2 sleep latency.

    This function computes the latency to the first stage of N2 sleep.
    Depending on the value of the `average` parameter, this function
    returns N2 sleep latency for each calendar day (`average=False`) from `start_date` to
    `end_date` or the average value across all days (`average=True`).
    Latency is reported in minutes.
    Beware that, if Garmin data are used, N2 sleep latency will always be equal
    to nan as Garmin does not report N2 sleep stages.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_n2_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 0.0,
            datetime.date(2023, 9, 10): 0.0,
            datetime.date(2023, 9, 11): 0.0,
            datetime.date(2023, 9, 12): 0.0,
            datetime.date(2023, 9, 13): 0.0,
            datetime.date(2023, 9, 14): 0.0,
            datetime.date(2023, 9, 15): 0.0}

        pylabfront.sleep.get_n2_latency(loader, user_id, start_date, end_date, average=True)
        >> {
                'f457c562-2159-431c-8866-dfa9a917d9b8':
                    {
                        'Lat_N2': 0.0,
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
    loader : :class:`loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which N2 sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average N2 sleep latency over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and N2 sleep latency as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_N2`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N2_LATENCY, start_date, end_date, average
    )


def get_n3_latency(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get N3 sleep latency.

    This function computes the latency to the first stage of N3 sleep.
    Depending on the value of the `average` parameter, this function
    returns N3 sleep latency for each calendar day (`average=False`) from `start_date` to
    `end_date` or the average value across all days (`average=True`).

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_n3_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 6.0,
            datetime.date(2023, 9, 10): 20.0,
            datetime.date(2023, 9, 11): 32.0,
            datetime.date(2023, 9, 12): 16.0,
            datetime.date(2023, 9, 13): 9.0,
            datetime.date(2023, 9, 14): 19.0,
            datetime.date(2023, 9, 15): 15.0}

        pylabfront.sleep.get_n3_latency(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which N3 sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average N3 sleep latency over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and N3 sleep latency as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_N3`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N3_LATENCY, start_date, end_date, average
    )


def get_rem_latency(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get REM sleep latency.

    This function computes the latency to the first stage of REM sleep.
    Depending on the value of the `average` parameter, this function
    returns REM sleep latency for each calendar day (`average=False`) from `start_date` to
    `end_date` or the average value across all days (`average=True`).

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_rem_latency(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 47.0,
            datetime.date(2023, 9, 10): 119.0,
            datetime.date(2023, 9, 11): 69.0,
            datetime.date(2023, 9, 12): 57.0,
            datetime.date(2023, 9, 13): 79.0,
            datetime.date(2023, 9, 14): 167.0,
            datetime.date(2023, 9, 15): 52.0}

        pylabfront.sleep.get_rem_latency(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`, optional
        The id(s) for which REM sleep latency must be retrieved, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average REM sleep latency over days, or to return the value for each day, by default False

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and REM sleep latency as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `Lat_REM`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_REM_LATENCY, start_date, end_date, average
    )


def get_n1_duration(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get N1 sleep duration.

    This function returns the absolute time spent in N1 sleep stage for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns N1 sleep time for each night (``average=False``),
    or the average N1 sleep time from ``start_date`` to ``end_date`` (``average=True``).
    Duration is reported in minutes.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_n1_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 280.0,
            datetime.date(2023, 9, 10): 256.0,
            datetime.date(2023, 9, 11): 333.0,
            datetime.date(2023, 9, 12): 312.0,
            datetime.date(2023, 9, 13): 288.0,
            datetime.date(2023, 9, 14): 233.0,
            datetime.date(2023, 9, 15): 295.0}

        pylabfront.sleep.get_n1_duration(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        Initialized instance of :class:`loader.LabfrontLoader`, required in order to properly load data.
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
    average : :class:`bool`, optional
        Average N1 sleep across nights, by default False. If set to ``True``, then
        the average N1 sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        N1 sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and N1 sleep duration as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `N1`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N1_DURATION, start_date, end_date, average
    )


def get_n2_duration(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get N2 sleep duration.

    This function returns the absolute time spent in N2 sleep stage for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns N2 sleep time for each night (``average=False``),
    or the average N2 sleep time from ``start_date`` to ``end_date`` (``average=True``).
    Duration is reported in minutes.
    Beware that if Garmin data are used, then N2 sleep duration will always be equal to
    nan as Garmin does not detect N2 sleep stages.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_n2_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): nan,
            datetime.date(2023, 9, 10): nan,
            datetime.date(2023, 9, 11): nan,
            datetime.date(2023, 9, 12): nan,
            datetime.date(2023, 9, 13): nan,
            datetime.date(2023, 9, 14): nan,
            datetime.date(2023, 9, 15): nan}

        pylabfront.sleep.get_n2_duration(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        Initialized instance of :class:`loader.LabfrontLoader`, required in order to properly load data.
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
    average : :class:`bool`, optional
        Average N2 sleep across nights, by default False. If set to ``True``, then
        the average N2 sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        N1 sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and N2 sleep duration as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `N2`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N2_DURATION, start_date, end_date, average
    )


def get_n3_duration(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get N3 sleep duration.

    This function returns the absolute time spent in N3 sleep stage for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns N3 sleep time for each night (``average=False``),
    or the average N3 sleep time from ``start_date`` to ``end_date`` (``average=True``).
    Duration is reported in minutes.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_n3_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 53.0,
            datetime.date(2023, 9, 10): 112.0,
            datetime.date(2023, 9, 11): 37.0,
            datetime.date(2023, 9, 12): 49.0,
            datetime.date(2023, 9, 13): 66.0,
            datetime.date(2023, 9, 14): 76.0,
            datetime.date(2023, 9, 15): 83.0}

        pylabfront.sleep.get_n3_duration(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        Initialized instance of :class:`loader.LabfrontLoader`, required in order to properly load data.
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
    average : :class:`bool`, optional
        Average N3 sleep across nights, by default False. If set to ``True``, then
        the average N3 sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        N1 sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and N3 sleep duration as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `N3`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N3_DURATION, start_date, end_date, average
    )


def get_rem_duration(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get REM sleep duration.

    This function returns the absolute time spent in REM sleep stage for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns REM sleep time for each night (``average=False``),
    or the average REM sleep time from ``start_date`` to ``end_date`` (``average=True``).
    Duration is reported in minutes.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_rem_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 164.0,
            datetime.date(2023, 9, 10): 144.0,
            datetime.date(2023, 9, 11): 85.0,
            datetime.date(2023, 9, 12): 74.0,
            datetime.date(2023, 9, 13): 81.0,
            datetime.date(2023, 9, 14): 93.0,
            datetime.date(2023, 9, 15): 116.0}

        pylabfront.sleep.get_rem_duration(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        Initialized instance of :class:`loader.LabfrontLoader`, required in order to properly load data.
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
    average : :class:`bool`, optional
        Average REM sleep across nights, by default False. If set to ``True``, then
        the average REM sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        N1 sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and REM sleep duration as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `REM`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_REM_DURATION, start_date, end_date, average
    )


def get_nrem_duration(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get NREM sleep duration.

    This function returns the absolute time spent in NREM sleep stage for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns NREM sleep time for each night (``average=False``),
    or the average NREM sleep time from ``start_date`` to ``end_date`` (``average=True``).
    Duration is reported in minutes.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_nrem_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 333.0,
            datetime.date(2023, 9, 10): 368.0,
            datetime.date(2023, 9, 11): 370.0,
            datetime.date(2023, 9, 12): 361.0,
            datetime.date(2023, 9, 13): 354.0,
            datetime.date(2023, 9, 14): 309.0,
            datetime.date(2023, 9, 15): 433.0}

        pylabfront.sleep.get_nrem_duration(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        Initialized instance of :class:`loader.LabfrontLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which NREM sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    average : :class:`bool`, optional
        Average NREM sleep across nights, by default False. If set to ``True``, then
        the average NREM sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        N1 sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and NREM sleep duration as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `NREM`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_NREM_DURATION, start_date, end_date, average
    )


def get_awake_duration(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get awake sleep duration.

    This function returns the absolute time spent in awake stage for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns awake time for each night (``average=False``),
    or the average awake time from ``start_date`` to ``end_date`` (``average=True``).
    Duration is reported in minutes.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_awake_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 4.0,
            datetime.date(2023, 9, 10): 2.0,
            datetime.date(2023, 9, 11): 0.0,
            datetime.date(2023, 9, 12): 2.0,
            datetime.date(2023, 9, 13): 2.0,
            datetime.date(2023, 9, 14): 0.0,
            datetime.date(2023, 9, 15): 5.0}

        pylabfront.sleep.get_awake_duration(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        Initialized instance of :class:`loader.LabfrontLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which awake data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    average : :class:`bool`, optional
        Average awake time across nights, by default False. If set to ``True``, then
        the average awake time sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        awake time for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and awake duration as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `AWAKE`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_AWAKE_DURATION, start_date, end_date, average
    )


def get_unmeasurable_duration(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get unmeasurable sleep duration.

    This function returns the absolute time spent in unmeasurable sleep stage for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns unmeasurable sleep time for each night (``average=False``),
    or the average unmeasurable sleep time from ``start_date`` to ``end_date`` (``average=True``).
    Duration is reported in minutes.

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_unmeasurable_duration(loader, user_id, start_date, end_date)

        >> {'f457c562-2159-431c-8866-dfa9a917d9b8':
            datetime.date(2023, 9, 9): 0.0,
            datetime.date(2023, 9, 10): 0.0,
            datetime.date(2023, 9, 11): 0.0,
            datetime.date(2023, 9, 12): 0.0,
            datetime.date(2023, 9, 13): 0.0,
            datetime.date(2023, 9, 14): 0.0,
            datetime.date(2023, 9, 15): 0.0}

        pylabfront.sleep.get_unmeasurable_duration(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`loader.LabfrontLoader`
        Initialized instance of :class:`loader.LabfrontLoader`, required in order to properly load data.
    user_id : :class:`str` or :class:`list`, optional
        IDs of the users for which unmeasurable sleep data have to be extracted, by default "all"
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    average : :class:`bool`, optional
        Average NREM sleep across nights, by default False. If set to ``True``, then
        the average NREM sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        N1 sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and unmeasurable sleep duration as values.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with `UNMEASURABLE`
        as key and its value, and an additional `days` keys that contains an array of all
        calendar days over which the average was computed.
    """
    return get_sleep_statistic(
        loader,
        user_id,
        _SLEEP_METRIC_UNMEASURABLE_DURATION,
        start_date,
        end_date,
        average,
    )


def get_n1_percentage(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N1_PERCENTAGE, start_date, end_date, average
    )


def get_n2_percentage(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N2_PERCENTAGE, start_date, end_date, average
    )


def get_n3_percentage(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_N3_PERCENTAGE, start_date, end_date, average
    )


def get_rem_percentage(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_REM_PERCENTAGE, start_date, end_date, average
    )


def get_nrem_percentage(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_NREM_PERCENTAGE, start_date, end_date, average
    )


def get_wake_after_sleep_onset(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_WASO, start_date, end_date, average
    )


def get_sleep_score(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
):
    return get_sleep_statistic(
        loader, user_id, _SLEEP_METRIC_SLEEP_SCORE, start_date, end_date, average
    )


def get_sleep_timestamps(
    loader: loader.LabfrontLoader,
    user_id : Union[str, list] = "all",
    start_date : Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average : bool = False,
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
    average : :class:`bool`, optional
        Whether to calculate the average sleep and awake time of the user, by default False.

    Returns
    -------
    :class:`dict`
        Dictionary with user ids as primary keys, if average is False then dates as secondary keys
        and sleep timestamps as values, otherwise (average starting time, average ending time) as values
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        # better to give a bit of rooms before and after start_date and end_date to ensure they're included
        df = loader.load_garmin_connect_sleep_summary(user, start_date, end_date)
        if len(df) > 0:
            df = df.groupby(constants._SLEEP_SUMMARY_CALENDAR_DATE_COL).head(1)
            df["waking_time"] = df[constants._ISODATE_COL] + df[
                constants._SLEEP_SUMMARY_DURATION_IN_MS_COL
            ].astype(int).apply(lambda x: datetime.timedelta(milliseconds=x))
            data_dict[user] = pd.Series(
                zip(
                    df[constants._ISODATE_COL].dt.to_pydatetime(),
                    df["waking_time"].dt.to_pydatetime(),
                ),
                df[constants._SLEEP_SUMMARY_CALENDAR_DATE_COL],
            ).to_dict()
            if average:
                sleep_times = [timestamp[0] for timestamp in data_dict[user].values()]
                wake_times = [timestamp[1] for timestamp in data_dict[user].values()]
                sleep_times = [item.strftime("%H:%M") for item in sleep_times]
                wake_times = [item.strftime("%H:%M") for item in wake_times]
                mean_sleep_time = utils.mean_time(sleep_times)
                mean_wake_time = utils.mean_time(wake_times)
                data_dict[user] = (mean_sleep_time, mean_wake_time)
        else:
            data_dict[user] = None

    return data_dict


def get_sleep_midpoints(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
    return_days: bool = False,
):
    """Get the midpoints of sleeping occurrences

    Returns for every night in the period of interest the midpoint of the
    sleeping process.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user_id : :class:`str`, optional
        ID of the user for which sleep midpoints are computed, by default "all".
    start_date : :class:`datetime.datetime`, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime`, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to return the average midpoint for the user (in hours, from midnight), by default False
    return_days : :class:`bool`, optional
        Whether to show the days used for the computation of the average, by default False

    Returns
    -------
    :class:`dict`
        Dictionary with user ids as primary keys, if average is False then dates as secondary keys
        and sleep timestamps as values, otherwise the average for that user
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        sleep_timestamps = get_sleep_timestamps(loader, 
                                                user_id = user,
                                                start_date = start_date,
                                                end_date = end_date)[
            user
        ]
        if sleep_timestamps is None:
            data_dict[user] = None
        else:
            data_dict[user] = OrderedDict()
            for k, v in sleep_timestamps.items():
                daily_start_hour = v[0]
                daily_end_hour = v[1]
                midpoint = daily_start_hour + (daily_end_hour - daily_start_hour) / 2
                data_dict[user][k] = midpoint
            if average:
                days = list(data_dict[user].keys())
                midpoints = [v for v in data_dict[user].values()]
                midpoints = [midpoint.strftime("%H:%M") for midpoint in midpoints]
                mean_midpoint = utils.mean_time(midpoints)
                data_dict[user] = {}
                if return_days:
                    data_dict[user]["average_midpoint"] = mean_midpoint
                    data_dict[user]["days"] = days
                else:
                    data_dict[user] = mean_midpoint

    return data_dict


def get_awakenings(
    loader : loader.LabfrontLoader, 
    user_id : Union[str, list] = "all",
    start_date : Union[datetime.datetime, datetime.date, str, None] = None, 
    end_date : Union[datetime.datetime, datetime.date, str, None] = None, 
    average : bool = False
):
    """Get the number of awakenings

    Returns the number of times the user(s) of interest woke up during the night.
    This is checked considering the hypnogram and checking variations in sleep stages
    and awake status detection. If ``average`` is set to True, the average number of
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

    user_id = utils.get_user_ids(loader, user_id)

    data_dict = {}
    if average:
        average_dict = {}

    for user in user_id:
        data_dict[user] = {}
        if average:
            average_dict[user] = {}
        try:
            df = loader.load_garmin_connect_sleep_summary(user, start_date, end_date)
            nights_available = df[constants._SLEEP_SUMMARY_CALENDAR_DATE_COL]
            for night in nights_available:
                hypnogram = loader.load_hypnogram(
                    user, night, night
                )[night]["values"]

                # TODO do we need hyonogram? Can't we use sleep stages?
                
                # check if there a difference in stage between successive observations (first one defaults to no change)
                stages_diff = np.concatenate(
                    [
                        [0],
                        hypnogram[1:]
                        - hypnogram[:-1]
                    ]
                )
                # if there has been a negative change and the current stage is awake, then count it as awakening
                num_awakenings = np.logical_and(
                    hypnogram == 0, stages_diff < 0
                ).sum()
                data_dict[user][night] = num_awakenings
            if average:
                average_dict[user]["AWAKENINGS"] = np.nanmean(list(data_dict[user].values()))
                average_dict[user]["days"] = [
                    datetime.datetime.strftime(night, "%Y-%m-%d")
                    for night in nights_available
                ]
        except:
            data_dict[user] = None

    if average:
        return average_dict
    return data_dict


def get_cpd(
    loader : loader.LabfrontLoader,
    user : Union[str, None] = None,
    start_date : Union[datetime.datetime, datetime.date, str, None] = None,
    end_date : Union[datetime.datetime, datetime.date, str, None] = None,
    sleep_metric : str = "midpoint",
    chronotype_sleep_start : str = "00:00",
    chronotype_sleep_end : str = "08:00",
    days_to_consider : int = 28,
    verbose : bool = False,
    average : bool = True,
):
    """Computes composite phase deviation (CPD)

    Returns a measure of sleep regularity, either in terms of stability of rest midpoints
    if `sleep_metric` is 'midpoint', or in terms of duration is `sleep_metric` is 'duration'.
    The measure is computed for the period between `start_date` and `end_date`
    but only keeping in consideration the most recent `days_to_consider`.
    Note that this function, since it requires a specific chronotype for a person,
    is only computed for a specific user, it can't consider multiple users at the same time.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    user : :class:`str`, optional
        ID of the user for which CPD is computed, by default None.
    start_date : :class:`datetime.datetime`, optional
        Start date from which to compute CPD, by default None.
    end_date : :class:`datetime.datetime`, optional
        End date until which to compute CPD, by default None.
    sleep_metric : :class:`str`, optional
        the metric for the computation of CPD, can be either "midpoint" or "duration", by default "midpoint"
    chronotype_sleep_start : :class:`str`, optional
        the hour of reference at which the user begins to sleep in format HH:MM, by default "00:00"
    chronotype_sleep_end : :class:`str`, optional
        the hour of reference at which the user wakes up in format HH:MM, by default "08:00"
    days_to_consider : :class:`int`, optional
        the maximum number of days to consider in the period of interest, by default 28
    verbose : :class:`str`, optional
        whether to show daily cpd components
    average : :class:`bool`, optional
        whether to return the CPD or the single day CPD components

    Returns
    -------
    :class:`float`
        CPD metric, indicating sleep regularity of the user

    Raises
    -------
    ValueError

    `user` isn't specified.
    """

    if user is None:
        raise ValueError("Specify a user")
    
    user = loader.get_full_id(user)

    if sleep_metric == "midpoint":
        # define what is the expected midpoint based on the chronotype
        chronotype_sleep_midpoint = utils.mean_time(
            [chronotype_sleep_start, chronotype_sleep_end]
        )
        sleep_midpoints = get_sleep_midpoints(loader,
                                             user_id = user,
                                             start_date = start_date,
                                             end_date = end_date)[user]

        previous_midpoint = None
        CPDs = []
        dates = []

        try:
            for calendar_date, midpoint in list(sleep_midpoints.items())[
                -days_to_consider:
            ]:
                # mistiming component
                chronotype_daily_midpoint = datetime.datetime(
                    calendar_date.year,
                    calendar_date.month,
                    calendar_date.day,
                    hour=int(chronotype_sleep_midpoint[:2]),
                    minute=int(chronotype_sleep_midpoint[3:]),
                )
                # if the expected midpoint is prior to midnight we need to adjust the day
                if 14 < int(chronotype_sleep_midpoint[:2]) < 24:
                    chronotype_daily_midpoint -= datetime.timedelta(days=1)

                mistiming_component = (
                    chronotype_daily_midpoint - midpoint
                ).total_seconds() / (60 * 60)

                # irregularity component
                if previous_midpoint is None:  # only for the first night recorded
                    irregularity_component = 0
                else:
                    previous_day_midpoint_proxy = datetime.datetime(
                        calendar_date.year,
                        calendar_date.month,
                        calendar_date.day,
                        hour=previous_midpoint.hour,
                        minute=previous_midpoint.minute,
                    )

                    if 14 < previous_day_midpoint_proxy.hour < 24:
                        previous_day_midpoint_proxy -= datetime.timedelta(days=1)

                    irregularity_component = (
                        previous_day_midpoint_proxy - midpoint
                    ).total_seconds() / (60 * 60)

                previous_midpoint = midpoint

                cpd = np.sqrt(mistiming_component**2 + irregularity_component**2)
                if verbose:
                    print(
                        f"Date: {calendar_date}. Mistiming component: {round(mistiming_component,2)}. Irregularity component {round(irregularity_component,2)}."
                    )
                CPDs.append(cpd)
                dates.append(calendar_date)
        except:
            return np.nan

    elif sleep_metric == "duration":
        chronotype_sleep_duration = (
            datetime.datetime.strptime(chronotype_sleep_end, "%H:%M")
            - datetime.datetime.strptime(chronotype_sleep_start, "%H:%M")
        ).total_seconds() / (60 * 60)
        if chronotype_sleep_duration < 0:  # takes care of sleep-time prior to midnight
            chronotype_sleep_duration += 24
        try:
            sleep_durations = get_total_sleep_time(loader, user, start_date, end_date)[
                user
            ]
        except:
            return np.nan

        CPDs = []
        dates = []
        previous_duration = None

        try:
            for calendar_date, daily_duration in list(sleep_durations.items())[
                -days_to_consider:
            ]:
                daily_duration = daily_duration / 60  # conversion in hours

                mistiming_component = chronotype_sleep_duration - daily_duration

                if previous_duration is None:
                    irregularity_component = 0
                else:
                    irregularity_component = previous_duration - daily_duration

                previous_duration = daily_duration

                cpd = np.sqrt(mistiming_component**2 + irregularity_component**2)
                if verbose:
                    print(
                        f"Date: {calendar_date}. Mistiming component: {round(mistiming_component,2)}. Irregularity component {round(irregularity_component,2)}."
                    )
                CPDs.append(cpd)
                dates.append(calendar_date)
        except:
            return np.nan

    else:
        raise KeyError("The sleep metric must be either 'midpoint' or 'duration'")

    if average:
        return np.mean(CPDs)
    else:
        return {dates[i]: CPDs[i] for i in range(len(dates))}


def get_sleep_metric_std(
    loader : loader.LabfrontLoader,
    metric : str,
    user_id : str, 
    start_date : Union[datetime.datetime, datetime.date, str, None] = None,
    end_date : Union[datetime.datetime, datetime.date, str, None] = None, 
):
    """Calculates standard deviation of a desired sleep metric

    Given a selected metric, calculates for the period of interest
    and user of interest, its standard deviation.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    metric : :class:`str`
        Name of the metric or name of the sleep function for which calculate std
    user_id : :class:`str`
        user id for the user of interest
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.

    Returns
    -------
    :class:`float`
        Standard deviation for the sleep metric of interest

    Raises
    -------
    ValueError
        `metric` must valid: support is only for "midpoint" or "duration" in the current version
    """
    if metric == "duration":  # in hours
        metric_data = get_sleep_period_time(loader, user_id, start_date, end_date)[user_id]
        metric_data = [duration / (1000 * 60 * 60) for duration in metric_data.values()]
    elif metric == "midpoint":  # in hours
        midpoints = list(
            get_sleep_midpoints(loader, 
                                user_id = user_id,
                                start_date = start_date, 
                                end_date = end_date)[user_id].values()
        )
        # need to check for possible midpoints before midnight
        metric_data = []
        for midpoint in midpoints:
            midpoint_pydt = midpoint.to_pydatetime()
            hour_component = midpoint_pydt.hour
            minute_component = midpoint_pydt.minute
            if hour_component > 13:
                hour_component -= 24
            metric_data.append(hour_component + minute_component / 60)
    else:
        try:
            metric_data = metric(loader, start_date, end_date, user_id)[user_id]
            metric_data = list(metric_data.values())
        except:
            raise ValueError(
                "Metric specified isn't valid"
            )  # TODO implement for other features as needed

    return np.nanstd(metric_data)


def _compute_sleep_score(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    if constants._SLEEP_SUMMARY_OVERALL_SLEEP_SCORE_COL in sleep_summary.columns:
        sleep_score = sleep_summary[constants._SLEEP_SUMMARY_OVERALL_SLEEP_SCORE_COL]
    else:
        sleep_score = pd.Series()
    return sleep_score


def _compute_time_in_bed(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
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


def _compute_total_sleep_time(sleep_summary: pd.DataFrame, *args) -> pd.Series:
    """Compute Total Sleep Time (TST) metric for sleep data.

    This function computes the TST as the total duration of the N1, N2, N3,
    and REM sleep stages.

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
        (
            constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
    ):
        tst = (
            sleep_summary[constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL]
        ) / (
            1000 * 60
        )  # convert from ms to seconds, and then to minutes
    else:
        tst = pd.Series()
    return tst


def _compute_sleep_efficiency(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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
    if (
        (
            constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL in sleep_summary.columns)
        and (constants._SLEEP_SUMMARY_DURATION_IN_MS_COL in sleep_summary.columns)
    ):
        tot_duration = (
            sleep_summary[constants._SLEEP_SUMMARY_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL]
        )
        sleep_duration = (
            sleep_summary[constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL]
        )
        se = (sleep_duration / tot_duration) * 100
    else:
        se = pd.Series()
    return se


def _compute_sleep_maintenance_efficiency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
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
    if (
        (
            constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (constants._SLEEP_SUMMARY_DURATION_IN_MS_COL in sleep_summary.columns)
    ):
        sleep_duration = (
            sleep_summary[constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL]
        ) / (1000 * 60)
        spt = _compute_sleep_period_time(sleep_summary, sleep_stages)
        se = (sleep_duration / spt) * 100
    else:
        se = pd.Series()
    return se


def _compute_sleep_stage_percentage(
    sleep_summary: pd.DataFrame, sleep_stage: str
) -> pd.Series:
    """Compute the percentage of time spent in a sleep stage.

    This function computes the percentage of time in a sleep stage
    as the ratio between the time spent in it and the sum of the
    time spent sleeping 

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
        (
            constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (
            constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL
            in sleep_summary.columns
        )
        and (constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL in sleep_summary.columns)
    ):
        tot_duration = (
            sleep_summary[constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL]
        )
        if sleep_stage == "NREM":
            perc = (
                (
                    tot_duration
                    - sleep_summary[
                        constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
                    ]
                )
                / tot_duration
                * 100
            )
        else:
            if sleep_stage == "N1":
                col = constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL
            elif sleep_stage == "N3":
                col = constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL
            elif sleep_stage == "REM":
                col = constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
            else:
                raise ValueError(
                    f"{sleep_stage} is not a valid value. Select among [N1, N3, REM, NREM]"
                )
            perc = (sleep_summary[col]) / tot_duration * 100
    else:
        perc = pd.Series()
    return perc


def _compute_n1_percentage(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_n2_percentage(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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
    return pd.Series(np.nan, sleep_summary.index)


def _compute_n3_percentage(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_rem_percentage(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_nrem_percentage(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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
    sleep_summary: pd.DataFrame, sleep_stage: str
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
        if `sleep_stage` isn't one of "N1","N3","REM","NREM","AWAKE","UNMEASURABLE".
    """
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    if sleep_stage == "NREM":
        tot_duration = (
            sleep_summary[constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL]
            + sleep_summary[constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL]
        )
        dur = (
            tot_duration
            - sleep_summary[constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL]
        ) / (1000 * 60)
    else:
        if sleep_stage == "N1":
            col = constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL
        elif sleep_stage == "N3":
            col = constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL
        elif sleep_stage == "REM":
            col = constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL
        elif sleep_stage == "AWAKE":
            col = constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL
        elif sleep_stage == "UNMEASURABLE":
            col = constants._SLEEP_SUMMARY_UNMEASURABLE_DURATION_IN_MS_COL
        else:
            raise ValueError(
                f"{sleep_stage} is not a valid value. Select among [N1, N3, REM, NREM, AWAKE, UNMEASURABLE]"
            )
        dur = (sleep_summary[col]) / (1000 * 60)
    return dur


def _compute_n1_duration(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_n2_duration(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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
    return pd.Series(np.nan, index=sleep_summary.index)


def _compute_n3_duration(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_rem_duration(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_nrem_duration(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_awake_duration(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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


def _compute_unmeasurable_duration(sleep_summary: pd.DataFrame, *args) -> pd.Series:
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
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
) -> pd.Series:
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    if not isinstance(sleep_stages, pd.DataFrame):
        raise ValueError(
            f"sleep_stages must be a pd.DataFrame. {type(sleep_stages)} is not a valid type."
        )

    def sleep_diff(group):
        start = group[constants._UNIXTIMESTAMP_IN_MS_COL]
        duration = group[constants._SLEEP_STAGE_DURATION_IN_MS_COL]
        return (start.iloc[-1] + duration.iloc[-1] - start.iloc[0]) / (1000 * 60)

    filtered_sleep_stages = sleep_stages[
        sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
            sleep_summary.index
        )
    ].reset_index(drop=True)
    return (
        filtered_sleep_stages[
            filtered_sleep_stages[constants._SLEEP_STAGE_SLEEP_TYPE_COL]
            != constants._SLEEP_STAGE_AWAKE_STAGE_VALUE
        ]
        .groupby(constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL)
        .apply(sleep_diff)
    )


def _compute_wake_after_sleep_onset(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
) -> pd.Series:
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    if not isinstance(sleep_stages, pd.DataFrame):
        raise ValueError(
            f"sleep_stages must be a pd.DataFrame. {type(sleep_stages)} is not a valid type."
        )
    filtered_sleep_stages = sleep_stages[
        sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
            sleep_summary.index
        )
    ].reset_index(drop=True)
    return filtered_sleep_stages[
        filtered_sleep_stages[constants._SLEEP_STAGE_SLEEP_TYPE_COL]
        == constants._SLEEP_STAGE_AWAKE_STAGE_VALUE
    ].groupby(constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL)[
        constants._SLEEP_SUMMARY_DURATION_IN_MS_COL
    ].sum() / (
        1000 * 60
    )


def _compute_n1_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
) -> pd.DataFrame:
    """Compute N1 latency from sleep data.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        A sleep summary in the format provided by :class:`pylabfront.loader.DataLoader`
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages in the format provided by :class:`pylabfront.loader.DataLoader`

    Returns
    -------
    :class:`pd.DataFrame`
        A DataFrame with N1 Latency as value, and sleep summary ids as indexes.
    """
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    if constants._SLEEP_STAGE_LIGHT_STAGE_VALUE in latencies.columns:
        n1_latency = latencies[constants._SLEEP_STAGE_LIGHT_STAGE_VALUE]
    else:
        n1_latency = pd.Series(np.nan, index=sleep_summary.index)
    return n1_latency


def _compute_n2_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
) -> pd.DataFrame:
    """Compute N2 latency from sleep data.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        A sleep summary in the format provided by :class:`pylabfront.loader.DataLoader`
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages in the format provided by :class:`pylabfront.loader.DataLoader`

    Returns
    -------
    :class:`pd.DataFrame`
        A DataFrame with N2 Latency as value, and sleep summary ids as indexes.
    """
    n2_latency = pd.Series(np.nan, index=sleep_summary.index)
    return n2_latency


def _compute_n3_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
) -> pd.DataFrame:
    """Compute N3 latency from sleep data.

    Parameters
    ----------
    sleep_summary : :class:`pd.DataFrame`
        A sleep summary in the format provided by :class:`pylabfront.loader.DataLoader`
    sleep_stages : :class:`pd.DataFrame`
        Sleep stages in the format provided by :class:`pylabfront.loader.DataLoader`

    Returns
    -------
    :class:`pd.DataFrame`
        A DataFrame with N3 Latency as value, and sleep summary ids as indexes.
    """
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    if constants._SLEEP_STAGE_DEEP_STAGE_VALUE in latencies.columns:
        n3_latency = latencies[constants._SLEEP_STAGE_DEEP_STAGE_VALUE]
    else:
        n3_latency = pd.Series(np.nan, index=sleep_summary.index)
    return n3_latency


def _compute_rem_latency(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
) -> pd.DataFrame:
    """Computes REM Latency from sleep data.

    Parameters
    ----------
    sleep_summary : pd.DataFrame
        A sleep summary in the format provided by :class:`pylabfront.loader.DataLoader`
    sleep_stages : pd.DataFrame
        Sleep stages in the format provided by :class:`pylabfront.loader.DataLoader`

    Returns
    -------
    pd.DataFrame
        A DataFrame with REM Latency as value, and sleep summary ids as indexes.
    """
    latencies = _compute_latencies(sleep_summary, sleep_stages)
    if constants._SLEEP_STAGE_REM_STAGE_VALUE in latencies.columns:
        rem_latency = latencies[constants._SLEEP_STAGE_REM_STAGE_VALUE]
    else:
        rem_latency = pd.Series(np.nan, index=sleep_summary.index)
    return rem_latency


def _compute_latencies(
    sleep_summary: pd.DataFrame, sleep_stages: pd.DataFrame
) -> pd.DataFrame:
    """Compute sleep stages latencies.

    This function computes latencies for each sleep stage
    contained in ``sleep_stages`.

    Parameters
    ----------
    sleep_summary : pd.DataFrame
        Sleep summaries, that can be extracted using :method:`pylabfront.loader.DataLoader.load_sleep_summary`
    sleep_stages : pd.DataFrame
        Sleep stages, that can be extracted using :method:`pylabfront.loader.DataLoader.load_sleep_stage`

    Returns
    -------
    pd.DataFrame
        The returned :class:`pd.DataFrame` has as index the
        values of the ids of the sleep summary to which they
        refer to, and one column for each sleep stage:
        awake, light, deep, and rem. If none of these sleep
        stage is present in the `sleep_stages`, then the
        column is not present.

    Raises
    ------
    ValueError
        If `sleep_summary` or `sleep_stages` are not of type :class:`pd.DataFrame`
    """
    if not isinstance(sleep_summary, pd.DataFrame):
        raise ValueError(
            f"sleep_summary must be a pd.DataFrame. {type(sleep_summary)} is not a valid type."
        )
    if not isinstance(sleep_stages, pd.DataFrame):
        raise ValueError(
            f"sleep_stages must be a pd.DataFrame. {type(sleep_stages)} is not a valid type."
        )
    filtered_sleep_stages = sleep_stages[
        sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
            sleep_summary.index
        )
    ].reset_index(drop=True)
    latencies = (
        filtered_sleep_stages.groupby(
            [
                constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL,
                constants._SLEEP_STAGE_SLEEP_TYPE_COL,
            ]
        )[constants._ISODATE_COL].first()
        - sleep_summary[constants._ISODATE_COL]
    ).dt.total_seconds() / (60)
    latencies = latencies.rename("latency")
    latencies = latencies.reset_index().pivot(
        columns=constants._SLEEP_STAGE_SLEEP_TYPE_COL,
        index=constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL,
        values="latency",
    )
    latencies = latencies.rename_axis(None, axis=1)
    return latencies


_SLEEP_STATISTICS_DICT = {
    _SLEEP_METRIC_TIB: _compute_time_in_bed,
    _SLEEP_METRIC_TST: _compute_total_sleep_time,
    _SLEEP_METRIC_SE: _compute_sleep_efficiency,
    _SLEEP_METRIC_SME: _compute_sleep_maintenance_efficiency,
    _SLEEP_METRIC_SPT: _compute_sleep_period_time,
    _SLEEP_METRIC_WASO: _compute_wake_after_sleep_onset,
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
}


def get_sleep_statistic(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list],
    metric: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
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

    Parameters
    ----------
    loader : :class:`pylabfront.loader.DataLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`
        The id(s) for which the sleep statistic must be computed.
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average the sleep statistic over days, or to return the value for each day, by default False

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
    if average:
        average_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        # Load sleep summary data
        sleep_summary = loader.load_garmin_connect_sleep_summary(
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
            sleep_stages = loader.load_garmin_connect_sleep_stage(
                user, sleep_summary_start_date, sleep_summary_end_date
            )
            # Keep only those belonging to sleep summaries
            sleep_stages = sleep_stages[
                sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
                    sleep_summary.index
                )
            ]
            # Compute metric -> pd.Series with sleepSummaryId as index
            metric_data = pd.DataFrame(
                _SLEEP_STATISTICS_DICT[metric](sleep_summary, sleep_stages).rename(
                    metric
                )
            )
            # Convert it to a pd.Series with calendarDate as index
            metric_data[constants._SLEEP_SUMMARY_CALENDAR_DATE_COL] = sleep_summary[
                constants._SLEEP_SUMMARY_CALENDAR_DATE_COL
            ]
            data_dict[user] = pd.Series(
                metric_data[metric].values,
                index=metric_data[constants._SLEEP_SUMMARY_CALENDAR_DATE_COL],
            ).to_dict()
            if average:
                sleep_data_df = pd.DataFrame.from_dict(data_dict[user], orient="index")
                average_dict[user] = {}
                if len(sleep_data_df[~sleep_data_df[0].isna()]) > 0:
                    average_dict[user][metric] = np.nanmean(
                        np.array(list(data_dict[user].values()))
                    )
                else:
                    average_dict[user][metric] = np.nan
                average_dict[user]["days"] = [
                    datetime.datetime.strftime(x, "%Y-%m-%d")
                    for x in sleep_data_df.index
                ]

    if average:
        return average_dict
    else:
        return data_dict


def get_sleep_statistics(
    loader: loader.LabfrontLoader,
    user_id: Union[str, list],
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    average: bool = False,
) -> dict:
    """Get sleep statistics from sleep data.

    This function is used by all the functions to get all the
    statistics from sleep data. It is more efficient than
    :func:`get_sleep_statistic` when multiple
    statistics are needed as it retrieves sleep data
    only once to compute all the statistics:

    Example::

        import pylabfront.loader
        import pylabfront.sleep
        import datetime

        loader = pylabfront.loader.LabfrontLoader()
        start_date = datetime.date(2023, 9, 9)
        end_date = datetime.date.today()
        user_id = "f457c562-2159-431c-8866-dfa9a917d9b8"

        pylabfront.sleep.get_sleep_statistics(loader, user_id, start_date, end_date)

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

        pylabfront.sleep.get_sleep_statistics(loader, user_id, start_date, end_date, average=True)
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
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str` or :class:`list`
        The id(s) for which the sleep statistic must be computed.
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    average : :class:`bool`, optional
        Whether to average the sleep statistic over days, or to return the value for each day, by default False

    Returns
    -------
    dict
        If ``average==False``, dictionary with ``user_id`` as key, and a nested dictionary with
        calendar days (as :class:`datetime.date`) as keys and sleep statistic key:value pairs.
        If ``average==True``, dictionary with ``user_id`` as key, and a nested dictionary with
        ``values`` as key of another nested dictionary with key:value pairs for each sleep statistic,
        and a ``days`` key that contains an array of all calendar days over which the average was computed.
    """
    data_dict = {}
    if average:
        average_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        # Load sleep summary data
        sleep_summary = loader.load_garmin_connect_sleep_summary(
            user, start_date, end_date, same_day_filter=True
        )
        if len(sleep_summary) > 0:
            sleep_summary = sleep_summary.set_index(
                constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL
            )
            # Metrics from sleep summary
            sleep_summary[_SLEEP_METRIC_TIB] = _compute_time_in_bed(sleep_summary)
            sleep_summary[_SLEEP_METRIC_TST] = _compute_total_sleep_time(sleep_summary)
            sleep_summary[_SLEEP_METRIC_SE] = _compute_sleep_efficiency(sleep_summary)
            sleep_summary[_SLEEP_METRIC_N1_PERCENTAGE] = _compute_n1_percentage(
                sleep_summary
            )
            sleep_summary[_SLEEP_METRIC_N2_PERCENTAGE] = np.nan
            sleep_summary[_SLEEP_METRIC_N3_PERCENTAGE] = _compute_n3_percentage(
                sleep_summary
            )
            sleep_summary[_SLEEP_METRIC_REM_PERCENTAGE] = _compute_rem_percentage(
                sleep_summary
            )
            sleep_summary[_SLEEP_METRIC_NREM_PERCENTAGE] = _compute_nrem_percentage(
                sleep_summary
            )
            sleep_summary[_SLEEP_METRIC_N1_DURATION] = _compute_n1_duration(
                sleep_summary
            )
            sleep_summary[_SLEEP_METRIC_N2_DURATION] = np.nan
            sleep_summary[_SLEEP_METRIC_N3_DURATION] = _compute_n3_duration(
                sleep_summary
            )
            sleep_summary[_SLEEP_METRIC_REM_DURATION] = _compute_rem_duration(
                sleep_summary
            )
            sleep_summary[_SLEEP_METRIC_NREM_DURATION] = _compute_nrem_duration(
                sleep_summary
            )
            # Metrics for sleep stages
            # SOL -
            # Load sleep stages from start to end of sleep summaries
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
            sleep_stages = loader.load_garmin_connect_sleep_stage(
                user, sleep_summary_start_date, sleep_summary_end_date
            )
            # Keep only those belonging to sleep summaries
            sleep_stages = sleep_stages[
                sleep_stages[constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL].isin(
                    sleep_summary.index
                )
            ]
            sleep_summary[_SLEEP_METRIC_SME] = _compute_sleep_maintenance_efficiency(
                sleep_summary, sleep_stages
            )
            sleep_summary[_SLEEP_METRIC_SPT] = _compute_sleep_period_time(
                sleep_summary, sleep_stages
            )
            sleep_summary[_SLEEP_METRIC_WASO] = _compute_wake_after_sleep_onset(
                sleep_summary, sleep_stages
            )
            latencies = _compute_latencies(sleep_summary, sleep_stages)
            if constants._SLEEP_STAGE_LIGHT_STAGE_VALUE in latencies.columns:
                sleep_summary[_SLEEP_METRIC_N1_LATENCY] = latencies[
                    constants._SLEEP_STAGE_LIGHT_STAGE_VALUE
                ]
            else:
                sleep_summary[_SLEEP_METRIC_N1_LATENCY] = np.nan
            sleep_summary[_SLEEP_METRIC_N2_LATENCY] = np.nan
            if constants._SLEEP_STAGE_DEEP_STAGE_VALUE in latencies.columns:
                sleep_summary[_SLEEP_METRIC_N3_LATENCY] = latencies[
                    constants._SLEEP_STAGE_DEEP_STAGE_VALUE
                ]
            else:
                sleep_summary[_SLEEP_METRIC_N3_LATENCY] = np.nan
            if constants._SLEEP_STAGE_REM_STAGE_VALUE in latencies.columns:
                sleep_summary[_SLEEP_METRIC_REM_LATENCY] = latencies[
                    constants._SLEEP_STAGE_REM_STAGE_VALUE
                ]
            else:
                sleep_summary[_SLEEP_METRIC_REM_LATENCY] = np.nan
            user_sleep_metrics_df = sleep_summary.set_index(
                sleep_summary[constants._SLEEP_SUMMARY_CALENDAR_DATE_COL]
            ).loc[
                :,
                [
                    _SLEEP_METRIC_TIB,
                    _SLEEP_METRIC_SPT,
                    _SLEEP_METRIC_WASO,
                    _SLEEP_METRIC_TST,
                    _SLEEP_METRIC_N1_DURATION,
                    _SLEEP_METRIC_N2_DURATION,
                    _SLEEP_METRIC_N3_DURATION,
                    _SLEEP_METRIC_REM_DURATION,
                    _SLEEP_METRIC_NREM_DURATION,
                    _SLEEP_METRIC_N1_LATENCY,
                    _SLEEP_METRIC_N2_LATENCY,
                    _SLEEP_METRIC_N3_LATENCY,
                    _SLEEP_METRIC_REM_LATENCY,
                    _SLEEP_METRIC_N1_PERCENTAGE,
                    _SLEEP_METRIC_N2_PERCENTAGE,
                    _SLEEP_METRIC_N3_PERCENTAGE,
                    _SLEEP_METRIC_REM_PERCENTAGE,
                    _SLEEP_METRIC_NREM_PERCENTAGE,
                    _SLEEP_METRIC_SE,
                    _SLEEP_METRIC_SME,
                ],
            ]
            data_dict[user] = user_sleep_metrics_df.to_dict("index")

            if average:
                average_dict[user] = {}
                average_dict[user]["values"] = user_sleep_metrics_df.mean().to_dict()
                average_dict[user]["days"] = [x for x in user_sleep_metrics_df.index]

    if average:
        return average_dict
    else:
        return data_dict
