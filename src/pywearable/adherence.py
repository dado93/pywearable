"""
This module contains all the functions related to the analysis
of Labfront adherence.
"""


import datetime
from typing import Union

import pandas as pd

from . import constants, utils
from .loader.base import BaseLoader

_LABFRONT_TASK_SCHEDULE_KEY = "taskScheduleRepeat"
_LABFRONT_TODO_STRING = "todo"
_LABFRONT_GARMIN_CONNECT_CALENDAR_DAY_COL = "calendarDate"
_MS_TO_HOURS_CONVERSION = 1000 * 60 * 60


def get_questionnaire_dict(
    loader: BaseLoader,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    questionnaire: str = "all",
    safe_delta: int = 6,
):
    """Get total number of filled questionnaire in the given timeframe.

    This function returns the total number of filled questionnaire
    for the given user(s) in the selected timeframe. This adherence
    is returned in dictionary format::

        {
            'WRSD-PMI-BO-01_4a520aea-12d9-4513-8a0c-3055d399b097': {
                'questionario mattutino': {
                    'n_filled': 28,
                    'taskScheduleRepeat': True
                }
            },
            'WRSD-PMI-BO-02_56453d1a-7101-4f6e-95c3-ba5caee88cad': {
                'questionario mattutino': {
                    'n_filled': 9,
                    'taskScheduleRepeat': True
                }
            }
        }


    Parameters
    ----------
    loader : :class:`loader.BaseLoader`
        Instance of :class:`loader.BaseLoader`.
    user_id : :class:`str` or :class:`list`, optional
        Id(s) of user(s) for which adherence has to be computed, by default "all"
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for questionnaire adherence, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for questionnaire adherence, by default None
    questionnaire : :class:`str`, optional
        Questionnaire of interest, by default "all"
    safe_delta : :class:`int`, optional
        Amount of hours needed to consider valid two successive filled questionnaires, by default 6

    Returns
    -------
    :class:`dict`
        Dictionary with user_id as key, then a nested dictionary
        with questionnaire name as key, and number of filled
        questionnaires (`n_filled`) and `taskScheduleRepeat`
        as keys with their correspondent values.
    """

    adherence_dict = {}

    user_id = utils.get_user_ids(loader, user_id)

    if questionnaire == "all":
        questionnaire = loader.get_available_questionnaires()
    elif isinstance(questionnaire, str):
        questionnaire = [loader.get_task_full_id(questionnaire)]

    if not (isinstance(user_id, list) and isinstance(questionnaire, list)):
        raise TypeError("user id and questionnaire_names have to be lists.")

    inv_map = {v: k for k, v in loader.tasks_dict.items()}

    for user in user_id:
        adherence_dict[user] = {}
        participant_questionnaires = loader.get_available_questionnaires([user])
        for quest in questionnaire:
            questionnaire_name = inv_map[quest]
            adherence_dict[user][questionnaire_name] = {}
            if quest in participant_questionnaires:
                questionnaire_df = loader.load_questionnaire(
                    user_id=user,
                    start_date=start_date,
                    end_date=end_date,
                    questionnaire_name=questionnaire_name,
                )
                timestamps = questionnaire_df[constants._UNIXTIMESTAMP_IN_MS_COL]
                count = 0
                for i in range(len(timestamps)):
                    if (
                        i == 0
                        or timestamps[i] - timestamps[i - 1]
                        > _MS_TO_HOURS_CONVERSION * safe_delta
                    ):
                        count += 1
                adherence_dict[user][questionnaire_name]["n_filled"] = count
                is_repeatable = utils.is_task_repeatable(
                    (
                        loader.data_path
                        / loader.get_full_id(user)
                        / constants._QUESTIONNAIRE_FOLDER
                        / quest
                    )
                )
                adherence_dict[user][questionnaire_name][
                    constants._TASK_SCHEDULE_COL
                ] = is_repeatable
            else:
                adherence_dict[user][questionnaire_name]["n_filled"] = 0
                # need to understand if the questionnaire is repeatable
                # we do this by iterating through all users
                is_repeatable = None
                for full_user in loader.get_full_ids():
                    try:
                        is_repeatable = utils.is_task_repeatable(
                            (
                                loader.data_path
                                / full_user
                                / constants._QUESTIONNAIRE_FOLDER
                                / quest
                            )
                        )
                    except:
                        pass
                    else:
                        break
                adherence_dict[user][questionnaire_name][
                    constants._TASK_SCHEDULE_COL
                ] = is_repeatable

    return adherence_dict


