"""
This module contains all the functions related to analysis
of sleep data.
"""

import numpy as np
import pandas as pd
import datetime
import yasa

import pylabfront.utils as utils
from collections import OrderedDict
import pylabfront.loader
import dateutil.parser

_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_REM_MS_COL = "remSleepInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_DEEP_SLEEP_MS_COL = "deepSleepDurationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_LIGHT_SLEEP_MS_COL = "lightSleepDurationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_AWAKE_SLEEP_MS_COL = "awakeDurationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_SLEEP_QUALITY_COL = "overallSleepScore"

_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL = "remSleepInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_LIGHT_SLEEP_MS_COL = "lightSleepDurationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_DEEP_SLEEP_MS_COL = "deepSleepDurationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_SLEEP_MS_COL = "awakeDurationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_MS_COL = (
    "unmeasurableSleepInMs"
)
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL = "durationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SCORE_COL = "overallSleepScore"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL = "calendarDate"
_LABFRONT_ISO_DATE_KEY = "isoDate"


_YASA_TIME_IN_BED = "TIB"
_YASA_SLEEP_PERIOD_TIME = "SPT"
_YASA_WAKE_AFTER_SLEEP_ONSET = "WASO"
_YASA_TOTAL_SLEEP_TIME = "TST"
_YASA_SLEEP_EFFICIENCY = "SE"
_YASA_SLEEP_MAINTENANCE_EFFICIENCY = "SME"
_YASA_SLEEP_ONSET_LATENCY = "SOL"
_YASA_N1_PERC = "%N1"
_YASA_N2_PERC = "%N2"
_YASA_N3_PERC = "%N3"
_YASA_REM_PERC = "%REM"
_YASA_NREM_PERC = "%NREM"
_YASA_N1_LATENCY = "Lat_N1"
_YASA_N2_LATENCY = "Lat_N2"
_YASA_N3_LATENCY = "Lat_N3"
_YASA_REM_LATENCY = "Lat_REM"
_YASA_N1_DURATION = "N1"
_YASA_N2_DURATION = "N2"
_YASA_N3_DURATION = "N3"
_YASA_REM_DURATION = "REM"
_YASA_NREM_DURATION = "NREM"


def get_time_in_sleep_stage(
    loader, sleep_stage, start_date=None, end_date=None, user_id="all", average=False
):
    """Get total time spent in a sleep stage for each day.

    This function returns the absolute time spent in a certain sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.
    This function considers only the first entry of the sleep summary in a given
    day. For example, consider the following sleep summary file::

        x4bda8f5-644c5284-6540,2023-04-29,7200000,1682723460000,2023-04-29T01:11:00.000+02:00
        x4bda8f5-644cf298-26e8,2023-04-29,7200000,1682764440000,2023-04-29T12:34:00.000+02:00

    There were two separate rows for the same day. One was for a full night sleep, while the second
    one was an afternoon nap. This function will consider only the first row.

    Parameters
    -----------
    loader: :class:`pylabfront.loader.LabfrontLoader`
        Instance of `LabfrontLoader`.
    sleep_stage: :class:`str`
        Type of sleep stage or metric to be extracted. Valid strings are:
            - REM': REM sleep stage.
            - LIGHT_SLEEP: Light sleep stage.
            - DEEP_SLEEP: Deep sleep stage.
            - AWAKE: Awake sleep stage.
            - UNMEASURABLE: Unmeasureable sleep stage.
            - DURATION: Total duration of sleep.
            - SLEEP_SCORE: Sleep score computed by Garmin.
    start_date :class:`datetime.datetime`, optional
        Start date from which sleep stages should be extracted, by default None.
    end_date :class:`datetime.datetime`, optional
        End date from which sleep stages should be extracted, by default None.
    user_id: :class:`str`, optional
        ID of the participants, by default "all".

    Returns
    -------
    :class:`dict`
        Dictionary with calendar day as key, and time spent in `sleep_stage` as value.
    """
    data_dict = {}
    if average:
        average_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    if not isinstance(user_id, list):
        raise TypeError("user_id has to be a list.")
    if sleep_stage == "REM":
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL
    elif sleep_stage == "LIGHT_SLEEP":
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_LIGHT_SLEEP_MS_COL
    elif sleep_stage == "DEEP_SLEEP":
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_DEEP_SLEEP_MS_COL
    elif sleep_stage == "AWAKE":
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_SLEEP_MS_COL
    elif sleep_stage == "UNMEASURABLE":
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_MS_COL
    elif sleep_stage == "DURATION":
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL
    elif sleep_stage == "SLEEP_SCORE":
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SCORE_COL
    else:
        raise ValueError("Invalid metric")

    for user in user_id:
        # Load sleep summary data
        participant_sleep_summary = loader.load_garmin_connect_sleep_summary(
            user, start_date, end_date
        )
        if len(participant_sleep_summary) > 0:
            participant_sleep_summary = participant_sleep_summary.groupby(
                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL
            ).head(1)
            data_dict[user] = pd.Series(
                participant_sleep_summary[column].values,
                index=participant_sleep_summary[
                    _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL
                ],
            ).to_dict()
            if average:
                sleep_data_df = pd.DataFrame.from_dict(data_dict[user], orient="index")
                average_dict[user] = {}
                average_dict[user]["values"] = np.nanmean(
                    np.array(list(data_dict[user].values()))
                )
                average_dict[user]["days"] = [x for x in sleep_data_df.index]

    if average:
        return average_dict
    return data_dict


