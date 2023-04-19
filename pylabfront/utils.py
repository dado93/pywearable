import time
import pandas as pd


def get_user_ids(loader, user_ids):
    if user_ids == "all":
        user_ids = loader.get_user_ids()

    if isinstance(user_ids, str):
        if user_ids not in loader.get_user_ids():
            raise ValueError("User not found")
        else:
            user_ids = [user_ids]

    if not isinstance(user_ids, list):
        raise TypeError("participant_ids has to be a list.")
    
    return user_ids

def get_summary(loader):
    # TODO COMPLETELY CHANGE ??
    """ Returns a general summary of the latest update of every metric for every participant
    
    Args:
        data_path (str): Path to folder containing data.

    Returns:
        DataFrame: general summary of the number of full days since metrics were updated for all participants.
        Entries are NaN if the metric has never been registered for the participant.
    """

    available_metrics = set(loader.get_available_metrics())
    available_metrics.discard("todo")
    available_metrics.discard("questionnaire")
    available_metrics = sorted(list(available_metrics))
    available_questionnaires = loader.get_available_questionnaires()
    MS_TO_DAY_CONVERSION = 1000*60*60*24

    features_dictionary = {}
    
    for full_participant_id in sorted(loader.ids_dict.keys()):
        participant_id = full_participant_id[:(len(full_participant_id)- loader._LABFRONT_ID_LENGHT)]
        features_dictionary[participant_id] = {}
        participant_metrics = loader.get_available_metrics([full_participant_id])
        participant_questionnaires = loader.get_available_questionnaires([full_participant_id])

        for metric in available_metrics:
            name_metric = metric[7:]
            if metric not in participant_metrics:
                features_dictionary[participant_id][name_metric] = None
            else: # figure out how many days since the last update
               last_unix_times = [v[loader._LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] for v in loader.ids_dict[full_participant_id][metric].values()]
               number_of_days_since_update = (time.time()*1000 - max(last_unix_times)) // MS_TO_DAY_CONVERSION
               features_dictionary[participant_id][name_metric] = number_of_days_since_update
        
        for questionnaire in available_questionnaires:
            name_questionnaire = questionnaire[:(len(questionnaire) - loader._LABFRONT_ID_LENGHT)]
            if questionnaire not in participant_questionnaires:
                features_dictionary[participant_id][name_questionnaire] = None
            else:
                last_unix_times = [v[loader._LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] for v in loader.ids_dict[full_participant_id][loader._LABFRONT_QUESTIONNAIRE_STRING][questionnaire].values()]
                number_of_days_since_update = (time.time()*1000 - max(last_unix_times)) // MS_TO_DAY_CONVERSION
                features_dictionary[participant_id][name_questionnaire] = number_of_days_since_update

    df = pd.DataFrame(features_dictionary)
    return df.T

def is_task_repetable(file_path):
    """Returns boolean indication of questionnaire/todo repetability

    Args:
        file_path (Path): path to the folder of the questionnaire/todo csv files

    Returns:
        bool: Indication if the questionnaire/todo is repeatable
    """
    csv_path = list((file_path).iterdir())[0]
    with open(csv_path,"r") as f:
        for _ in range(5):
            line = f.readline().split(",")
    return line[7] == "true"

def is_weekend(day):
    """ Indication if the day considered is either a Saturday or Sunday.

    Args:
        day (datatime): date of interest.

    Returns:
        bool: True/False depending if day is a weekend day or not.
    """
    return day.weekday() in [5,6]