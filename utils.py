import os
from pathlib import Path

import datetime
import pandas as pd
import timeit

_LABFRONT_ID_LENGHT = 37
_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = 'firstSampleUnixTimestampInMs'
_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = 'lastSampleUnixTimestampInMs'
_LABFRONT_ISO_DATE_KEY = 'isoDate'
_LABFRONT_CSV_STATS_SKIP_ROWS = 3
_LABFRONT_QUESTIONNAIRE_STRING = 'questionnaire'
_LABFRONT_TODO_STRING = 'todo'
_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY = 'timezoneOffsetInMs'
_LABFRONT_GARMIN_DEVICE_TIMEZONEOFFSET_MS_KEY = 'timezone'

_LABFRONT_UNIXTIMESTAMP_MS_KEY = 'unixTimestampInMs'
_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'

def create_time_dictionary(data_path):
    """Create a dictionary with start and end times for all files.

    This function creates and returns a dictionary with start and
    end unix times for all the files that are present in the 
    data_path. This is useful to easily determine, based on an
    input time and date, which files need to be loaded.
    Args:
        data_path (str): Path to folder containing data.
    Returns:
        dict: Dictionary with start and end times for all files.
    """
    
    data_path = Path(data_path)
    if not data_path.exists():
        raise FileNotFoundError
    participant_dict = {}
    for participant_folder in data_path.iterdir():
        # For each participant
        participant_dict[participant_folder.name] = {}
        if participant_folder.is_dir():
            for participant_metric_folder in participant_folder.iterdir():
                # For each metric
                if participant_metric_folder.is_dir():
                    participant_dict[participant_folder.name][participant_metric_folder.name] = {}
                    # If it is a folder, then we need to read the csv files and get first and last unix times, and min sample rate
                    for metric_data in participant_metric_folder.iterdir():
                        # For each csv folder/file
                        if metric_data.is_file():
                            # If it is a file
                            first_ts, last_ts = get_labfront_file_stats(metric_data)
                            participant_dict[participant_folder.name][participant_metric_folder.name][metric_data.name] = {
                                _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: first_ts,
                                _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: last_ts
                            }
                        else:
                            # For each questionnaire/task folder
                            participant_dict[participant_folder.name][participant_metric_folder.name][metric_data.name] = {}
                            for csv_file in metric_data.iterdir():
                                first_ts, last_ts = get_labfront_file_stats(csv_file)
                                participant_dict[participant_folder.name][participant_metric_folder.name][metric_data.name][csv_file.name] = {
                                    _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: first_ts,
                                    _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: last_ts
                                }
    return participant_dict

def get_files_timerange(participant_dict, participant_id, 
                            metric, start_date, end_date, 
                            is_questionnaire=False, is_todo=False, task_name = None):
    """Get files containing daily data from within a given time range.

    This function retrieves the files that contain data in a given time range. By setting start 
    and end times to the time range of interest, this function returns all the files that
    contain data within this time range. This function is based on unix timestamps, thus it
    does not take into account timezones. In order to find the files containing data within
    the timerange, 12 hours are removed (added) from the start_date (end_date).

    Args:
        participant_dict (dict): Dictionary with first and last unix time stamps for each participant
                                    and for each metric.
        participant_id (str): Unique participant identified
        metric (str): Metric of interest
        start_date (datetime): Start date and time of interest
        end_date (datetime): End date and time of interest
        is_questionnaire (bool, optional): Metric of interest is a questionnaire. Defaults to False.
        is_todo (bool, optional): Metric of interest is a todo. Defaults to False.
        task_name (str, optional): Name of the questionnaire or of the todo. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        list: Array with files that are closest to the requested datetime.
    """
    if is_questionnaire and is_todo:
        with ValueError as e:
            raise e + "Select only questionnaire or todo."
    if (is_questionnaire or is_todo) and (task_name is None):
        with ValueError as e:
            raise e + "Please specify name of questionnaire or of todo."
    if is_questionnaire or is_todo:
        temp_dict = participant_dict[participant_id][metric][task_name]
    else:
        temp_dict = participant_dict[participant_id][metric]
    # Convert dictionary to a pandas dataframe, so that we can sort it
    temp_pd = pd.DataFrame.from_dict(temp_dict, orient='index').sort_values(by=_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY)
    if (start_date is None) and (end_date is None):
        return list(temp_pd.index)
    # Convert date to unix format: YYYY/MM/DD
    # First, make sure that we have a datetime
    if not isinstance(start_date, datetime.datetime):
        start_dt = datetime.datetime.strptime(start_date, "%Y/%m/%d")
    else:
        start_dt = start_date
    if not isinstance(end_date, datetime.datetime):
        end_dt = datetime.datetime.strptime(end_date, "%Y/%m/%d")
    else:
        end_dt = end_date

    # Then, convert it to UNIX timestamp
    start_dt_timestamp = (start_dt - datetime.timedelta(hours=12)).timestamp()
    end_dt_timestamp = (end_dt + datetime.timedelta(hours=12)).timestamp()
    # Compute difference with first and last columns
    temp_pd['min_diff'] = temp_pd[_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] - start_dt_timestamp
    temp_pd['max_diff'] = temp_pd[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] - end_dt_timestamp

    # For the first time stamp, let's check if we have some files that start before date
    temp_pd_min = temp_pd[temp_pd['min_diff'] < 0]
    if len(temp_pd_min) > 0:
        min_row = temp_pd_min['min_diff'].idxmin()
    else:
        min_row = temp_pd['min_diff'].idxmin()
    
    # For last time stamp, let's check if we have some files that start after date
    temp_pd_max = temp_pd[temp_pd['max_diff'] > 0]
    # Find rows with lowest difference
    if len(temp_pd_max) > 0:
        max_row = temp_pd_max['max_diff'].idxmin()
    else:
        max_row = temp_pd['max_diff'].idxmin()

    return list(temp_pd.loc[min_row:max_row].index)