def get_questionnaire_adherence(
    loader: BaseLoader,
    number_of_days: int,
    user_id: Union[str, list] = "all",
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    questionnaire_names="all",
    safe_delta=6,
    return_percentage=True,
):
    """Returns adherence of the user(s) for the questionnaire(s).

    This function assumes daily adherence is necessary for repetitive questionnaires.

    Parameters
    ----------
        loader: :class:`pylabfront.loader.LabfrontLoader`
            Instance of `LabfrontLoader`.
        number_of_days: :class:`int`
            Total number of days over which adherence must be computed.
        user_id: :class:`list` or :class:`str`, optional
            List of the user IDs of interest, by default "all".
        start_date: :class:`datetime.datetime`, optional
            Start date from which data have to be extracted, by default None.
        end_date: :class:`datetime.datetime`, optional
            End date from which data have to be extracted, by default None.
        questionnaire_names: :class:`list`, optional
            List of the questionnaires of interest, by default "all".
        safe_delta: :class:`int`, optional
            Amount of hours needed to consider two successive filled questionnaires valid, by default 6.
        return_percentage: :class:`bool`, optional
            Whether to return data as percentage (True) or as absolute values.

    Returns
    -------
        :class:`dict`
            Adherence dictionary containing the percentages of adherence
            with respect to the requirements for the questionnaires and
            users of interest.
    """

    questionnaire_adherence = {}

    questionnaire_dict = get_questionnaire_dict(
        loader, start_date, end_date, user_id, questionnaire_names, safe_delta
    )
    for participant_id in questionnaire_dict.keys():
        questionnaire_adherence[participant_id] = {}
        for questionnaire in questionnaire_dict[participant_id].keys():
            if questionnaire_dict[participant_id][questionnaire][
                _LABFRONT_TASK_SCHEDULE_KEY
            ]:
                # It is a repeated task
                if return_percentage:
                    questionnaire_adherence[participant_id][questionnaire] = round(
                        (
                            questionnaire_dict[participant_id][questionnaire][
                                "n_filled"
                            ]
                            / number_of_days
                        )
                        * 100,
                        2,
                    )
                else:
                    questionnaire_adherence[participant_id][questionnaire] = {}
                    questionnaire_adherence[participant_id][questionnaire][
                        "total"
                    ] = number_of_days
                    questionnaire_adherence[participant_id][questionnaire][
                        "n_filled"
                    ] = questionnaire_dict[participant_id][questionnaire]["n_filled"]

            else:
                # it's not a repeated task - or it has never been filled
                if return_percentage:
                    questionnaire_adherence[participant_id][questionnaire] = (
                        questionnaire_dict[participant_id][questionnaire]["n_filled"]
                        == 1
                    ) * 100
                else:
                    questionnaire_adherence[participant_id][questionnaire] = {}
                    questionnaire_adherence[participant_id][questionnaire]["total"] = 1
                    questionnaire_adherence[participant_id][questionnaire][
                        "n_filled"
                    ] = questionnaire_dict[participant_id][questionnaire]["n_filled"]

    return questionnaire_adherence


def get_todo_dict(
    loader: BaseLoader,
    start_date=None,
    end_date=None,
    user_id="all",
    todo_names="all",
    safe_delta=6,
):
    """
    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list):  IDs of participants. Defaults to "all".
        todo_names (list): Name of the todos. Defaults to "all".
        safe_delta (int): Amount of hours needed to consider two successive filled todos valid. Defaults to 6.

    Returns:
        dict: Dictionary with adherence data for the participants and todo required.
    """

    adherence_dict = {}

    if user_id == "all":
        user_id = loader.get_user_ids()

    if todo_names == "all":
        todo_names = loader.get_available_todos()

    if not (isinstance(user_id, list) and isinstance(todo_names, list)):
        raise TypeError("user_id and todo_names have to be lists.")

    inv_map = {v: k for k, v in loader.tasks_dict.items()}

    for user in user_id:
        adherence_dict[user] = {}
        participant_todos = loader.get_available_todos([user])
        for todo in todo_names:
            todo_name = inv_map[todo]
            adherence_dict[user][todo_name] = {}
            if todo in participant_todos:
                todo_df = loader.load_todo(
                    user, start_date, end_date, task_name=todo_name
                )
                timestamps = todo_df.unixTimestampInMs
                count = 0
                for i in range(len(timestamps)):
                    if (
                        i == 0
                        or timestamps[i] - timestamps[i - 1]
                        > _MS_TO_HOURS_CONVERSION * safe_delta
                    ):
                        count += 1
                adherence_dict[user][todo_name]["n_filled"] = count
                is_repeatable = utils.is_task_repeatable(
                    (
                        loader.data_path
                        / loader.get_full_id(user)
                        / _LABFRONT_TODO_STRING
                        / todo
                    )
                )
                adherence_dict[user][todo_name][
                    _LABFRONT_TASK_SCHEDULE_KEY
                ] = is_repeatable
            else:
                adherence_dict[user][todo_name]["n_filled"] = 0
                adherence_dict[user][todo_name][_LABFRONT_TASK_SCHEDULE_KEY] = None

    return adherence_dict


