"""
This module contains all the functions related to analysis
of sleep data.
"""

import numpy as np
import pandas as pd
import datetime
import yasa

_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_DEEP_SLEEP_MS_COL = 'deepSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_LIGHT_SLEEP_MS_COL = 'lightSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_AWAKE_SLEEP_MS_COL = 'awakeDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_SLEEP_QUALITY_COL = 'overallSleepScore'

_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL = 'remSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_LIGHT_SLEEP_MS_COL = 'lightSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_DEEP_SLEEP_MS_COL = 'deepSleepDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_SLEEP_MS_COL = 'awakeDurationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_MS_COL = 'unmeasurableSleepInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL = 'durationInMs'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SCORE_COL = 'overallSleepScore'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL = 'calendarDate'

_YASA_TIME_IN_BED = 'TIB'
_YASA_SLEEP_PERIOD_TIME = 'SPT'
_YASA_WAKE_AFTER_SLEEP_ONSET = 'WASO'
_YASA_TOTAL_SLEEP_TIME = 'TST'
_YASA_SLEEP_EFFICIENCY = 'SE'
_YASA_SLEEP_MAINTENANCE_EFFICIENCY = 'SME'
_YASA_SLEEP_ONSET_LATENCY = 'SOL'
_YASA_N1_PERC = '%N1'
_YASA_N2_PERC = '%N2'
_YASA_N3_PERC = '%N3'
_YASA_REM_PERC = '%REM'
_YASA_NREM_PERC = '%NREM'
_YASA_N1_LATENCY = 'Lat_N1'
_YASA_N2_LATENCY = 'Lat_N2'
_YASA_N3_LATENCY = 'Lat_N3'
_YASA_REM_LATENCY = 'Lat_REM'
_YASA_N1_DURATION = 'N1'
_YASA_N2_DURATION = 'N2'
_YASA_N3_DURATION = 'N3'
_YASA_REM_DURATION = 'REM'
_YASA_NREM_DURATION = 'NREM '


def get_time_in_sleep_stage(loader, sleep_stage, start_date=None, end_date=None, user_id="all", average=False):
    """Get total time spent in a sleep stage for each day.

    This function returns the absolute time spent in a certain sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        sleep_stage (str): Type of sleep stage or metric to be extracted.
                            'REM': REM sleep stage.
                            'LIGHT_SLEEP': Light sleep stage.
                            'DEEP_SLEEP': Deep sleep stage.
                            'AWAKE': Awake sleep stage.
                            'UNMEASURABLE': Unmeasureable sleep stage.
                            'DURATION': Total duration of sleep.
                            'SLEEP_SCORE': Sleep score computed by Garmin.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep stages should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep stages should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with calendar day as key, and time spent in `sleep_stage` as value.
    """
    data_dict = {}
    if average:
        average_dict = {}
    if user_id == "all":
        # get all participant ids automatically
        user_id = loader.get_user_ids()

    if isinstance(user_id, str):
        user_id = [user_id]

    if not isinstance(user_id, list):
        raise TypeError("participant_ids has to be a list.")
    if sleep_stage == 'REM':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_REM_MS_COL
    elif sleep_stage == 'LIGHT_SLEEP':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_LIGHT_SLEEP_MS_COL
    elif sleep_stage == 'DEEP_SLEEP':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_DEEP_SLEEP_MS_COL
    elif sleep_stage == 'AWAKE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_SLEEP_MS_COL
    elif sleep_stage == 'UNMEASURABLE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_MS_COL
    elif sleep_stage == 'DURATION':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_MS_COL
    elif sleep_stage == 'SLEEP_SCORE':
        column = _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SCORE_COL
    else:
        raise ValueError("Invalid metric")

    for user in user_id:
        # Load sleep summary data
        participant_sleep_summary = loader.load_garmin_connect_sleep_summary(
            user, start_date, end_date)
        if len(participant_sleep_summary) > 0:
            data_dict[user] = pd.Series(participant_sleep_summary[column].values,
                                        index=participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL]).to_dict()
            if average:
                average_dict[user] = np.array(
                    list(data_dict[user].values())).mean()
    if average:
        return average_dict
    return data_dict