def get_data_from_datetime(data_path, participant_id, metric, start_date, 
                            end_date, is_questionnaire=False, is_todo=False, task_name = None):
    
    if is_questionnaire and is_todo:
        raise ValueError("Select only questionnaire or todo.")
    if (is_questionnaire or is_todo) and (task_name is None):
        raise ValueError("Specify name of questionnaire or of todo.")
    
    participant_dict = create_time_dictionary(data_path)
    files = get_files_timerange(participant_dict, participant_id, 
                                metric, start_date, end_date, is_questionnaire, is_todo, task_name)
    
    if len(files) == 0:
        raise ValueError("No files available to load data.")
    if is_questionnaire:
        path_to_folder = Path(data_path) / participant_id / metric / _LABFRONT_QUESTIONNAIRE_STRING / task_name
    elif is_todo:
        path_to_folder = Path(data_path) / participant_id / metric / _LABFRONT_TODO_STRING / task_name
    else:
        path_to_folder = Path(data_path) / participant_id / metric

    # Load data from first file
    data = pd.read_csv(path_to_folder / files[0], skiprows=5)
    if _LABFRONT_GARMIN_CONNECT_STRING in metric:
        data = data.drop([_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY, _LABFRONT_UNIXTIMESTAMP_MS_KEY], axis=1)
    else:
        data = data.drop([_LABFRONT_GARMIN_DEVICE_TIMEZONEOFFSET_MS_KEY, _LABFRONT_UNIXTIMESTAMP_MS_KEY], axis=1)
    for f in files[1:]:
        tmp = pd.read_csv(path_to_folder / f, skiprows=5)
        if _LABFRONT_GARMIN_CONNECT_STRING in metric:
            tmp = tmp.drop([_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY, _LABFRONT_UNIXTIMESTAMP_MS_KEY], axis=1)
        else:
            tmp = tmp.drop([_LABFRONT_GARMIN_DEVICE_TIMEZONEOFFSET_MS_KEY, _LABFRONT_UNIXTIMESTAMP_MS_KEY], axis=1)
        data = pd.concat([data, tmp], ignore_index=True)
    # Convert to datetime according to isoformat
    data[_LABFRONT_ISO_DATE_KEY] = pd.to_datetime(data[_LABFRONT_ISO_DATE_KEY], format="%Y-%m-%dT%H:%M:%S.%f%z")
    # Get data only from given start and end dates
    if (not start_date is None) and (not end_date is None):
        return data[(data[_LABFRONT_ISO_DATE_KEY].dt.tz_localize(None) >= start_date)
                    & (data[_LABFRONT_ISO_DATE_KEY].dt.tz_localize(None) <= end_date)]
    else:
        return data

def get_ids(folder, return_dict=False):
    """Get participant IDs from folder with data.

    Args:
        folder (str): Path to folder containing data from participants.
        return_dict (bool): Whether to return a dictionary or two lists. Defaults to False.

    Returns:
        list: IDs of participants
        list: Labfront IDs of participants
    """
    # Get the names of the folder in root_folder
    folder_names = os.listdir(folder)
    ids = []
    labfront_ids = []
    for folder_name in folder_names:
        # Check that we have a folder
        if os.path.isdir(os.path.join(folder, folder_name)):
            labfront_id = folder_name[-_LABFRONT_ID_LENGHT+1:]
            labfront_ids.append(labfront_id)
            id = folder_name[:(len(folder_name)-_LABFRONT_ID_LENGHT)]
            ids.append(id)
    if return_dict:
        return dict(zip(ids, labfront_ids))
    return ids, labfront_ids

def get_header_length(file):
    """Get header length of Labfront csv file.

    Args:
        file (str): Path to csv file.
    """
    # Read first line of file
    with open(file, 'r') as f:
        line = f.readline().split(',')
    header_length = int(line[1])
    return header_length

def get_labfront_file_stats(path):
    """_summary_

    Args:
        path (str): Path to the file from which stats have to be extracted
        header_length (int): Length of the header in the csv file.

    Returns:
        int: First unix timestamp of data in csv file
        int: Last unix timestamp of data in csv file
    """

    # Get first and last unix timestamps from header
    header = pd.read_csv(path, nrows=1, skiprows=_LABFRONT_CSV_STATS_SKIP_ROWS)
    first_unix_timestamp = header[_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY].iloc[0]
    last_unix_timestamp = header[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY].iloc[0]
    
    return first_unix_timestamp, last_unix_timestamp

def get_available_metrics(folder):
    pass