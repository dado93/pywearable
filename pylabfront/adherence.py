import pylabfront.utils as utils
import pandas as pd

from pathlib import Path

_LABFRONT_TASK_SCHEDULE_KEY = "taskScheduleRepeat"
_LABFRONT_QUESTIONNAIRE_STRING = 'questionnaire'
_MS_TO_HOURS_CONVERSION = 1000*60*60

def get_questionnaire_dict(data_path, start_dt, end_dt, participant_ids="all", questionnaire_names="all", safe_delta=6):
    """
    Args:
        data_path (str): Path to folder containing data.
        participant_ids (list):  IDs of participants. Defaults to "all".
        questionnaire_names (list): Name of the questionnaires. Defaults to "all".
        safe_delta (int): Amount of hours needed to consider two successive filled questionnaires valid. Defaults to 6.

    Returns:
        dict: Dictionary with adherence data for the partecipants and questionnaires required.
    """

    if participant_ids == "all":
        participant_ids = [k+"_"+v for k,v in utils.get_ids(data_path,return_dict=True).items()]

    if questionnaire_names == "all":
        questionnaire_names = utils.get_available_questionnaires(data_path)

    if not (isinstance(participant_ids, list) and isinstance(questionnaire_names, list)):
        raise TypeError("participant_ids and questionnaire_names have to be lists.")

    adherence_dict = {}

    for participant_id in participant_ids:
        adherence_dict[participant_id] = {}
        participant_questionnaires = utils.get_available_questionnaires(data_path, [participant_id])
        for questionnaire in questionnaire_names:
            adherence_dict[participant_id][questionnaire] = {}
            if questionnaire in participant_questionnaires:
                questionnaire_df = utils.get_data_from_datetime(data_path,participant_id,_LABFRONT_QUESTIONNAIRE_STRING,start_dt,end_dt,is_questionnaire=True,task_name=questionnaire)
                timestamps = questionnaire_df.unixTimestampInMs
                count = 0
                for i in range(len(timestamps)):
                    if i == 0 or timestamps[i]-timestamps[i-1] > _MS_TO_HOURS_CONVERSION*safe_delta:
                        count += 1
                adherence_dict[participant_id][questionnaire]["n_filled"] = count
                adherence_dict[participant_id][questionnaire][_LABFRONT_TASK_SCHEDULE_KEY]= is_questionnaire_repetable((Path(data_path)/participant_id/_LABFRONT_QUESTIONNAIRE_STRING/questionnaire))
            else:
                adherence_dict[participant_id][questionnaire]["n_filled"] = 0
                adherence_dict[participant_id][questionnaire][_LABFRONT_TASK_SCHEDULE_KEY] = None

    return adherence_dict

def is_questionnaire_repetable(file_path):
    """Returns boolean indication of questionnaire repetability

    Args:
        file_path (Path): path to the folder of the questionnaire csv files

    Returns:
        bool: Indication if the questionnaire is repeatable
    """
    csv_path = list((file_path).iterdir())[0]
    with open(csv_path,"r") as f:
        for _ in range(5):
            line = f.readline().split(",")
    return line[7] == "true"


def get_questionnaire_adherence(data_path, start_dt, end_dt, number_of_days, participant_ids="all",questionnaire_names="all",safe_delta=6):
    """Returns adherence of the partecipant(s) for the questionnaire(s)

    Args:
        data_path (str): Path to folder containing data.
        start_dt (datetime): Start date and time of interest
        end_dt (datetime): End date and time of interest
        number_of_days (int): How many days the study lasted
        participant_ids (list, optional): List of the participants of interest. Defaults to "all".
        questionnaire_names (list, optional): List of the questionnaires of interest. Defaults to "all".
        safe_delta (int, optional): Amount of hours needed to consider two successive filled questionnaires valid. Defaults to 6.

    Returns:
        dict: _description_
    """
    
    questionnaire_adherence = {}

    questionnaire_dict = get_questionnaire_dict(data_path,start_dt,end_dt,participant_ids,questionnaire_names,safe_delta)
    for participant_id in questionnaire_dict.keys():
        questionnaire_adherence[participant_id] = {}
        for questionnaire in questionnaire_dict[participant_id].keys():
            if questionnaire_dict[participant_id][questionnaire][_LABFRONT_TASK_SCHEDULE_KEY]:
                questionnaire_adherence[participant_id][questionnaire] = round((questionnaire_dict[participant_id][questionnaire]["n_filled"] / number_of_days)*100,2)
            else:
                questionnaire_adherence[participant_id][questionnaire] = (questionnaire_dict[participant_id][questionnaire]["n_filled"] == 1) * 100
    
    return questionnaire_adherence


def get_metric_adherence(metric_names, num_days):
    '''total hours for device, bool for connect'''
    pass