def get_todo_adherence(
    loader: BaseLoader,
    number_of_days,
    start_date=None,
    end_date=None,
    user_id="all",
    todo_names="all",
    safe_delta=6,
    return_percentage=False,
):
    """Returns adherence of the participant(s) for the todo(s). Assumes daily adherence is necessary for repetitive todos.

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        number_of_days (int): How many days the study lasted
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        user_id (list, optional): List of the participants of interest. Defaults to "all".
        todo_names (list, optional): List of the todos of interest. Defaults to "all".
        safe_delta (int, optional): Amount of hours needed to consider two successive filled todos valid. Defaults to 6.

    Returns:
        dict: Adherence dictionary containing the percentages of adherence wrt the requirements for the todos and participants of interest.
    """

    todo_adherence = {}

    todo_dict = get_todo_dict(
        loader, start_date, end_date, user_id, todo_names, safe_delta
    )
    for participant_id in todo_dict.keys():
        todo_adherence[participant_id] = {}
        for todo in todo_dict[participant_id].keys():
            if todo_dict[participant_id][todo][_LABFRONT_TASK_SCHEDULE_KEY]:
                if return_percentage:
                    todo_adherence[participant_id][todo] = round(
                        (todo_dict[participant_id][todo]["n_filled"] / number_of_days)
                        * 100,
                        2,
                    )
                else:
                    todo_adherence[participant_id][todo] = {}
                    todo_adherence[participant_id]["n_filled"] = todo_dict[
                        participant_id
                    ][todo]["n_filled"]
                    todo_adherence[participant_id]["total"] = number_of_days
            else:
                if return_percentage:
                    todo_adherence[participant_id][todo] = (
                        todo_dict[participant_id][todo]["n_filled"] == 1
                    ) * 100
                else:
                    todo_adherence[participant_id][todo] = {}
                    todo_adherence[participant_id]["n_filled"] = todo_dict[
                        participant_id
                    ][todo]["n_filled"]
                    todo_adherence[participant_id]["total"] = 1

    return todo_adherence


def get_metric_adherence(
    loader: BaseLoader,
    loader_metric_fn,
    expected_fs,
    start_date=None,
    end_date=None,
    user_id="all",
):
    """Given an expected sampling frequency for a metric, returns the percentage of adherence for that metric"""
    # TODO MOSTLY, for now it's only for one user at a time
    metric_df = loader_metric_fn(
        user_id, start_date, end_date + datetime.timedelta(hours=23, minutes=59)
    )
    return (
        metric_df.groupby(metric_df[loader.date_column].dt.date)[
            loader.date_column
        ].nunique()
        / (60 * 60 * 24 / expected_fs)
        * 100
    )


def get_garmin_device_adherence(
    loader: BaseLoader, start_date=None, end_date=None, user_id="all"
):
    data_dict = {}
    user_id = utils.get_user_ids(loader, user_id)

    for user in user_id:
        try:
            df = loader.load_garmin_device_bbi(user, start_date, end_date)
            data_dict[user] = (
                df.groupby(df["isoDate"].dt.date).bbi.sum() / _MS_TO_HOURS_CONVERSION
            ).to_dict()
        except:
            data_dict[user] = None

    return data_dict


def get_night_adherence(
    loader: BaseLoader,
    start_date=None,
    end_date=None,
    user_id="all",
    return_percentage=False,
):
    """Get adherence in terms of amount of sleeping data gathered

    Parameters
    ----------
    loader : :class:`pylabfront.loader`
        Initialized instance of :class:`pylabfront.loader`, required in order to properly load data.
    start_date : :class:`datetime.datetime`, optional
        Start date from which should be extracted, by default None.
        If None is used, then the ``start_date`` will be the first day with available data
        for the given ``user_id``.
    end_date : class:`datetime.datetime`, optional
        End date up to which data should be extracted (inclusive of the whole day), by default None.
        If None is used, then the ``end_date`` will be the last day with available data
        for the given ``user_id``.
    user_id : :class:`str`, optional
        IDs of the users for which data have to extracted, by default "all"
    return_percentage : :class:`bool`, optional
        Whether to return the adherence as a percentage wrt to the amount of expected nights.

    Returns
    -------
    _class:`dict`
        Dictionary with user id as primary key and night adherence (in days or pct) as value.
    """

    user_id = utils.get_user_ids(loader, user_id)

    data_dict = {}

    for user in user_id:
        try:
            sleep_df = loader.load_sleep_summary(user, start_date, end_date)
            # just to be sure we check that there's only one row per day
            sleep_summaries = len(
                sleep_df.groupby(constants._CALENDAR_DATE_COL).tail(1)
            )
            num_nights = (end_date - start_date).days
            if return_percentage:
                data_dict[user] = round(sleep_summaries / num_nights * 100, 2)
            else:
                data_dict[user] = {}
                data_dict[user]["total"] = num_nights
                data_dict[user]["n_nights"] = sleep_summaries
        except:
            if return_percentage:
                data_dict[user] = 0
            else:
                data_dict[user] = {}

    return data_dict
