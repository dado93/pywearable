"""
This module contains all the functions related to the analysis
of Labfront cardiac data.
"""

import pylabfront.utils as utils
import numpy as np
import pandas as pd
import datetime

_LABFRONT_SPO2_COLUMN = "spo2"

_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATA_COL = "calendarDate"
_LABFRONT_HR_COLUMN = "beatsPerMinute"

_LABFRONT_RESTING_HR_COLUMN = "restingHeartRateInBeatsPerMinute"
_LABFRONT_AVG_HR_COLUMN = "averageHeartRateInBeatsPerMinute"
_LABFRONT_MAX_HR_COLUMN = "maxHeartRateInBeatsPerMinute"
_LABFRONT_MIN_HR_COLUMN = "minHeartRateInBeatsPerMinute"


def get_rest_spO2(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False,
):
    """Get spO2 during sleep.

    This function returns the mean rest spO2 computed for every day. 

    Parameters
    ----------
    loader: :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date: :class:`datetime.datetime`, optional
        Start date from which rest spO2 must be computed, by default None.
    end_date: :class:`datetime.datetime`, optional
        End date to which rest spO2 must be computed, by default None.
    user_id: :class:`str`, optional
        ID of the user for which spO2 must be computed, by default "all".
    average: :class:'bool', optional
        Whether to average the statistic or not, by default False.
        If set to True, then the statistic is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys, and rest spO2 as value.
    """

    user_id = utils.get_user_ids(loader,user_id)

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
                    spo2_data.groupby(
                        spo2_data[loader.date_column].dt.date
                    )[_LABFRONT_SPO2_COLUMN]
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

def get_cardiac_statistic(loader,
    statistic,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False
):
    """Get a single cardiac summary statistic.

    This function returns the cardiac statistic. Valid options for the
    cardiac statistic are:
        - :const:`cardiac._LABFRONT_RESTING_HR_COLUMN`: Average heart rate at rest during the monitoring period.
        - :const:`cardiac._LABFRONT_AVG_HR_COLUMN`: Average of heart rate values captured during the monitoring period. 
        - :const:`cardiac._LABFRONT_MAX_HR_COLUMN`: Maximum of heart rate values captured during the monitoring period.
        - :const:`cardiac._LABFRONT_MIN_HR_COLUMN`: Minimum of heart rate values captured during the monitoring period.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of a data loader.
    statistic : :class:`str`
        Cardiac statistic of interest.
    start_date : class:`datetime.datetime`, optional
        Start date from which the statistic has to be retrieved, by default None.
        If set to None, then the start date is set to the first date available.
    end_date : class:`datetime.datetime`, optional
        End date before which the statistic has to be retrieved, by default None.
        If set to None, then the end date is set to the last date available.
    user_id : :class:`str` or :class:`list`, optional
        ID of the user(s) for which the statistic has to be retrieved, by default "all".
        If multiple users are required, a list must be passed.
    average : :class:`bool`, optional
        Whether to average the statistic or not, by default False.
        If set to True, then the statistic is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with data of the required cardiac statistic.
    """
    user_id = utils.get_user_ids(loader,user_id)

    data_dict = {}
    if average:
        average_dict = {}

    for user in user_id:
        try:
            daily_summary_data = loader.load_garmin_connect_daily_summary(user,start_date,end_date)
            if len(daily_summary_data) > 0:
                data_dict[user] = pd.Series(daily_summary_data[statistic].values,
                                            index=daily_summary_data[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATA_COL]).to_dict()
        
            if average:
                cardiac_data_df = pd.DataFrame.from_dict(
                    data_dict[user], orient="index"
                )
                average_dict[user] = {}
                average_dict[user]["values"] = np.nanmean(
                    np.array(list(data_dict[user].values()))
                )
                average_dict[user]["days"] = [
                    datetime.datetime.strftime(x, "%Y-%m-%d")
                    for x in cardiac_data_df.index
                ]
        except:
            data_dict[user] = None
    
    if average:
        return average_dict
    return data_dict


def get_rest_heart_rate(loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False
):
    """Get heart rate during sleep.

    This function returns the heart rate while sleeping computed for every day. 

    Parameters
    ----------
    loader: :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date: :class:`datetime.datetime`, optional
        Start date from which rest heart rate must be computed, by default None.
    end_date: :class:`datetime.datetime`, optional
        End date to which rest heart rate must be computed, by default None.
    user_id: :class:`str`, optional
        ID of the user for which resting heart rate must be computed, by default "all".
    average: :class:'bool', optional
        Whether to average the statistic or not, by default False.
        If set to True, then the statistic is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys,
        and resting heart rate as value.
    """

    return get_cardiac_statistic(loader,_LABFRONT_RESTING_HR_COLUMN,start_date,end_date,user_id,average)

def get_max_heart_rate(loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False
):
    """Get maximum daily heart rate.

    This function returns the maximum heart rate recoreded for every day. 

    Parameters
    ----------
    loader: :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date: :class:`datetime.datetime`, optional
        Start date from which max heart rate must be computed, by default None.
    end_date: :class:`datetime.datetime`, optional
        End date to which max heart rate must be computed, by default None.
    user_id: :class:`str`, optional
        ID of the user for which max heart rate must be computed, by default "all".
    average: :class:'bool', optional
        Whether to average the statistic or not, by default False.
        If set to True, then the statistic is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys,
        and maximum heart rate as value.
    """

    return get_cardiac_statistic(loader,_LABFRONT_MAX_HR_COLUMN,start_date,end_date,user_id,average)

def get_min_heart_rate(loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False
):
    """Get minimum daily heart rate.

    This function returns the minimum heart rate recoreded for every day. 

    Parameters
    ----------
    loader: :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date: :class:`datetime.datetime`, optional
        Start date from which min heart rate must be computed, by default None.
    end_date: :class:`datetime.datetime`, optional
        End date to which min heart rate must be computed, by default None.
    user_id: :class:`str`, optional
        ID of the user for which min heart rate must be computed, by default "all".
    average: :class:'bool', optional
        Whether to average the statistic or not, by default False.
        If set to True, then the statistic is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys,
        and minimum heart rate as value.
    """
    return get_cardiac_statistic(loader,_LABFRONT_MIN_HR_COLUMN,start_date,end_date,user_id,average)

def get_avg_heart_rate(loader,
    start_date=None,
    end_date=None,
    user_id="all",
    average=False
):
    """Get average daily heart rate.

    This function returns the average heart rate recoreded for every day. 

    Parameters
    ----------
    loader: :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date: :class:`datetime.datetime`, optional
        Start date from which average heart rate must be computed, by default None.
    end_date: :class:`datetime.datetime`, optional
        End date to which average heart rate must be computed, by default None.
    user_id: :class:`str`, optional
        ID of the user for which average heart rate must be computed, by default "all".
    average: :class:'bool', optional
        Whether to average the statistic or not, by default False.
        If set to True, then the statistic is returned as the average from
        ``start_date`` to ``end_date``. If set to False, then a single value
        is returned for each day from ``start_date`` to ``end_date``.

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, calendar days as secondary keys,
        and average heart rate as value.
    """
    return get_cardiac_statistic(loader,_LABFRONT_AVG_HR_COLUMN,start_date,end_date,user_id,average)