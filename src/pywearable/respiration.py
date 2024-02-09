"""
This module contains all the functions related to analysis
of respiration data.
"""

# TODO find more efficient way to get sleep timestamps

import datetime
from typing import Union

import numpy as np
import pandas as pd

from . import constants, loader, utils

_RESPIRATION_METRIC_MEAN_PULSE_OX = "meanPulseOx"
_RESPIRATION_METRIC_P10_PULSE_OX = "p10PulseOx"
_RESPIRATION_METRIC_P20_PULSE_OX = "p20PulseOx"
_RESPIRATION_METRIC_P30_PULSE_OX = "p30PulseOx"
_RESPIRATION_METRIC_MEAN_AWAKE_BREATHS_PER_MINUTE = "meanAwakeBreathsPerMinute"
_RESPIRATION_METRIC_MEAN_REST_BREATHS_PER_MINUTE = "meanRestBreathsPerMinute"


def get_mean_rest_pulse_ox(
    loader: loader.BaseLoader,
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
    """Get mean pulse ox value at rest.

    This function computes the mean pulse ox value during
    resting sleep periods for the given ``user_id``
    and for the required time interval from ``start_date`` to
    ``end_date``. It is also possible to perform a
    transformation of the retrieved mean pulse ox values
    by setting the ``kind`` parameter to a valid function
    accepted by :func:`~pandas.Series.agg`. For example, it is
    possible to obtain the mean of the mean values by
    setting the ``kind`` parameter to ``"mean"``. If the
    ``kind`` argument requires additional positional
    arguments or keyword arguments, it is possible to set them
    by passing them to the ``kind_args`` and
    ``kind_kwargs`` arguments.
    The function used to load pulse_ox data is the
    :func:`~loader.BaseLoader.load_sleep_pulse_ox`. If
    loader-specific arguments are required, you can
    pass them using the ``loader_kwargs`` argument.
    The return type depends on the

    Parameters
    ----------
    loader : :class:`loader.BaseLoader`
        Initialized data loader, that must implement the method
        ``load_sleep_pulse_ox(user_id, start_date, end_date).
    user_id : :class:`str` or :class:`list` or `None`, optional
        User id for which the metric must be computed, by default ``"all"``.
        If the parameter is set to ``"all"``, then the ``loader`` must implement the function
        ``get_user_ids()`` in order to retrieve the list of user ids to
        use for the metric computation.
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        Start date for the computation of the metric, by default ``None``.
        If ``None`` is used as a value for the parameter, then the ``start_date`` will
        be specific for each user, depending on the first date with
        available data for the user.
        ``start_date`` is converted to a :class:`datetime.date`, so
        the first returned value will be related to the sleep occuring
        on the night starting the day before ``start_date``.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        End date for the computation of the metric, by default ``None``.
        If ``None`` is used as a value for the parameter, then the ``end_date`` will be specific
        for each user, depending on the first date with available data for the user.
        ``end_date`` is converted to a :class:`datetime.date`, so the
        last returned value will be related to sleep occuring on the night
        starting the day before ``end_date``.
    kind : :class:`str` or ``None``, optional
        Additional transformation to be performed on the metric, by default ``None``.
    kind_args : :class:`list`, optional
        Additional positional arguments to be passed to the function used
        by the ``kind`` method, by default ``[]``
    kind_kwargs : :class:`dict`, optional
        Additional keyword arguments to be passed to the function used by the ``kind``
        method, by default no additional keywords arguments are passed.
    loader_kwargs: :class:`dict`
        Keyword arguemnts for the ``load_sleep_pulse_ox`` loading function of the ``loader``,
        by default no keyword arguments are passed.
    return_dict: :class:`bool`
        Whether to return a :class:`dict` or a :class:`pd.DataFrame`

    Returns
    -------
    :class:`dict` or :class:`pd.DataFrame`
        the return type can be:
            - :class:`dict` if ``return_df`` is ``False``
            - :class:`pd.DataFrame` if ``return_df`` is ``True``. The returned :class:`pd.DataFrame` will
              have a index of type :class:`pd.MultiIndex` if ``return_multi_index`` is set to
              ``True``, with the levels of the index being ``"user"`` and ``"calendarDate"``. If
              ``return_multi_index`` is set to ``False``, then the returned :class:`pd.DataFrame`
              will have a standard :class:`pd.RangeIndex` and ``"user"`` and ``"calenderDate"``
              will be two colums of the returned :class:`pd.DataFrame`.
    """
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_MEAN_PULSE_OX,
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


def get_p10_rest_pulse_ox(
    loader: loader.BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = False,
):
    """Get 10th percentile pulse ox value at rest.

    This function computes the 10-th percentile of
    pulse ox value during resting sleep periods for the given
    ``user_id`` and for the required time interval from ``start_date`` to
    ``end_date``.
    It is also possible to perform a
    transformation of the retrieved p10 values
    by setting the ``kind`` parameter to a valid function
    accepted by :func:`~pandas.Series.agg`. For example, it is
    possible to obtain the mean of the mean values by
    setting the ``kind`` parameter to ``"mean"``. If the
    ``kind`` argument requires additional positional
    arguments or keyword arguments, it is possible to set them
    by passing them to the ``kind_args`` and
    ``kind_kwargs`` arguments.
    The function used to load pulse_ox data is the
    :func:`~loader.BaseLoader.load_sleep_pulse_ox`. If
    loader-specific arguments are required, you can
    pass them using the ``loader_kwargs`` argument
    in a :class:`dict` format.

    Parameters
    ----------
    loader : :class:`loader.BaseLoader`
        Initialized data loader
    user_id : :class:`str` or :class:`list` or `None`, optional
        User id for which the metric must be computed, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        Start date for the computation of the metric, by default ``None``
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        End date for the computation of the metric, by default ``None``
    kind : :class:`str` or ``None``, optional
        Additional transformation to be performed on the metric, by default ``None``
    kind_args : :class:`tuple` or :class:`list`, optional
        Additional positional arguments to be passed to the function used
        by the ``kind`` method, by default None
    kind_kwargs : :class:`dict`, optional
        Additional keyword to be passed to the function used by the ``kind`` method, by default None
    loader_kwargs: :class:`dict`
        Keyword arguemnts for the ``load_sleep_pulse_ox`` loading function of the ``loader``
    return_dict: :class:`bool`
        Whether to return a :class:`dict` or a :class:`pd.DataFrame`

    Returns
    -------
    :class:`dict` or :class:`pd.DataFrame`
        the return type can be:
            - :class:`dict` if ``return_dict`` is ``True``
            - :class:`pd.DataFrame` if ``return_dict`` is ``False``
    """
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_P10_PULSE_OX,
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


def get_p20_rest_pulse_ox(
    loader: loader.BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = False,
):
    """Get 20th percentile pulse ox value at rest.

    This function computes the 20-th percentile of
    pulse ox value during resting sleep periods for the given
    ``user_id`` and for the required time interval from ``start_date`` to
    ``end_date``.
    It is also possible to perform a
    transformation of the retrieved p20 values
    by setting the ``kind`` parameter to a valid function
    accepted by :func:`~pandas.Series.agg`. For example, it is
    possible to obtain the mean of the mean values by
    setting the ``kind`` parameter to ``"mean"``. If the
    ``kind`` argument requires additional positional
    arguments or keyword arguments, it is possible to set them
    by passing them to the ``kind_args`` and
    ``kind_kwargs`` arguments.
    The function used to load pulse_ox data is the
    :func:`~loader.BaseLoader.load_sleep_pulse_ox`. If
    loader-specific arguments are required, you can
    pass them using the ``loader_kwargs`` argument
    in a :class:`dict` format.

    Parameters
    ----------
    loader : :class:`loader.BaseLoader`
        Initialized data loader
    user_id : :class:`str` or :class:`list` or `None`, optional
        User id for which the metric must be computed, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        Start date for the computation of the metric, by default ``None``
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        End date for the computation of the metric, by default ``None``
    kind : :class:`str` or ``None``, optional
        Additional transformation to be performed on the metric, by default ``None``
    kind_args : :class:`tuple` or :class:`list`, optional
        Additional positional arguments to be passed to the function used
        by the ``kind`` method, by default None
    kind_kwargs : :class:`dict`, optional
        Additional keyword to be passed to the function used by the ``kind`` method, by default None
    loader_kwargs: :class:`dict`
        Keyword arguemnts for the ``load_sleep_pulse_ox`` loading function of the ``loader``
    return_dict: :class:`bool`
        Whether to return a :class:`dict` or a :class:`pd.DataFrame`

    Returns
    -------
    :class:`dict` or :class:`pd.DataFrame`
        the return type can be:
            - :class:`dict` if ``return_dict`` is ``True``
            - :class:`pd.DataFrame` if ``return_dict`` is ``False``
    """
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_P20_PULSE_OX,
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


def get_p30_rest_pulse_ox(
    loader: loader.BaseLoader,
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
    """Get 30th percentile pulse ox value at rest.

    This function computes the 30-th percentile of
    pulse ox value during resting sleep periods for the given
    ``user_id`` and for the required time interval from ``start_date`` to
    ``end_date``.
    It is also possible to perform a
    transformation of the retrieved p30 values
    by setting the ``kind`` parameter to a valid function
    accepted by :func:`~pandas.Series.agg`. For example, it is
    possible to obtain the mean of the mean values by
    setting the ``kind`` parameter to ``"mean"``. If the
    ``kind`` argument requires additional positional
    arguments or keyword arguments, it is possible to set them
    by passing them to the ``kind_args`` and
    ``kind_kwargs`` arguments.
    The function used to load pulse_ox data is the
    :func:`~loader.BaseLoader.load_sleep_pulse_ox`. If
    loader-specific arguments are required, you can
    pass them using the ``loader_kwargs`` argument
    in a :class:`dict` format.

    Parameters
    ----------
    loader : :class:`loader.BaseLoader`
        Initialized data loader
    user_id : :class:`str` or :class:`list` or `None`, optional
        User id for which the metric must be computed, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        Start date for the computation of the metric, by default ``None``
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        End date for the computation of the metric, by default ``None``
    kind : :class:`str` or ``None``, optional
        Additional transformation to be performed on the metric, by default ``None``
    kind_args : :class:`tuple` or :class:`list`, optional
        Additional positional arguments to be passed to the function used
        by the ``kind`` method, by default None
    kind_kwargs : :class:`dict`, optional
        Additional keyword to be passed to the function used by the ``kind`` method, by default None
    loader_kwargs: :class:`dict`
        Keyword arguemnts for the ``load_sleep_pulse_ox`` loading function of the ``loader``
    return_dict: :class:`bool`
        Whether to return a :class:`dict` or a :class:`pd.DataFrame`

    Returns
    -------
    :class:`dict` or :class:`pd.DataFrame`
        the return type can be:
            - :class:`dict` if ``return_dict`` is ``True``
            - :class:`pd.DataFrame` if ``return_dict`` is ``False``
    """
    return get_rest_pulse_ox_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_P30_PULSE_OX,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_dict=return_df,
        return_multi_index=return_multi_index,
    )


def _compute_mean_rest_pulse_ox(rest_pulse_ox: pd.DataFrame) -> pd.Series:
    return _compute_rest_pulse_ox_statistic(rest_pulse_ox, "mean")


def _compute_p10_rest_pulse_ox(rest_pulse_ox: pd.DataFrame) -> pd.Series:
    return _compute_rest_pulse_ox_statistic(rest_pulse_ox, np.percentile, 10)


def _compute_p20_rest_pulse_ox(rest_pulse_ox: pd.DataFrame) -> pd.Series:
    return _compute_rest_pulse_ox_statistic(rest_pulse_ox, np.percentile, 20)


def _compute_p30_rest_pulse_ox(rest_pulse_ox: pd.DataFrame) -> pd.Series:
    return _compute_rest_pulse_ox_statistic(rest_pulse_ox, np.percentile, 30)


def _compute_rest_pulse_ox_statistic(
    rest_pulse_ox: pd.DataFrame,
    agg,
    *agg_args,
    **agg_kwargs,
) -> pd.Series:
    if type(rest_pulse_ox) != pd.DataFrame:
        raise ValueError(
            f"rest_pulse_ox must be of type pd.DataFrame and not {type(rest_pulse_ox)}"
        )
    if constants._CALENDAR_DATE_COL not in rest_pulse_ox.columns:
        raise ValueError(
            f"{constants._CALENDAR_DATE_COL} not found among rest_pulse_ox columns {rest_pulse_ox.columns}"
        )
    if constants._SPO2_SPO2_COL not in rest_pulse_ox.columns:
        raise ValueError(
            f"{constants._SPO2_SPO2_COL} not found among rest_pulse_ox columns {rest_pulse_ox.columns}"
        )
    agg_series = rest_pulse_ox.groupby(constants._CALENDAR_DATE_COL)[
        constants._SPO2_SPO2_COL
    ].agg(agg, *agg_args, **agg_kwargs)
    return agg_series


_REST_PULSE_OX_STATISTICS_DICT = {
    _RESPIRATION_METRIC_MEAN_PULSE_OX: _compute_mean_rest_pulse_ox,
    _RESPIRATION_METRIC_P10_PULSE_OX: _compute_p10_rest_pulse_ox,
    _RESPIRATION_METRIC_P20_PULSE_OX: _compute_p20_rest_pulse_ox,
    _RESPIRATION_METRIC_P30_PULSE_OX: _compute_p30_rest_pulse_ox,
}


def get_rest_pulse_ox_statistic(
    loader: loader.BaseLoader,
    metric: Union[str, list, tuple, None] = None,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: str = None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
    """Get a rest pulse ox statistic.

    This function computes a statistic of
    pulse ox value during resting sleep periods for the given
    ``user_id`` and for the required time interval from ``start_date`` to
    ``end_date``.
    It is also possible to perform a
    transformation of the retrieved statistic
    by setting the ``kind`` parameter to a valid function
    accepted by :func:`~pandas.Series.agg`. For example, it is
    possible to obtain the mean of the mean values by
    setting the ``kind`` parameter to ``"mean"``. If the
    ``kind`` argument requires additional positional
    arguments or keyword arguments, it is possible to set them
    by passing them to the ``kind_args`` and
    ``kind_kwargs`` arguments.
    The function used to load pulse_ox data is the
    :func:`~loader.BaseLoader.load_sleep_pulse_ox`. If
    loader-specific arguments are required, you can
    pass them using the ``loader_kwargs`` argument
    in a :class:`dict` format.

    Parameters
    ----------
    loader : :class:`loader.BaseLoader`
        Initialized data loader
    metric : :class:`str`
        The statistic that needs to be computed. Available options are:

            - ``"meanPulseOx"``
            - ``"p10PulseOx"``
            - ``"p20PulseOx"``
            - ``"p30PulseOx"``

    user_id : :class:`str` or :class:`list` or `None`, optional
        User id for which the metric must be computed, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        Start date for the computation of the metric, by default ``None``
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or `None`, optional
        End date for the computation of the metric, by default ``None``
    kind : :class:`str` or function, optional
        Additional transformation to be performed on the metric, by default ``None``
    kind_args : :class:`list`, optional
        Additional positional arguments to be passed to the function used
        by the ``kind`` method, by default None
    kind_kwargs : :class:`dict`, optional
        Additional keyword arguments to be passed to the function used by the ``kind`` method, by default None
    loader_kwargs: :class:`dict`
        Keyword arguemnts for the ``load_sleep_pulse_ox`` loading function of the ``loader``
    return_dict: :class:`bool`
        Whether to return a :class:`dict` or a :class:`pd.DataFrame`

    Returns
    -------
    :class:`dict` or :class:`pd.DataFrame`
        the return type can be:
            - :class:`dict` if ``return_dict`` is ``True``
            - :class:`pd.DataFrame` if ``return_dict`` is ``False``
    """
    return get_rest_pulse_ox_statistics(
        loader=loader,
        metrics=metric,
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


def get_rest_pulse_ox_statistics(
    loader: loader.BaseLoader,
    metrics: Union[str, list, tuple, None] = None,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    kind: Union[str, None] = None,
    kind_args=[],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
    """Get rest pulse ox statistics.

    This function returns a rest pulse ox statistics for each day. Depending on the value
    of the ``kind`` parameter, the function returns a statistic for rest pulse ox data.
    The value of the ``kind`` parameter can be any value that is accepted by
    a transform operation by pandas. By default, the function returns the ``mean``
    pulse ox at rest.

    Parameters
    ----------
    loader: :class:`pywearable.loader.BaseLoader`
        Instance of a data loader.
    metrics: :class:`str` or :class:`list`
        List of rest pulse ox statistic(s) that needs to be retrived. Available options are:

            - ``"meanPulseOx"``
            - ``"p10PulseOx"``
            - ``"p20PulseOx"``
            - ``"p30PulseOx"``
            - ``None``: compute all statistics

    user_id: :class:`str`, optional
        Unique identifier of the user for which pulse ox statistics must be computed, by default ``"all"``.
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
    kind : :class:`str` or function, optional
        Additional transformation to be performed on the metric, by default ``None``
    kind_args : :class:`list`, optional
        Additional positional arguments to be passed to the function used
        by the ``kind`` method, by default None
    kind_kwargs : :class:`dict`, optional
        Additional keyword arguments to be passed to the function used by the ``kind`` method, by default None
    loader_kwargs: :class:`dict`
        Keyword arguemnts for the ``load_sleep_pulse_ox`` loading function of the ``loader``
    return_dict: :class:`bool`
        Whether to return a :class:`dict` or a :class:`pd.DataFrame`

    Returns
    -------
    :class:`dict` or :class:`pd.DataFrame`
        the return type can be:
            - :class:`dict` if ``return_dict`` is ``True``
            - :class:`pd.DataFrame` if ``return_dict`` is ``False``
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
    # Check metrics
    if metrics is None:
        # Consider all metrics
        metrics = list(_REST_PULSE_OX_STATISTICS_DICT.keys())
    if type(metrics) == str:
        metrics = [metrics]

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
        rest_pulse_ox_stat_df = pd.DataFrame(index=multi_index, columns=metrics)
        both_dates_valid = True
    else:
        # Set up a standard df and we will populate it later with indexes
        rest_pulse_ox_stat_df = pd.DataFrame()
    for user in user_id:
        if not (both_dates_valid):
            user_rest_pulse_ox_stat_df = pd.DataFrame()
        rest_pulse_ox = loader.load_sleep_pulse_ox(
            user_id=user,
            start_date=ext_start_date,
            end_date=ext_end_date,
            **loader_kwargs,
        )
        if len(rest_pulse_ox) > 0:
            # Get only data with calendar date between start and end date and reset index
            if not (start_date is None):
                rest_pulse_ox = rest_pulse_ox[
                    rest_pulse_ox[constants._CALENDAR_DATE_COL] >= start_date
                ].reset_index(drop=True)
            if not (end_date is None):
                rest_pulse_ox = rest_pulse_ox[
                    rest_pulse_ox[constants._CALENDAR_DATE_COL] <= end_date
                ].reset_index(drop=True)
            for metric in metrics:
                # Get series with metrics by calendarDate
                ser = _REST_PULSE_OX_STATISTICS_DICT[metric](
                    rest_pulse_ox=rest_pulse_ox
                )
                if both_dates_valid:
                    rest_pulse_ox_stat_df.loc[(user, ser.index), metric] = ser.values
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
                        ).rename(metric)
                        if len(user_rest_pulse_ox_stat_df) == 0:
                            # Empty df, first metric
                            user_rest_pulse_ox_stat_df = ser.to_frame()
                        else:
                            user_rest_pulse_ox_stat_df = pd.merge(
                                user_rest_pulse_ox_stat_df,
                                ser,
                                left_index=True,
                                right_index=True,
                                how="outer",
                            )
            if not both_dates_valid:
                rest_pulse_ox_stat_df = pd.concat(
                    (rest_pulse_ox_stat_df, user_rest_pulse_ox_stat_df)
                )
    # Perform kind operation by user
    if not (kind is None):
        rest_pulse_ox_stat_df = rest_pulse_ox_stat_df.groupby(
            level=constants._USER_COL
        ).agg(kind, *kind_args, **kind_kwargs)
    # Return based on settings
    return utils.return_multiindex_df(
        rest_pulse_ox_stat_df, return_df, return_multi_index
    )


def get_mean_rest_breaths_per_minute(
    loader: loader.BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, None] = None,
    end_date: Union[datetime.datetime, datetime.date, None] = None,
    remove_zero: bool = False,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
    """Get mean rest breaths per minute.

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
    return get_breaths_per_minute_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_MEAN_REST_BREATHS_PER_MINUTE,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        remove_zero=remove_zero,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_mean_awake_breaths_per_minute(
    loader: loader.BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, None] = None,
    end_date: Union[datetime.datetime, datetime.date, None] = None,
    remove_zero: bool = False,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
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
    return get_breaths_per_minute_statistic(
        loader=loader,
        metric=_RESPIRATION_METRIC_MEAN_AWAKE_BREATHS_PER_MINUTE,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        remove_zero=remove_zero,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def _compute_mean_rest_breaths_per_minute(
    awake_breaths_per_minute, rest_breaths_per_minute
):
    return _compute_breaths_per_minute_statistic(rest_breaths_per_minute, agg="mean")


def _compute_mean_awake_breaths_per_minute(
    awake_breths_per_minute, rest_breaths_per_minute
):
    return _compute_breaths_per_minute_statistic(awake_breths_per_minute, agg="mean")


def _compute_breaths_per_minute_statistic(
    breaths_per_minute: pd.DataFrame,
    agg,
    *agg_args,
    **agg_kwargs,
) -> pd.Series:
    if type(breaths_per_minute) != pd.DataFrame:
        raise ValueError(
            f"breaths_per_minute must be of type pd.DataFrame and not {type(breaths_per_minute)}"
        )
    if constants._CALENDAR_DATE_COL not in breaths_per_minute.columns:
        return pd.Series()
    if constants._RESPIRATION_BREATHS_PER_MINUTE_COL not in breaths_per_minute.columns:
        return pd.Series()
    agg_series = breaths_per_minute.groupby(constants._CALENDAR_DATE_COL)[
        constants._RESPIRATION_BREATHS_PER_MINUTE_COL
    ].agg(agg, *agg_args, **agg_kwargs)
    return agg_series


_BREATHS_PER_MINUTE_STATISTICS_DICT = {
    _RESPIRATION_METRIC_MEAN_REST_BREATHS_PER_MINUTE: _compute_mean_rest_breaths_per_minute,
    _RESPIRATION_METRIC_MEAN_AWAKE_BREATHS_PER_MINUTE: _compute_mean_awake_breaths_per_minute,
}


def get_breaths_per_minute_statistic(
    loader: loader.BaseLoader,
    metric: str,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    remove_zero: bool = False,
    kind=None,
    kind_args: list = [],
    kind_kwargs: dict = {},
    loader_kwargs: dict = {},
    return_df: bool = True,
    return_multi_index: bool = True,
):
    return get_breaths_per_minute_statistics(
        loader=loader,
        metrics=metric,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        remove_zero=remove_zero,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=return_df,
        return_multi_index=return_multi_index,
    )


def get_breaths_per_minute_statistics(
    loader: loader.BaseLoader,
    metrics: Union[str, list] = None,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    remove_zero: bool = False,
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
    if metrics is None:
        # Consider all metrics
        metrics = list(_BREATHS_PER_MINUTE_STATISTICS_DICT.keys())
    if type(metrics) == str:
        metrics = [metrics]

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
            [user_id, date_periods], names=["user", constants._CALENDAR_DATE_COL]
        )
        breaths_per_minute_stats_df = pd.DataFrame(index=multi_index, columns=metrics)
        both_dates_valid = True
    else:
        breaths_per_minute_stats_df = pd.DataFrame()
    for user in user_id:
        if not (both_dates_valid):
            user_breaths_per_minute_stats_df = pd.DataFrame()
        breaths_per_minute = loader.load_respiration(
            user_id=user,
            start_date=start_date,
            end_date=end_date,
            **loader_kwargs,
        )
        # Load daily respiration
        if len(breaths_per_minute) > 0:
            # Get only data when no sleeping is occurring
            breaths_per_minute = breaths_per_minute[
                breaths_per_minute[constants._IS_SLEEPING_COL] == False
            ].reset_index(drop=True)
            # Add calendar Date information
            breaths_per_minute[constants._CALENDAR_DATE_COL] = breaths_per_minute[
                constants._ISODATE_COL
            ].dt.normalize()
            if remove_zero:
                breaths_per_minute = breaths_per_minute[
                    breaths_per_minute[constants._RESPIRATION_BREATHS_PER_MINUTE_COL]
                    > 0
                ].reset_index(drop=True)
        # Load sleep respiration
        rest_breaths_per_minute = loader.load_sleep_respiration(
            user_id=user,
            start_date=ext_start_date,
            end_date=ext_end_date,
            **loader_kwargs,
        )
        if len(rest_breaths_per_minute) > 0:
            # Get only data with calendar date between start and end date and reset index
            if not (start_date is None):
                rest_breaths_per_minute = rest_breaths_per_minute[
                    rest_breaths_per_minute[constants._CALENDAR_DATE_COL] >= start_date
                ].reset_index(drop=True)
            if not (end_date is None):
                rest_breaths_per_minute = rest_breaths_per_minute[
                    rest_breaths_per_minute[constants._CALENDAR_DATE_COL] <= end_date
                ].reset_index(drop=True)
            if remove_zero:
                rest_breaths_per_minute = rest_breaths_per_minute[
                    rest_breaths_per_minute[
                        constants._RESPIRATION_BREATHS_PER_MINUTE_COL
                    ]
                    > 0
                ].reset_index(drop=True)
        for metric in metrics:
            # Get series with metrics by calendarDate
            ser = _BREATHS_PER_MINUTE_STATISTICS_DICT[metric](
                breaths_per_minute, rest_breaths_per_minute
            )
            if both_dates_valid:
                breaths_per_minute_stats_df.loc[(user, ser.index), metric] = ser.values
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
                            names=[constants._USER_COL, constants._CALENDAR_DATE_COL],
                        )
                    ).rename(metric)
                    if len(user_breaths_per_minute_stats_df) == 0:
                        # Empty df, first metric
                        user_breaths_per_minute_stats_df = ser.to_frame()
                    else:
                        user_breaths_per_minute_stats_df = pd.merge(
                            user_breaths_per_minute_stats_df,
                            ser,
                            left_index=True,
                            right_index=True,
                            how="outer",
                        )
        if not both_dates_valid:
            breaths_per_minute_stats_df = pd.concat(
                (breaths_per_minute_stats_df, user_breaths_per_minute_stats_df)
            )
    # Perform kind operation by user
    if not (kind is None):
        breaths_per_minute_stats_df = breaths_per_minute_stats_df.groupby(
            level="user"
        ).agg(kind, *kind_args, **kind_kwargs)
    return utils.return_multiindex_df(
        breaths_per_minute_stats_df, return_df, return_multi_index
    )


def get_respiration_statistics(
    loader: loader.BaseLoader,
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
    """_summary_

    _extended_summary_

    Parameters
    ----------
    loader : loader.BaseLoader
        _description_
    user_id : Union[str, list], optional
        _description_, by default "all"
    start_date : Union[datetime.datetime, datetime.date, str, None], optional
        _description_, by default None
    end_date : Union[datetime.datetime, datetime.date, str, None], optional
        _description_, by default None
    kind : _type_, optional
        _description_, by default None
    kind_args : list, optional
        _description_, by default []
    kind_kwargs : dict, optional
        _description_, by default {}
    loader_kwargs : dict, optional
        _description_, by default {}
    return_df : bool, optional
        _description_, by default True
    return_multi_index : bool, optional
        _description_, by default True

    Returns
    -------
    _type_
        _description_
    """
    rest_pulse_ox_statistics = get_rest_pulse_ox_statistics(
        loader=loader,
        metrics=None,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=True,
        return_multi_index=True,
    )
    breaths_per_minute_statistics = get_breaths_per_minute_statistics(
        loader=loader,
        metrics=None,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        kind=kind,
        kind_args=kind_args,
        kind_kwargs=kind_kwargs,
        loader_kwargs=loader_kwargs,
        return_df=True,
        return_multi_index=True,
    )
    respiration_statistics_df = pd.merge(
        left=rest_pulse_ox_statistics,
        right=breaths_per_minute_statistics,
        right_index=True,
        left_index=True,
        how="outer",
    )
    return utils.return_multiindex_df(
        respiration_statistics_df, return_df, return_multi_index
    )
