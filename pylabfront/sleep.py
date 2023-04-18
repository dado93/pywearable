"""
This module contains all the functions related to analysis
of Labfront sleep data.
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


def get_sleep_summary_stage_by_day(loader, sleep_stage, start_date=None, end_date=None, participant_id="all"):
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
    if participant_id == "all":
        # get all participant ids automatically
        participant_id = loader.get_user_ids()

    if isinstance(participant_id, str):
        participant_id = [participant_id]

    if not isinstance(participant_id, list):
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

    for participant in participant_id:
        # Load sleep summary data
        participant_sleep_summary = loader.load_garmin_connect_sleep_summary(
            participant, start_date, end_date)
        if len(participant_sleep_summary) > 0:
            data_dict[participant] = pd.Series(participant_sleep_summary[column].values,
                                               index=participant_sleep_summary[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DAY_COL]).to_dict()

    return data_dict


def get_sleep_summary_stage_average(loader, sleep_stage, start_date=None, end_date=None, participant_id="all"):
    """"Get average time spent in a sleep stage across timerange.

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        sleep_stage (str): Type of sleep stage or metric to be extracted.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Dictionary with participant id as key, and average time spent in `sleep_stage` as value.
    """
    data_dict = get_sleep_summary_stage_by_day(
        loader, sleep_stage, start_date, end_date, participant_id)
    average_dict = {}
    for participant in data_dict.keys():
        average_dict[participant] = np.array(
            list(data_dict[participant].values())).mean()
    return average_dict


def get_rem_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get REM sleep time for each day.

    This function returns the absolute time spent in REM stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "REM", start_date, end_date, participant_id)


def get_average_rem_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average REM sleep time across time range.

    This function returns the average time spent in REM stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_average(loader, "REM", start_date, end_date, participant_id)


def get_light_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get light sleep time for each day.

    This function returns the absolute time spent in light stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "LIGHT_SLEEP", start_date, end_date, participant_id)


def get_average_light_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average light sleep time across time range.

    This function returns the average time spent in light sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_average(loader, "LIGHT_SLEEP", start_date, end_date, participant_id)


def get_deep_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get deep sleep time for each day.

    This function returns the absolute time spent in deep sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which REM data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which REM data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "DEEP_SLEEP", start_date, end_date, participant_id)


def get_average_deep_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average deep sleep time across time range.

    This function returns the average time spent in deep sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which deep sleep data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which deep sleep data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_average(loader, "DEEP_SLEEP", start_date, end_date, participant_id)


def get_awake_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get awake sleep time for each day.

    This function returns the absolute time spent in awake stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which awake sleep data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which awake sleep data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".
    """
    return get_sleep_summary_stage_by_day(loader, "AWAKE", start_date, end_date, participant_id)


def get_average_awake_sleep(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average wake sleep time across time range.

    This function returns the average time spent in deep sleep stage for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which awake sleep data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which awake sleep data should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Return:
        dict: average awake sleep.
    """
    return get_sleep_summary_stage_average(loader, "AWAKE", start_date, end_date, participant_id)


def get_sleep_duration(loader, start_date=None, end_date=None, participant_id="all"):
    """Get sleep duration for each day.

    This function returns the total sleep duration for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which total sleep duration should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which total sleep duration should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Returns:
        dict: Total sleep duration by participant and by day.
    """
    return get_sleep_summary_stage_by_day(loader, "DURATION", start_date, end_date, participant_id)


def get_average_sleep_duration(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average sleep duration across time range.

    This function returns the average sleep duration for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep duration should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep duration should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Return:
        dict: average awake sleep.
    """
    return get_sleep_summary_stage_average(loader, "DURATION", start_date, end_date, participant_id)


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
    return get_sleep_summary_stage_by_day(loader, "SLEEP_SCORE", start_date, end_date, participant_id)


def get_average_sleep_score(loader, start_date=None, end_date=None, participant_id="all"):
    """Get average sleep score across time range.

    This function returns the average sleep score for
    the given participant(s) for each given day from ``start_date`` to
    ``end_date``, in units of milliseconds.

    Args:
        load: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which sleep score should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which sleep score should be extracted. Defaults to None.
        participant_id (:class:`str`, optional): ID of the participants. Defaults to "all".

    Return:
        dict: Average sleep score by participant.
    """
    return get_sleep_summary_stage_average(loader, "SLEEP_SCORE", start_date, end_date, participant_id)


def get_sleep_statistics(loader, start_date=None, end_date=None,
                         participant_id="all", resolution=1, average=False):
    data_dict = {}
    intervals = int(
        divmod((end_date - start_date).total_seconds(), 3600*12)[0])
    calendar_days = [
        start_date + i * datetime.timedelta(days=1) for i in range(intervals)]
    for participant in participant_id:
        data_dict[participant] = {}
        for calendar_day in calendar_days:
            hypnogram = loader.load_hypnogram(
                participant, calendar_day, resolution)
            if len(hypnogram) > 0:
                data_dict[participant][calendar_day] = {}
                sleep_statistics = yasa.sleep_statistics(
                    hypnogram['stage'], 1/(resolution*60))
                if not average:
                    data_dict[participant][calendar_day] = sleep_statistics
                else:
                    for statistic in sleep_statistics.keys():
                        data_dict[participant][calendar_day][statistic] = np.array(
                            list(sleep_statistics[statistic])).nanmean()


def get_time_in_bed(loader, start_date=None, end_date=None, participant_id="all", average=False):

    pass


def get_sleep_period_time():
    pass


def get_wake_after_sleep_onset():
    pass


def get_total_sleep_time():
    pass


def get_sleep_efficiency():
    pass


def get_sleep_maintenance_efficiency():
    pass


def get_sleep_onset_latency():
    pass


def get_sleep_latencies():
    pass


def get_number_of_arousals():
    pass
