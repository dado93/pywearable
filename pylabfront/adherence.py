"""
This module contains all the functions related to the analysis
of Labfront adherence.
"""


import pylabfront.utils as utils
import pandas as pd
import datetime

from pathlib import Path

_LABFRONT_TASK_SCHEDULE_KEY = "taskScheduleRepeat"
_LABFRONT_TODO_STRING = 'todo'
_LABFRONT_QUESTIONNAIRE_STRING = 'questionnaire'
_MS_TO_HOURS_CONVERSION = 1000*60*60

def get_questionnaire_dict(loader, start_dt, end_dt, participant_ids="all", questionnaire_names="all", safe_delta=6):
    """
    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        number_of_days (int): How many days the study lasted
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        participant_ids (list):  IDs of participants. Defaults to "all".
        questionnaire_names (list): Name of the questionnaires. Defaults to "all".
        safe_delta (int): Amount of hours needed to consider two successive filled questionnaires valid. Defaults to 6.

    Returns:
        dict: Dictionary with adherence data for the partecipants and questionnaires required.
    """
    adherence_dict = {}

    if participant_ids == "all":
        participant_ids = loader.get_user_ids()

    if questionnaire_names == "all":
        questionnaire_names = loader.get_available_questionnaires()

    if not (isinstance(participant_ids, list) and isinstance(questionnaire_names, list)):
        raise TypeError("participant_ids and questionnaire_names have to be lists.")
    
    inv_map = {v: k for k, v in loader.tasks_dict.items()}

    for participant_id in participant_ids:
        adherence_dict[participant_id] = {}
        participant_questionnaires = loader.get_available_questionnaires([participant_id])
        for questionnaire in questionnaire_names:
            questionnaire_name = inv_map[questionnaire]
            adherence_dict[participant_id][questionnaire_name] = {}
            if questionnaire in participant_questionnaires:
                questionnaire_df = loader.load_questionnaire(participant_id,start_dt,end_dt,task_name=questionnaire_name)
                timestamps = questionnaire_df.unixTimestampInMs
                count = 0
                for i in range(len(timestamps)):
                    if i == 0 or timestamps[i]-timestamps[i-1] > _MS_TO_HOURS_CONVERSION*safe_delta:
                        count += 1
                adherence_dict[participant_id][questionnaire_name]["n_filled"] = count
                is_repeatable = utils.is_task_repetable((loader.data_path/loader.get_full_id(participant_id)/_LABFRONT_QUESTIONNAIRE_STRING/questionnaire))
                adherence_dict[participant_id][questionnaire_name][_LABFRONT_TASK_SCHEDULE_KEY] = is_repeatable
            else:
                adherence_dict[participant_id][questionnaire_name]["n_filled"] = 0
                adherence_dict[participant_id][questionnaire_name][_LABFRONT_TASK_SCHEDULE_KEY] = None

    return adherence_dict

def get_questionnaire_adherence(loader, number_of_days, start_dt=None, end_dt=None, participant_ids="all",questionnaire_names="all",safe_delta=6):
    """Returns adherence of the partecipant(s) for the questionnaire(s). Assumes daily adherence is necessary for repetitive questionnaires.

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        number_of_days (int): How many days the study lasted
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list, optional): List of the participants of interest. Defaults to "all".
        questionnaire_names (list, optional): List of the questionnaires of interest. Defaults to "all".
        safe_delta (int, optional): Amount of hours needed to consider two successive filled questionnaires valid. Defaults to 6.

    Returns:
        dict: Adherence dictionary containing the percentages of adherence wrt the requirements for the questionaries and participants of interest.
    """
    
    questionnaire_adherence = {}

    questionnaire_dict = get_questionnaire_dict(loader,start_dt,end_dt,participant_ids,questionnaire_names,safe_delta)
    for participant_id in questionnaire_dict.keys():
        questionnaire_adherence[participant_id] = {}
        for questionnaire in questionnaire_dict[participant_id].keys():
            if questionnaire_dict[participant_id][questionnaire][_LABFRONT_TASK_SCHEDULE_KEY]:
                questionnaire_adherence[participant_id][questionnaire] = round((questionnaire_dict[participant_id][questionnaire]["n_filled"] / number_of_days)*100,2)
            else:
                questionnaire_adherence[participant_id][questionnaire] = (questionnaire_dict[participant_id][questionnaire]["n_filled"] == 1) * 100
    
    return questionnaire_adherence