def get_rem_sleep_duration(loader, start_date=None, end_date=None, user_id="all", average=False):
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
        for the given ``user_id``.
    end_date : :class:`datetime.datetime`, optional
        End date up to which REM data should be extracted, by default None.
        If None is used, then the ``end_date`` will be the last day with available sleep data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which REM data have to extracted, by default "all"
    average : :class:`bool`, optional
        Average REM sleep across nights, by default False.
        If set to ``True``, then the average REM sleep from ``start_date`` to ``end_date`` is
        returned. Otherwise, REM sleep for each night from ``start_date`` to ``end_date`` is 
        returned.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the REM sleep times for the given ``user_id``. 
        The primary key of the dictionary is always ``user_id``.
        If ``average`` is set to True, each value is a nested dictionary 
        with the following structure:
        - ``REM``: containing REM sleep times
        - ``days``: days over which REM sleep times were averaged
        If ``average`` is set to False,  each value is a nested dictionary
        with the following structure:
        - ``day`` : ``REM Sleep Time``
    """
    return get_time_in_sleep_stage(loader, "REM", start_date, end_date, user_id, average)


def get_light_sleep_duration(loader, start_date=None, end_date=None, user_id="all", average=False):
    """Get light sleep time.

    This function returns the absolute time spent in light sleep stage for
    the given participant(s). Depending on the value of ``average``
    parameter, the function returns light sleep time for each night (``average=False``),
    or the average light sleep time from ``start_date`` to ``end_date`` (``average=True``).

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
        returned. Otherwise, light sleep for each night from ``start_date`` to ``end_date`` is 
        returned.

    Returns
    -------
    :class:`dict`
        The returned dictionary contains the light sleep times for the given ``user_id``. 
        The primary key of the dictionary is always ``user_id``.
        If ``average`` is set to True, each value is a nested dictionary 
        with the following structure:
        - ``LIGHT_SLEEP``: containing light sleep times
        - ``days``: days over which light sleep times were averaged
        If ``average`` is set to False,  each value is a nested dictionary
        with the following structure:has to be
        - ``day`` : ``Light Sleep Time``
    """
    return get_time_in_sleep_stage(loader, "LIGHT_SLEEP", start_date, end_date, user_id, average)


def get_deep_sleep_duration(loader, start_date=None, end_date=None, user_id="all", average=False):
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
    return get_time_in_sleep_stage(loader, "DEEP_SLEEP", start_date, end_date, user_id, average)


def get_awake_sleep_duration(loader, start_date=None, end_date=None, participant_id="all"):
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
    return get_time_in_sleep_stage(loader, "AWAKE", start_date, end_date, participant_id)


def get_sleep_duration(loader, start_date=None, end_date=None, participant_id="all"):
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
        - ``awake_SLEEP``: containing awake sleep times
        - ``days``: days over which awake sleep times were averaged
        If ``average`` is set to False,  each value is a nested dictionary
        with the following structure:
        - ``day`` : ``Sleep Duration``
    """
    return get_time_in_sleep_stage(loader, "DURATION", start_date, end_date, participant_id)


def get_sleep_score(loader, start_date=None, end_date=None, participant_id="all"):
    """Get sleep score for each day.

    This function returns the sleep score for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep score should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep score should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Sleep score by participant and by day.
    """
    return get_time_in_sleep_stage(loader, "SLEEP_SCORE", start_date, end_date, participant_id)


def get_sleep_statistics(loader, start_date=None, end_date=None,
                         user_id="all", resolution=1, average=False):
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
    if user_id == "all":
        # get all participant ids automatically
        user_id = loader.get_user_ids()

    if isinstance(user_id, str):
        user_id = [user_id]

    if not isinstance(user_id, list):
        raise TypeError("participant_ids has to be a list.")

    data_dict = {}
    average_dict = {}
    intervals = int(
        divmod((end_date - start_date).total_seconds(), 3600*12)[0])
    calendar_days = [
        start_date + i * datetime.timedelta(days=1) for i in range(intervals)]
    for participant in user_id:
        data_dict[participant] = {}
        for calendar_day in calendar_days:
            try:
                hypnogram = loader.load_hypnogram(
                    participant, calendar_day, resolution)
            except:
                if not average:
                    data_dict[participant][calendar_day] = None
                continue
            sleep_statistics = yasa.sleep_statistics(
                hypnogram['stage'], 1/(resolution*60))
            data_dict[participant][calendar_day] = {}
            data_dict[participant][calendar_day] = sleep_statistics
        if average:
            sleep_stats_df = pd.DataFrame.from_dict(
                data_dict[participant], orient='index')
            average_dict[participant] = {}
            average_dict[participant]['values'] = sleep_stats_df.mean().to_dict()
            average_dict[participant]['days'] = [datetime.datetime.strftime(
                x, "%Y-%m-%d") for x in sleep_stats_df.index]
    if average:
        return average_dict
    else:
        return data_dict


def get_sleep_statistic(loader, statistic, start_date=None, end_date=None,
                        user_id="all", resolution=1, average=False):
    all_stats_dict = get_sleep_statistics(
        loader, start_date=start_date, end_date=end_date, user_id=user_id, average=average, resolution=resolution)
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
            statistic_dict[user][statistic] = all_stats_dict[user]['values'][statistic]
            statistic_dict[user]['days'] = all_stats_dict[user]['days']
    return statistic_dict


def get_time_in_bed(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_TIME_IN_BED,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_sleep_period_time(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_SLEEP_PERIOD_TIME,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_wake_after_sleep_onset(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_WAKE_AFTER_SLEEP_ONSET,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_total_sleep_time(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_TOTAL_SLEEP_TIME,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_sleep_efficiency(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_SLEEP_EFFICIENCY,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_sleep_maintenance_efficiency(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_SLEEP_MAINTENANCE_EFFICIENCY,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_sleep_onset_latency(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_SLEEP_ONSET_LATENCY,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_rem_sleep_latency(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_REM_LATENCY,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_n1_sleep_latency(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_N1_LATENCY,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_n2_sleep_latency(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_N2_LATENCY,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_n3_sleep_latency(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_N3_LATENCY,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_rem_sleep_percentage(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_REM_PERC,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_n1_sleep_percentage(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_N1_PERC,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_n2_sleep_percentage(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_N2_PERC,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_n3_sleep_percentage(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_N3_PERC,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)


def get_nrem_sleep_percentage(loader, start_date=None, end_date=None, user_id="all", resolution=1, average=False):
    return get_sleep_statistic(loader, statistic=_YASA_NREM_PERC,
                               start_date=start_date, end_date=end_date,
                               user_id=user_id, resolution=resolution, average=average)
