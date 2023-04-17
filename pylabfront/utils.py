import time
import pandas as pd

def get_summary(loader):
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