def get_todo_dict(loader, start_dt=None, end_dt=None, participant_ids="all", todo_names="all", safe_delta=6):
    """
    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list):  IDs of participants. Defaults to "all".
        todo_names (list): Name of the todos. Defaults to "all".
        safe_delta (int): Amount of hours needed to consider two successive filled todos valid. Defaults to 6.

    Returns:
        dict: Dictionary with adherence data for the partecipants and todos required.
    """

    adherence_dict = {}

    if participant_ids == "all":
        participant_ids = loader.get_user_ids()

    if todo_names == "all":
        todo_names =loader.get_available_todos()

    if not (isinstance(participant_ids, list) and isinstance(todo_names, list)):
        raise TypeError("participant_ids and todo_names have to be lists.")

    inv_map = {v: k for k, v in loader.tasks_dict.items()}

    for participant_id in participant_ids:
        adherence_dict[participant_id] = {}
        participant_todos = loader.get_available_todos([participant_id])
        for todo in todo_names:
            todo_name = inv_map[todo]
            adherence_dict[participant_id][todo_name] = {}
            if todo in participant_todos:
                todo_df = loader.load_todo(participant_id,start_dt,end_dt,task_name=todo_name)
                timestamps = todo_df.unixTimestampInMs
                count = 0
                for i in range(len(timestamps)):
                    if i == 0 or timestamps[i]-timestamps[i-1] > _MS_TO_HOURS_CONVERSION*safe_delta:
                        count += 1
                adherence_dict[participant_id][todo_name]["n_filled"] = count
                is_repeatable = utils.is_task_repetable((loader.data_path/loader.get_full_id(participant_id)/_LABFRONT_TODO_STRING/todo))
                adherence_dict[participant_id][todo_name][_LABFRONT_TASK_SCHEDULE_KEY]= is_repeatable
            else:
                adherence_dict[participant_id][todo_name]["n_filled"] = 0
                adherence_dict[participant_id][todo_name][_LABFRONT_TASK_SCHEDULE_KEY] = None

    return adherence_dict

def get_todo_adherence(loader, number_of_days, start_dt=None, end_dt=None, participant_ids="all",todo_names="all",safe_delta=6):
    """Returns adherence of the partecipant(s) for the todo(s). Assumes daily adherence is necessary for repetitive todos.

    Args:
        loader: (:class:`pylabfront.loader.LabfrontLoader`): Instance of `LabfrontLoader`.
        number_of_days (int): How many days the study lasted
        start_date (:class:`datetime.datetime`, optional): Start date from which data should be extracted. Defaults to None.
        end_date (:class:`datetime.datetime`, optional): End date from which data should be extracted. Defaults to None.
        participant_ids (list, optional): List of the participants of interest. Defaults to "all".
        todo_names (list, optional): List of the todos of interest. Defaults to "all".
        safe_delta (int, optional): Amount of hours needed to consider two successive filled todos valid. Defaults to 6.

    Returns:
        dict: Adherence dictionary containing the percentages of adherence wrt the requirements for the todos and participants of interest.
    """
    
    todo_adherence = {}

    todo_dict = get_todo_dict(loader,start_dt,end_dt,participant_ids,todo_names,safe_delta)
    for participant_id in todo_dict.keys():
        todo_adherence[participant_id] = {}
        for todo in todo_dict[participant_id].keys():
            if todo_dict[participant_id][todo][_LABFRONT_TASK_SCHEDULE_KEY]:
                todo_adherence[participant_id][todo] = round((todo_dict[participant_id][todo]["n_filled"] / number_of_days)*100,2)
            else:
                todo_adherence[participant_id][todo] = (todo_dict[participant_id][todo]["n_filled"] == 1) * 100
    
    return todo_adherence

def get_metric_adherence(loader,
                         loader_metric_fn,
                         expected_fs,
                         start_date=None,
                         end_date=None,
                         user_id="all"):
    '''Given an expected sampling frequency for a metric, returns the percentage of adherence for that metric

    
    '''
    metric_df = loader_metric_fn(user_id,start_date,end_date+datetime.timedelta(hours=23,minutes=59))
    return metric_df.groupby(metric_df[loader.date_column].dt.date)[loader.date_column].nunique() / (60*60*24 / expected_fs) * 100