def get_rem_sleep_duration(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get REM sleep time.

    This function returns the absolute time spent in REM stage for
    the given participant(s). Depending on the value of ``average``
    parameter, the function returns REM sleep time for each night (``average=False``),
    or the average REM sleep time from ``start_date`` to ``end_date`` (``average=True``).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which REM data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``, by default None
    end_date : :class:`datetime.datetime`, optional
        End date up to which REM data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``, by default None
    user_id : :class:`str`, optional
        IDs of the users for which REM data have to extracted, by default "all"
    average : bool, optional
        Average REM sleep across nights, by default False. If set to ``True``, then
        the average REM sleep from ``start_date`` to ``end_date`` is returned. Otherwise,
        REM sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    dict
    """
    return get_time_in_sleep_stage(
        loader, "REM", start_date, end_date, user_id, average
    )


def get_light_sleep_duration(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get light sleep time.

    This function returns the absolute time spent in light sleep stage for
    the given participant(s). Depending on the value of ``average``
    parameter, the function returns light sleep time for each night (``average=False``),
    or the average light sleep time from ``start_date`` to ``end_date`` (``average=True``).
    The primary key of the dictionary is always ``user_id``. If ``average`` is set to True,
    each value is a nested dictionary with the following structure:
        - ``LIGHT_SLEEP``: containing light sleep times
        - ``days``: days over which light sleep times were averaged
    If ``average`` is set to False,  each value is a nested dictionary with the following structure:
        - ``day`` : ``Light Sleep Time``

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which light sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which light sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which light sleep data have to extracted, by default "all"
    average : :class:`bool`, optional
        Average light sleep across nights, by default False.
        If set to ``True``, then the average light sleep from ``start_date`` to ``end_date`` is
        returned. Otherwise, light sleep for each night from ``start_date`` to ``end_date`` is returned.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the light sleep times for the given ``user_id``.
    """
    return get_time_in_sleep_stage(
        loader, "LIGHT_SLEEP", start_date, end_date, user_id, average
    )


def get_deep_sleep_duration(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get deep sleep time.

    This function returns the absolute time spent in deep sleep stage for
    the given participant(s). Depending on the value of ``average``
    parameter, the function returns deep sleep time for each night (``average=False``),
    or the average deep sleep time from ``start_date`` to ``end_date`` (``average=True``).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which deep sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which deep sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which deep sleep data have to extracted, by default "all"
    average : :class:`bool`, optional
        Average deep sleep across nights, by default False.
        If set to ``True``, then the average deep sleep from ``start_date`` to ``end_date`` is
        returned. Otherwise, deep sleep for each night from ``start_date`` to ``end_date`` is
        returned.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the deep sleep times for the given ``user_id``.
        The primary key of the dictionary is always ``user_id``.
        If ``average`` is set to True, each value is a nested dictionary
        with the following structure:
            - ``DEEP_SLEEP``: containing deep sleep times
            - ``days``: days over which deep sleep times were averaged
        If ``average`` is set to False,  each value is a nested dictionary
        with the following structure:
            - ``day`` : ``Deep Sleep Time``
    """

    return get_time_in_sleep_stage(
        loader, "DEEP_SLEEP", start_date, end_date, user_id, average
    )


def get_awake_sleep_duration(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get awake sleep time.

    This function returns the absolute time spent in awake sleep stage for
    the given participant(s). Depending on the value of ``average``
    parameter, the function returns awake sleep time for each night (``average=False``),
    or the average awake sleep time from ``start_date`` to ``end_date`` (``average=True``).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which awake sleep data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which awake sleep data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which awake sleep data have to extracted, by default "all"
    average : :class:`bool`, optional
        Average awake sleep across nights, by default False.
        If set to ``True``, then the average awake sleep from ``start_date`` to ``end_date`` is
        returned. Otherwise, awake sleep for each night from ``start_date`` to ``end_date`` is
        returned.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the awake sleep times for the given ``user_id``.
        The primary key of the dictionary is always ``user_id``.
        If ``average`` is set to True, each value is a nested dictionary
        with the following structure:

            - ``AWAKE``: containing awake sleep times
            - ``days``: days over which awake sleep times were averaged

        If ``average`` is set to False,  each value is a nested dictionary
        with the following structure:

            - ``day`` : ``Awake Sleep Time``

    """
    return get_time_in_sleep_stage(
        loader, "AWAKE", start_date, end_date, user_id, average
    )


def get_sleep_duration(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get sleep duration.

    This function returns the absolute sleep duration for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns sleep duration for each night (``average=False``),
    or the average sleep duration from ``start_date`` to ``end_date`` (``average=True``).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep duration data should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which awake sleep duration data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which sleep duration data have to extracted, by default "all"
    average : :class:`bool`, optional
        Average sleep duration across nights, by default False.
        If set to ``True``, then the average sleep duration from ``start_date`` to ``end_date`` is
        returned. Otherwise, sleep duration for each night from ``start_date`` to ``end_date`` is
        returned.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the sleep duration for the given ``user_id``.
        The primary key of the dictionary is always ``user_id``.
        If ``average`` is set to True, each value is a nested dictionary
        with the following structure:

            - ``DURATION``: containing sleep durations
            - ``days``: days over which awake duration values were averaged

        If ``average`` is set to False,  each value is a nested dictionary
        with the following structure:

        - ``day`` : ``Sleep Duration``
    """
    return get_time_in_sleep_stage(
        loader, "DURATION", start_date, end_date, user_id, average
    )


def get_sleep_score(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get sleep score.

    This function returns the sleep score for
    the given user(s). Depending on the value of ``average``
    parameter, the function returns sleep scores for each night (``average=False``),
    or the average sleep scores from ``start_date`` to ``end_date`` (``average=True``).

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which sleep scores should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available sleep data
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which awake sleep scores should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which sleep scores have to extracted, by default "all"
    average : :class:`bool`, optional
        Average sleep scores across nights, by default False.
        If set to ``True``, then the average sleep scores from ``start_date`` to ``end_date`` is
        returned. Otherwise, sleep scores for each night from ``start_date`` to ``end_date`` is
        returned.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the sleep scores for the given ``user_id``.
        The primary key of the dictionary is always ``user_id``.
        If ``average`` is set to True, each value is a nested dictionary
        with the following structure:

            - ``SLEEP_SCORE``: containing sleep score values
            - ``days``: days over which awake scores values were averaged

        If ``average`` is set to False, each value of the dictionary is a nested dictionary
        with the following structure:

        - ``day`` : ``Sleep Duration``

    """
    return get_time_in_sleep_stage(
        loader, "SLEEP_SCORE", start_date, end_date, user_id, average
    )


def get_sleep_statistics(
    labfront_loader: pylabfront.loader.LabfrontLoader,
    start_date=None,
    end_date=None,
    user_id="all",
    resolution=1,
    average=False,
):
    """Get sleep statistics from hypnograms.

    This function computes the following sleep statistics from the hypnogram
    extracted from sleep data:

        - Time In Bed (TIM): total duration of the hypnogram
        - Sleep Period Time (SPT): duration from first to last period of sleep.
        - Wake After Sleep Onset (WASO): duration of wake periods within SPT.
        - Total Sleep Time (TST): total duration of N1 + N2 + N3 + REM sleep in SPT.
        - Sleep Efficiency (SE): TST / TIB * 100 (%).
        - Sleep Maintenance Efficiency (SME): TST / SPT * 100 (%).
        - W, N1, N2, N3 and REM: sleep stages duration. NREM = N1 + N2 + N3.
        - % (W, … REM): sleep stages duration expressed in percentages of TST.
        - Latencies: latencies of sleep stages from the beginning of the record.
        - Sleep Onset Latency (SOL): Latency to first epoch of any sleep.

    The sleep statistics are automatically computed through `yasa <https://raphaelvallat.com/yasa>`_, so always make
    sure to check `yasa documentation <https://raphaelvallat.com/yasa/build/html/generated/yasa.sleep_statistics.html>`_
    to check the available sleep statistics.

    The sleep statistics are returned in dictionary format. If ``average`` is set
    to False, then the returned dictionary has ``participant_id`` as primary key,
    calendar days from ``start_date`` to ``end_date`` as secondary keys, and
    finally sleep statistics dictionary, with each key being the name of the
    statistic, and the value the corresponding computed value. If no sleep data
    is available for a given day, then ``None`` is returned in the dictionary. An example
    of the returned dictionary is the following ::

        {
            'ID-01': {
                datetime.datetime(2023, 3, 24, 0, 0): {
                    'TIB': 447.0,
                    'SPT': 447.0,
                    'WASO': 12.0,
                    'TST': 435.0,
                    'N1': 278.0,
                    'N2': 0.0,
                    'N3': 99.0,
                    'REM': 58.0,
                    'NREM': 377.0,
                    'SOL': 0.0,
                    'Lat_N1': 0.0,
                    'Lat_N2': nan,
                    'Lat_N3': 10.0,
                    'Lat_REM': 159.0,
                    '%N1': 63.9080459770115,
                    '%N2': 0.0,
                    '%N3': 22.75862068965517,
                    '%REM': 13.333333333333334,
                    '%NREM': 86.66666666666667,
                    'SE': 97.31543624161074,
                    'SME': 97.31543624161074
                },
                datetime.datetime(2023, 3, 25, 0, 0): None,
            }
        }

    If, instead, the ``average`` is set to ``True``, then the following
    dictionary is returned: ::

        {
            'ID-01': {
                'values': {
                    'TIB': 392.5,
                    'SPT': 392.3333333333333,
                    'WASO': 11.166666666666666,
                    'TST': 381.1666666666667,
                    'N1': 222.66666666666666,
                    'N2': 0.0,
                    'N3': 101.16666666666667,
                    'REM': 57.333333333333336,
                    'NREM': 323.8333333333333,
                    'SOL': 0.0,
                    'Lat_N1': 0.0,
                    'Lat_N2': nan,
                    'Lat_N3': 18.0,
                    'Lat_REM': 147.6,
                    '%N1': 58.720683726884715,
                    '%N2': 0.0,
                    '%N3': 27.14386877227862,
                    '%REM': 14.13544750083667,
                    '%NREM': 85.86455249916332,
                    'SE': 97.18162923269273,
                    'SME': 97.23617440388664
                    },
                'days': ['2023-03-24', '2023-03-28', '2023-03-29', '2023-03-30', '2023-03-31', '2023-04-04']
            }
        }

    Args:
        loader (_type_): _description_
        start_date (_type_, optional): _description_. Defaults to None.
        end_date (_type_, optional): _description_. Defaults to None.
        user_id (str, optional): _description_. Defaults to "all".
        resolution (int, optional): _description_. Defaults to 1.
        average (bool, optional): _description_. Defaults to False.

    Raises:
        TypeError: _description_

    Returns:
        _type_: _description_
    """
    user_id = utils.get_user_ids(labfront_loader, user_id)

    data_dict = {}
    average_dict = {}
    if type(start_date) == datetime.datetime:
        start_date = start_date.date()
    elif isinstance(start_date, str):
        start_date = dateutil.parser.parse(start_date).date()
    if type(end_date) == datetime.datetime:
        end_date = end_date.date()
    elif isinstance(end_date, str):
        end_date = dateutil.parser.parse(end_date).date()

    if not ((start_date is None) or (end_date is None)):
        intervals = int(divmod((end_date - start_date).total_seconds(), 3600 * 24)[0])
        calendar_days = [
            start_date + i * datetime.timedelta(days=1) for i in range(1, intervals + 1)
        ]
    for participant in user_id:
        data_dict[participant] = {}
        if (start_date is None) or (end_date is None):
            if start_date is None:
                # get first unix ts
                first_unix_ts = labfront_loader.get_first_unix_timestamp(
                    participant,
                    pylabfront.loader._LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING,
                )
                start_date = (
                    datetime.datetime.utcfromtimestamp(first_unix_ts / 1000)
                    - datetime.timedelta(hours=12)
                ).date()
            if end_date is None:
                # get first unix ts
                last_unix_ts = labfront_loader.get_last_unix_timestamp(
                    participant,
                    pylabfront.loader._LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING,
                )
                end_date = (
                    datetime.datetime.utcfromtimestamp(last_unix_ts / 1000)
                    + datetime.timedelta(hours=12)
                ).date()
            intervals = int(
                divmod((end_date - start_date).total_seconds(), 3600 * 24)[0]
            )
            calendar_days = [
                start_date + i * datetime.timedelta(days=1)
                for i in range(1, intervals + 1)
            ]
        for calendar_day in calendar_days:
            try:
                hypnogram = labfront_loader.load_hypnogram(
                    participant, calendar_day, resolution
                )
            except:
                if not average:
                    data_dict[participant][calendar_day] = None
                continue
            sleep_statistics = yasa.sleep_statistics(
                hypnogram["stage"], 1 / (resolution * 60)
            )
            data_dict[participant][calendar_day] = {}
            data_dict[participant][calendar_day] = sleep_statistics
        if average:
            sleep_stats_df = pd.DataFrame.from_dict(
                data_dict[participant], orient="index"
            )
            average_dict[participant] = {}
            average_dict[participant]["values"] = sleep_stats_df.mean().to_dict()
            average_dict[participant]["days"] = [x for x in sleep_stats_df.index]
    if average:
        return average_dict
    else:
        return data_dict


def get_sleep_statistic(
    loader,
    statistic,
    start_date=None,
    end_date=None,
    user_id="all",
    resolution=1,
    average=False,
):
    """Get a single sleep statistic computed from hypnograms.

    This function returns the computed sleep statistic. Valid options for the
    sleep statistic are:
        - :const:`sleep._YASA_TIME_IN_BED`: total duration of the hypnogram
        - :const:`sleep._YASA_SLEEP_PERIOD_TIME`: duration from first to last period of sleep.
        - :const:`sleep._YASA_WAKE_AFTER_SLEEP_ONSET`: duration of wake periods within SPT.
        - :const:`sleep._YASA_TOTAL_SLEEP_TIME`: total duration of N1 + N2 + N3 + REM sleep in SPT.
        - :const:`sleep._YASA_SLEEP_EFFICIENCY`: TST / TIB * 100 (%).
        - :const:`sleep._YASA_SLEEP_MAINTENANCE_EFFICIENCY`: TST / SPT * 100 (%).
        - :const:`sleep._YASA_SLEEP_ONSET_LATENCY`: Latency to first epoch of any sleep.
        - :const:`sleep._YASA_N1_PERC`: N1 sleep percentage of TST.
        - :const:`sleep._YASA_N2_PERC`: N2 sleep percentage of TST.
        - :const:`sleep._YASA_N3_PERC`: N3 sleep percentage of TST.
        - :const:`sleep._YASA_REM_PERC`: REM sleep percentage of TST.
        - :const:`sleep._YASA_NREM_PERC`: NREM sleep percentage of TST.
        - :const:`sleep._YASA_N1_DURATION`: N1 sleep stage duration.
        - :const:`sleep._YASA_N2_DURATION`: N2 sleep stage duration.
        - :const:`sleep._YASA_N3_DURATION`: N3 sleep stage duration.
        - :const:`sleep._YASA_REM_DURATION`: REM sleep stage duration.
        - :const:`sleep._YASA_NREM_DURATION`: NREM sleep stage duration.
        - :const:`sleep._YASA_N1_LATENCY`: Latency of first N1 sleep stage.
        - :const:`sleep._YASA_N2_LATENCY`: Latency of first N2 sleep stage.
        - :const:`sleep._YASA_N3_LATENCY`: Latency of first N3 sleep stage.
        - :const:`sleep._YASA_REM_LATENCY`: Latency of first REM sleep stage.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    statistic : :class:`str`
        Sleep statistic of interest.
    start_date : class:`datetime.datetime`, optional
        Start date from which the statistic has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the statistic has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the statistic has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the statistic has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the statistic or not, by default False.
        If set to True, then the statistic is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with data of the required sleep statistic.
    """
    all_stats_dict = get_sleep_statistics(
        loader,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        average=average,
        resolution=resolution,
    )
    statistic_dict = {}
    for user in all_stats_dict.keys():
        statistic_dict[user] = {}
        if not average:
            for day in all_stats_dict[user].keys():
                if isinstance(all_stats_dict[user][day], dict):
                    statistic_dict[user][day] = all_stats_dict[user][day][statistic]
                else:
                    statistic_dict[user][day] = None
        else:
            statistic_dict[user][statistic] = all_stats_dict[user]["values"][statistic]
            statistic_dict[user]["days"] = all_stats_dict[user]["days"]
    return statistic_dict


def get_time_in_bed(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get time in bed (TIB) statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from time in bed has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the time in bed has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the time in bed has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the time in bed has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the time in bed or not, by default False.
        If set to True, then the time in bed is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with time in bed data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_TIME_IN_BED,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_sleep_period_time(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get sleep period time (SPT) statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from sleep period time has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the sleep period time has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the sleep period time has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the sleep period time has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the sleep period time or not, by default False.
        If set to True, then the sleep period time is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with sleep period time data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_SLEEP_PERIOD_TIME,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_wake_after_sleep_onset(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get wake after sleep onset (WASO) statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from wake after sleep onset has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the wake after sleep onset has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the wake after sleep onset has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the wake after sleep onset has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the wake after sleep onset or not, by default False.
        If set to True, then the wake after sleep onset is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with wake after sleep onset data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_WAKE_AFTER_SLEEP_ONSET,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_total_sleep_time(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get total sleep time (TST) statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from total sleep time has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the total sleep time has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the total sleep time has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the total sleep time has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the total sleep time or not, by default False.
        If set to True, then the total sleep time is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with total sleep time data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_TOTAL_SLEEP_TIME,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_sleep_efficiency(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get sleep efficiency (SE) statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from sleep efficiency has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the sleep efficiency has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the sleep efficiency has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the sleep efficiency has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the sleep efficiency or not, by default False.
        If set to True, then the sleep efficiency is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with sleep efficiency data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_SLEEP_EFFICIENCY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_sleep_maintenance_efficiency(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get sleep maintenance efficiency (SE) statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from sleep maintenance efficiency has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the sleep maintenance efficiency has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the sleep maintenance efficiency has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the sleep maintenance efficiency has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the sleep maintenance efficiency or not, by default False.
        If set to True, then the sleep maintenance efficiency is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with sleep maintenance efficiency data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_SLEEP_MAINTENANCE_EFFICIENCY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_sleep_onset_latency(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get sleep onset latency (SE) statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from sleep onset latency has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the sleep onset latency has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the sleep onset latency has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the sleep onset latency has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the sleep onset latency or not, by default False.
        If set to True, then the sleep onset latency is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with sleep onset latency data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_SLEEP_ONSET_LATENCY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_rem_sleep_latency(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get REM sleep latency statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from REM sleep latency has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the REM sleep latency has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the REM sleep latency has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the REM sleep latency has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the REM sleep latency or not, by default False.
        If set to True, then the REM sleep latency is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with REM sleep latency data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_REM_LATENCY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_n1_sleep_latency(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get N1 sleep latency statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from N1 sleep latency has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the N1 sleep latency has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the N1 sleep latency has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the N1 sleep latency has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the N1 sleep latency or not, by default False.
        If set to True, then the N1 sleep latency is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with N1 sleep latency data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_N1_LATENCY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_n2_sleep_latency(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get N2 sleep latency statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from N2 sleep latency has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the N2 sleep latency has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the N2 sleep latency has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the N2 sleep latency has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the N2 sleep latency or not, by default False.
        If set to True, then the N2 sleep latency is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with N2 sleep latency data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_N2_LATENCY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_n3_sleep_latency(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get N3 sleep latency statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from N3 sleep latency has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the N3 sleep latency has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the N3 sleep latency has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the N3 sleep latency has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the N3 sleep latency or not, by default False.
        If set to True, then the N3 sleep latency is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with N3 sleep latency data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_N3_LATENCY,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_rem_sleep_percentage(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get REM sleep percentage statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from REM sleep percentage has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the REM sleep percentage has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the REM sleep percentage has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the REM sleep percentage has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the REM sleep percentage or not, by default False.
        If set to True, then the REM sleep percentage is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with REM sleep percentage data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_REM_PERC,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_n1_sleep_percentage(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get N1 sleep percentage statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from N1 sleep percentage has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the N1 sleep percentage has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the N1 sleep percentage has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the N1 sleep percentage has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the N1 sleep percentage or not, by default False.
        If set to True, then the N1 sleep percentage is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with N1 sleep percentage data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_N1_PERC,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_n2_sleep_percentage(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get N2 sleep percentage statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from N2 sleep percentage has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the N2 sleep percentage has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the N2 sleep percentage has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the N2 sleep percentage has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the N2 sleep percentage or not, by default False.
        If set to True, then the N2 sleep percentage is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with N2 sleep percentage data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_N2_PERC,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_n3_sleep_percentage(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get N3 sleep percentage statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from N3 sleep percentage has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the N3 sleep percentage has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the N3 sleep percentage has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the N3 sleep percentage has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the N3 sleep percentage or not, by default False.
        If set to True, then the N3 sleep percentage is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with N3 sleep percentage data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_N3_PERC,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_nrem_sleep_percentage(
    loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False
):
    """Get NREM sleep percentage statistic.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date from NREM sleep percentage has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the NREM sleep percentage has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the NREM sleep percentage has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    resolution : :class:`int`, optional
        Resolution in minutes for which the NREM sleep percentage has to be returned, by default 1.
        This affects the creation of the hypnogram.
    average : :class:`bool`, optional
        Whether to average the NREM sleep percentage or not, by default False.
        If set to True, then the NREM sleep percentage is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with NREM sleep percentage data.
    """
    return get_sleep_statistic(
        loader,
        statistic=_YASA_NREM_PERC,
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        resolution=resolution,
        average=average,
    )


def get_sleep_timestamps(
    loader: pylabfront.loader.LabfrontLoader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False,
):
    """Get the timestamps of the beginning and the end of sleep occurrences.

    Returns for every day, the time when the user fell asleep and when he woke up
    The information is based on the sleep summaries of the user

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    start_date : class:`datetime.datetime`, optional
        Start date of the period of interest, by default None.
    end_date : class:`datetime.datetime`, optional
        End date of the period of interest, by default None.
    user_id : :class:`str`, optional
        ID of the user for which sleep timestamps are computed, by default "all".
    average : :class:`bool`, optional
        Whether to calculate the average sleep and awake time of the user (in hours), by default False.

    Returns
    -------
    dict
        Dictionary with user ids as primary keys, if average is False then dates as secondary keys
        and sleep timestamps as values, otherwise (average starting time, average ending time) as values
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        # better to give a bit of rooms before and after start_date and end_date to ensure they're included
        df = loader.load_garmin_connect_sleep_summary(user, start_date, end_date)
        if len(df) > 0:
            df = df.groupby(
                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL
            ).head(1)
            df["waking_time"] = df[_LABFRONT_ISO_DATE_KEY] + df[
                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL
            ].astype(int).apply(lambda x: datetime.timedelta(milliseconds=x))
            data_dict[user] = pd.Series(
                zip(
                    df[_LABFRONT_ISO_DATE_KEY].dt.to_pydatetime(),
                    df["waking_time"].dt.to_pydatetime(),
                ),
                df[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL],
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
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False,
    return_days=False,
):
    """Get the midpoints of sleeping occurrences

    Returns for every night in the period of interest the midpoint of the
    sleeping process.
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None.
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest, by default None.
    user_id : :class:`str`, optional
        ID of the user for which sleep midpoints are computed, by default "all".
    average : bool, optional
        Whether to return the average midpoint for the user (in hours, from midnight), by default False
    return_days : bool, optional
        Whether to show the days used for the computation of the average, by default False

    Returns
    -------
    dict
        Dictionary with user ids as primary keys, if average is False then dates as secondary keys
        and sleep timestamps as values, otherwise the average for that user
    """
    data_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        sleep_timestamps = get_sleep_timestamps(loader, start_date, end_date, user)[
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


def get_awakenings(loader, start_date, end_date, user_id="all", average=False):
    """Get the number of awakenings

    Returns the number of times the user(s) of interest woke up during the night.
    This is checked considering the hypnogram and checking variations in sleep stages
    and awake status detection. If ``average`` is set to True, the average number of
    awakenings per night during the period between ``start_date`` and ``end_date`` is returned.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None.
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest, by default None.
    user_id : :class:`str`, optional
        ID of the user for which awakenings are computed, by default "all".
    average : bool, optional
        Whether to return only the average number of awakenings per night for the user, by default False

    Returns
    -------
    dict
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
            nights_available = df.calendarDate
            for night in nights_available:
                hypnogram = loader.load_hypnogram(user, night)
                # check if there a difference in stage between successive observations (first one defaults to no change)
                hypnogram["stages_diff"] = np.concatenate(
                    [
                        [0],
                        hypnogram.iloc[1:, :].stage.values
                        - hypnogram.iloc[:-1, :].stage.values,
                    ]
                )
                # if there has been a negative change and the current stage is awake, then count it as awakening
                hypnogram["awakening"] = np.logical_and(
                    hypnogram.stage == 0, hypnogram.stages_diff < 0
                )
                num_awakenings = hypnogram.awakening.sum()
                data_dict[user][night] = num_awakenings
            if average:
                average_dict[user]["value"] = np.nanmean(list(data_dict[user].values()))
                average_dict[user]["days"] = [
                    datetime.datetime.strftime(night, "%Y-%m-%d")
                    for night in nights_available
                ]
        except:
            data_dict[user] = None

    if average:
        return average_dict
    return data_dict

def get_cpd(loader, 
            start_date=None,
            end_date=None,
            user=None,
            sleep_metric="midpoint",
            chronotype_sleep_start = "00:00",
            chronotype_sleep_end = "08:00",
            days_to_consider=28,
            verbose=False,
            average=True):
    """Computes composite phase deviation (CPD)

    Returns a measure of sleep regularity, either in terms of stabmidpoints = ility of rest midpoints
    if `sleep_metric` is 'midpoint', or in terms of duration is `sleep_metric` is 'duration'.
    The measure is computed for the period between `start_date` and `end_date`
    but only keeping in consideration the most recent `days_to_consider`.
    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date from which to compute CPD, by default None.
    end_date : :class:`datetime.datetime`, optional
        End date until which to compute CPD, by default None.
    user : :class:`str`, optional
        ID of the user for which CPD is computed, by default None.
    sleep_metric : :class:`str`, optional
        the metric for the computation of CPD, can be either "midpoint" or "duration", by default "midpoint"
    chronotype_sleep_start : str, optional
        the hour of reference at which the user begins to sleep in format HH:MM, by default "00:00"
    chronotype_sleep_end : str, optional
        the hour of reference at which the user wakes up in format HH:MM, by default "08:00"
    days_to_consider : int, optional
        the maximum number of days to consider in the period of interest, by default 28
    verbose : :class:`str`, optional
        whether to show daily cpd components
    average : :class:`bool`, optional
        whether to return the CPD or the single day CPD components

    Returns
    -------
    float
        CPD metric, indicating sleep regularity of the user
    """

    if user is None:
        raise KeyError("Specify a user")

    if sleep_metric == "midpoint":
        # define what is the expected midpoint based on the chronotype
        chronotype_sleep_midpoint = utils.mean_time(
            [chronotype_sleep_start, chronotype_sleep_end]
        )
        sleep_midpoints = get_sleep_midpoints(loader, start_date, end_date, user)[user]

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
            sleep_durations = get_sleep_duration(loader, start_date, end_date, user)[
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
                daily_duration = daily_duration / (
                    1000 * 60 * 60
                )  # conversion in hours

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
        return {dates[i]:CPDs[i] for i in range(len(dates))}


def get_sleep_metric_std(
    loader, start_date=None, end_date=None, user=None, metric=None
):
    """Calculates standard deviation of a desired sleep metric

    Given a selected metric, calculates for the period of interest and user of interest, its standard deviation
    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date for the period of interest, by default None.
    end_date : :class:`datetime.datetime`, optional
        End date for the period of interest, by default None.
    user : str, optional
        user id for the user of interest, by default None
    metric : str, optional
        name of the metric or name of the sleep function for which calculate std, by default None

    Returns
    -------
    float
        Standard deviation for the sleep metric of interest
    """

    if metric is None:
        raise KeyError("Must specify a valid sleep metric")
    elif metric == "duration":  # in hours
        metric_data = get_sleep_duration(loader, start_date, end_date, user)[user]
        metric_data = [duration / (1000 * 60 * 60) for duration in metric_data.values()]
    elif metric == "midpoint":  # in hours
        midpoints = list(
            get_sleep_midpoints(loader, start_date, end_date, user)[user].values()
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
            metric_data = metric(loader, start_date, end_date, user)[user]
            metric_data = list(metric_data.values())
        except:
            raise KeyError(
                "Metric specified isn't valid"
            )  # TODO implement for other features as needed

    return np.nanstd(metric_data)
