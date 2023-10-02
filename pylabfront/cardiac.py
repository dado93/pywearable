"""
This module contains all the functions related to the analysis
of Labfront cardiac data.
"""

import datetime

import hrvanalysis
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyhrv

import pylabfront.sleep as sleep
import pylabfront.utils as utils

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
                        _LABFRONT_SPO2_COLUMN
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


def get_cardiac_statistic(
    loader, statistic, start_date=None, end_date=None, user_id="all", average=False
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
    user_id = utils.get_user_ids(loader, user_id)

    data_dict = {}
    if average:
        average_dict = {}

    for user in user_id:
        try:
            daily_summary_data = loader.load_garmin_connect_daily_summary(
                user, start_date, end_date
            )
            if len(daily_summary_data) > 0:
                daily_summary_data = daily_summary_data.groupby(
                    _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATA_COL
                ).tail(1)
                data_dict[user] = pd.Series(
                    daily_summary_data[statistic].values,
                    index=daily_summary_data[
                        _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATA_COL
                    ].dt.date,
                ).to_dict()

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


def get_rest_heart_rate(
    loader, start_date=None, end_date=None, user_id="all", average=False
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

    return get_cardiac_statistic(
        loader, _LABFRONT_RESTING_HR_COLUMN, start_date, end_date, user_id, average
    )


def get_max_heart_rate(
    loader, start_date=None, end_date=None, user_id="all", average=False
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

    return get_cardiac_statistic(
        loader, _LABFRONT_MAX_HR_COLUMN, start_date, end_date, user_id, average
    )


def get_min_heart_rate(
    loader, start_date=None, end_date=None, user_id="all", average=False
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
    return get_cardiac_statistic(
        loader, _LABFRONT_MIN_HR_COLUMN, start_date, end_date, user_id, average
    )


def get_avg_heart_rate(
    loader, start_date=None, end_date=None, user_id="all", average=False
):
    """Get average daily heart rate.

    This function returns the average heart rate recorded for every day.

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


def get_hrv_time_domain(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    pyhrv=False,
    filtering_kwargs={},
):
    """Get time-domain heart rate variability features.

    This function returns a dictionary containing for every user of interest
    the time domain hrv features for the period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    pyhrv : bool, optional
        whether to use pyhrv to compute features, alternatively hrvanalysis is used, by default False
    filtering_kwargs : dict, optional
        kwargs of the bbi filtering function for outliers and ectopic beats, by default {}

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key, time-domain hrv feature names as secondary keys,
        and the values of the features as dictionary values.
    """
    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            bbi = loader.load_garmin_device_bbi(user,start_date,end_date).bbi
            bbi = utils.filter_bbi(bbi, **filtering_kwargs)
            if pyhrv: # pyhrv has more features but it's a lot slower
                td_features = pyhrv.time_domain.time_domain(bbi).as_dict()
            else:
                td_features = hrvanalysis.get_time_domain_features(bbi)
            data_dict[user] = td_features
        except:
            data_dict[user] = None

    return data_dict


def get_hrv_frequency_domain(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    method="ar",
    filtering_kwargs={},
    method_kwargs={},
):
    """Get frequency-domain heart rate variability features.

    This function returns a dictionary containing for every user of interest
    the frequency domain hrv features for the period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    method : str, optional
        method used for the calculation of the power spectral density graph, by default "ar"
    filtering_kwargs : dict, optional
        kwargs of the bbi filtering function for outliers and ectopic beats, by default {}
    method_kwargs : dict, optional
        kwargs needed for the method psd calculation, by default {}

    Returns
    -------
    :class:`dict`
        Dictionary with participant id as primary key,
        frequency-domain hrv feature names and method params as secondary keys,
        and the values of the features and params as dictionary values.
        In case the value is a list, the items are relative (in order) to vlf, lf, hf ranges.

    Raises
    ------
    KeyError
        if the method specified isn't available the function returns this error.
    """
    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            bbi = loader.load_garmin_device_bbi(user,start_date,end_date).bbi
            bbi = utils.filter_bbi(bbi, **filtering_kwargs)
            if method == "ar":
                fd_features = pyhrv.frequency_domain.ar_psd(
                    bbi, show=False, **method_kwargs
                ).as_dict()
            elif method == "welch":
                fd_features = pyhrv.frequency_domain.welch_psd(
                    bbi, show=False, **method_kwargs
                ).as_dict()
            elif method == "lomb":
                fd_features = pyhrv.frequency_domain.lomb_psd(
                    bbi, show=False, **method_kwargs
                ).as_dict()
            else:
                raise KeyError("method specified unknown.")
            plt.close()
            data_dict[user] = fd_features
        except:
            data_dict[user] = None

    return data_dict


def get_hrv_nonlinear_domain(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    dfa=True,
    sampen=False,
    filtering_kwargs={},
    poincare_kwargs={},
    sampen_kwargs={},
    dfa_kwargs={},
):
    """Get non linear domain heart rate variability features.

    This function returns a dictionary containing for every user of interest
    the non linear domain hrv features for the period of interest.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    dfa : bool, optional
        whether to calculate features associated to detrended fluctuation analysis (dta), by default True
    sampen : bool, optional
        whether to calculate sample entropy features, by default False
        Note that this should be done only for bbi data of a few minutes at most, as its calculation take long.
    filtering_kwargs : dict, optional
        kwargs of the bbi filtering function for outliers and ectopic beats, by default {}
    poincare_kwargs : dict, optional
        kwargs associated to the calculation of poincaré features, by default {}
    sampen_kwargs : dict, optional
        kwargs associated to the calculation of sample entropy features, by default {}
    dfa_kwargs : dict, optional
        kwargs associated to the calculation of detrended fluctuation analysis, by default {}

    Returns
    -------
    Dictionary with participant id as primary key,
    non linear domain hrv feature names as secondary keys,
    and the values of the features as dictionary values.
    """
    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            bbi = loader.load_garmin_device_bbi(user,start_date,end_date).bbi
            bbi = utils.filter_bbi(bbi, **filtering_kwargs)
            non_linear_features = {}
            non_linear_features |= pyhrv.nonlinear.poincare(
                bbi, show=False, **poincare_kwargs
            ).as_dict()
            plt.close()
            if dfa:
                non_linear_features |= pyhrv.nonlinear.dfa(
                    bbi, show=False, **dfa_kwargs
                ).as_dict()
                plt.close()
            if sampen:  # for long bbi series this takes a lot of time
                non_linear_features |= pyhrv.nonlinear.sample_entropy(
                    bbi, **sampen_kwargs
                ).as_dict()
            data_dict[user] = non_linear_features
        except:
            data_dict[user] = None

    return data_dict


def get_hrv_features(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    filtering_kwargs={},
    time_domain_kwargs={},
    frequency_domain_kwargs={},
    nonlinear_domain_kwargs={},
):
    """Compute all hrv features (time, frequency, and non-linear domain) for a given period.
    Can be extremely computationally intensive if the period is too long.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    filtering_kwargs : dict, optional
        kwargs of the bbi filtering function for outliers and ectopic beats, by default {}
    time_domain_kwargs : dict, optional
        kwargs associated to the calculation of time domain hrv features, by default {}
    frequency_domain_kwargs : dict, optional
        kwargs associated to the calculation of frequency domain hrv features, by default {}
    nonlinear_domain_kwargs : dict, optional
        kwargs associated to the calculation of non linear domain hrv features, by default {}

    Returns
    -------
    Dictionary with participant id as primary key,
    hrv feature names and params for their calculation as secondary keys,
    and the values of the features or the params as dictionary values.
    """
    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            features = {}
            features |= get_hrv_time_domain(
                loader,
                start_date,
                end_date,
                user,
                filtering_kwargs=filtering_kwargs,
                **time_domain_kwargs
            )[user]
            features |= get_hrv_frequency_domain(
                loader,
                start_date,
                end_date,
                user,
                filtering_kwargs=filtering_kwargs,
                **frequency_domain_kwargs
            )[user]
            features |= get_hrv_nonlinear_domain(
                loader,
                start_date,
                end_date,
                user,
                filtering_kwargs=filtering_kwargs,
                **nonlinear_domain_kwargs
            )[user]
            data_dict[user] = features
        except:
            data_dict[user] = None

    return data_dict


def get_night_rmssd(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    coverage=0.7,
    method="all night",
):
    """Compute rmssd metrics considering night data for the specified participants and period.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    coverage : float, optional
        the percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7
    method : str, optional
        method specifying how to filter bbi data in order to compute the night metric, by default "all night"

    Returns
    -------
    Dictionary with participants as primary key,
    dates as secondary keys, and rmssd computed overnight as values.
    """

    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            sleeping_timestamps = sleep.get_sleep_timestamps(
                loader, start_date, end_date, user
            )[user]
            daily_means = {}

            for date, (start_hour, end_hour) in sleeping_timestamps.items():
                bbi_df = loader.load_garmin_device_bbi(user, start_hour, end_hour)
                bbi_df = bbi_df.set_index("isoDate")
                
                if method == "filter awake": # this filters out bbi relative to awake periods during sleep
                    bbi_df = utils.filter_out_awake_bbi(loader,user,bbi_df,date)

                counts = bbi_df.resample('5min').bbi.count() 
                means = bbi_df.resample('5min').bbi.mean() 
                coverage_filter = (counts > (300/(means/1000)*coverage)).values
                ST_analysis = bbi_df.resample('5min').bbi.apply(lambda x: pyhrv.time_domain.rmssd(x)[0] if x.count() > 5 else 0)
                ST_analysis = ST_analysis.iloc[coverage_filter & (ST_analysis != 0).values]
                rmssd_values_daily = ST_analysis.values
                daily_mean = rmssd_values_daily.mean()
                daily_means[date] = round(daily_mean, 1)
            data_dict[user] = daily_means
        except:
            data_dict[user] = None

    return data_dict


def get_night_sdnn(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    coverage=0.7,
    method="all night",
):
    """Compute sdnn metrics considering night data for the specified participants and period.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    coverage : float, optional
        the percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7
    method : str, optional
        method specifying how to filter bbi data in order to compute the night metric, by default "all night"

    Returns
    -------
    Dictionary with participants as primary key,
    dates as secondary keys, and sdnn computed overnight as values.
    """

    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            sleeping_timestamps = sleep.get_sleep_timestamps(
                loader, start_date, end_date, user
            )[user]

            daily_means = {}

            for date, (start_hour, end_hour) in sleeping_timestamps.items():
                bbi_df = loader.load_garmin_device_bbi(user, start_hour, end_hour)
                bbi_df = bbi_df.set_index("isoDate")
                if method == "filter awake":
                    bbi_df = utils.filter_out_awake_bbi(loader,user,bbi_df,date)
                counts = bbi_df.resample('5min').bbi.count() 
                means = bbi_df.resample('5min').bbi.mean() 
                coverage_filter = (counts > (300/(means/1000)*coverage)).values
                ST_analysis = bbi_df.resample('5min').bbi.apply(lambda x: pyhrv.time_domain.sdnn(x)[0] if x.count() > 5 else 0)
                ST_analysis = ST_analysis.iloc[coverage_filter & (ST_analysis != 0).values]
                sdnn_values_daily = ST_analysis.values
                daily_mean = sdnn_values_daily.mean()
                daily_means[date] = round(daily_mean, 1)
            data_dict[user] = daily_means
        except:
            data_dict[user] = None

    return data_dict


def get_night_lf(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    coverage=0.7,
    method="all night",
    minimal_periods=10,
):
    """Compute LF power metrics considering night data for the specified participants and period.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    coverage : float, optional
        the percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7
    method : str, optional
        method specifying how to filter bbi data in order to compute the night metric, by default "all night"

    Returns
    -------
    Dictionary with participants as primary key,
    dates as secondary keys, and LF absolute power computed overnight as values.
    """
    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            sleeping_timestamps = sleep.get_sleep_timestamps(
                loader, start_date, end_date, user
            )[user]

            daily_means = {}

            for date, (start_hour, end_hour) in sleeping_timestamps.items():
                bbi_df = loader.load_garmin_device_bbi(user, start_hour, end_hour)
                bbi_df = bbi_df.set_index("isoDate")
                if method == "filter awake":
                    bbi_df = utils.filter_out_awake_bbi(loader,user,bbi_df,date)
                counts = bbi_df.resample('5min').bbi.count() 
                means = bbi_df.resample('5min').bbi.mean() 
                coverage_filter = (counts > (300/(means/1000)*coverage)).values
                ST_analysis = bbi_df.resample('5min').bbi.apply(lambda x: pyhrv.frequency_domain.welch_psd(nni=x,
                                                                                                           show=False,
                                                                                                           mode="dev")[0]["fft_abs"][1] if x.count() > 5 else 0)
                ST_analysis = ST_analysis.iloc[coverage_filter & (ST_analysis != 0).values]
                lf_values_daily = ST_analysis.dropna().values
                if len(lf_values_daily) >= minimal_periods:
                    daily_mean = lf_values_daily.mean()
                    daily_means[date] = round(daily_mean, 1)
            data_dict[user] = daily_means
        except:
            data_dict[user] = None

    return data_dict


def get_night_hf(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    coverage=0.7,
    method="all night",
    minimal_periods=10,
):
    """Compute HF power metrics considering night data for the specified participants and period.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all".
    coverage : float, optional
        the percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7
    method : str, optional
        method specifying how to filter bbi data in order to compute the night metric, by default "all night"

    Returns
    -------
    Dictionary with participants as primary key,
    dates as secondary keys, and LF absolute power computed overnight as values.
    """
    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            sleeping_timestamps = sleep.get_sleep_timestamps(
                loader, start_date, end_date, user
            )[user]

            daily_means = {}

            for date, (start_hour, end_hour) in sleeping_timestamps.items():
                bbi_df = loader.load_garmin_device_bbi(user, start_hour, end_hour)
                bbi_df = bbi_df.set_index("isoDate")
                if method == "filter awake":
                    bbi_df = utils.filter_out_awake_bbi(loader,user,bbi_df,date)
                counts = bbi_df.resample('5min').bbi.count() 
                means = bbi_df.resample('5min').bbi.mean() 
                coverage_filter = (counts > (300/(means/1000)*coverage)).values
                ST_analysis = bbi_df.resample('5min').bbi.apply(lambda x: pyhrv.frequency_domain.welch_psd(nni=x,
                                                                                                           show=False,
                                                                                                           mode="dev")[0]["fft_abs"][2] if x.count() > 5 else 0)
                ST_analysis = ST_analysis.iloc[coverage_filter & (ST_analysis != 0).values]
                hf_values_daily = ST_analysis.dropna().values
                if len(hf_values_daily) >= minimal_periods:
                    daily_mean = hf_values_daily.mean()
                    daily_means[date] = round(daily_mean, 1)
            data_dict[user] = daily_means
        except:
            data_dict[user] = None

    return data_dict


def get_night_lfhf(
    loader,
    start_date=None,
    end_date=None,
    user_id="all",
    coverage=0.7,
    method="all night",
):
    """Compute LF/HF ratio metrics considering night data for the specified participants and period.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.Loader`
        Initialized instance of data loader.
    start_date : :class:`datetime.datetime`, optional
        Start date of the period of interest, by default None
    end_date : :class:`datetime.datetime`, optional
        End date of the period of interest (inclusive), by default None.
    user_id : class:`str`, optional
        ID of the user(s) for which hrv features must be computed, by default "all"
    coverage : float, optional
        the percentage of expected bbi observations for a period to be considered in the analysis, by default 0.7
    method : str, optional
        method specifying how to filter bbi data in order to compute the night metric, by default "all night"

    Returns
    -------
    Dictionary with participants as primary key,
    dates as secondary keys, and LF/HF ratio computed overnight as values.
    """

    user_id = utils.get_user_ids(loader, user_id)
    data_dict = {}

    for user in user_id:
        try:
            lf_dict = get_night_lf(
                loader, start_date, end_date, user, coverage=coverage, method=method
            )[user]
            hf_dict = get_night_hf(
                loader, start_date, end_date, user, coverage=coverage, method=method
            )[user]
            lfhf_dict = {}
            for date in lf_dict.keys():
                lf = lf_dict[date]
                hf = hf_dict[date]
                lfhf_dict[date] = lf / hf

            data_dict[user] = lfhf_dict
        except:
            data_dict[user] = None

    return data_dict
  