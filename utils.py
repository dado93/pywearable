
import os
import pandas as pd

_LABFRONT_ID_LENGHT = 37
_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = 'firstSampleUnixTimestampInMs'
_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = 'lastSampleUnixTimestampInMs'
_LABFRONT_ISO_DATE_KEY = 'isoDate'

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

def get_labfront_file_stats(path, header_length):
    """_summary_

    Args:
        path (str): Path to the file from which stats have to be extracted
        header_length (int): Length of the header in the csv file.

    Returns:
        int: First unix timestamp of data in csv file
        int: Last unix timestamp of data in csv file
        int: Sample rate (in seconds)
    """

    # Get first and last unix timestamps from header
    header = pd.read_csv(path, nrows=1, skiprows=header_length-2)
    first_unix_timestamp = header[_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY].iloc[0]
    last_unix_timestamp = header[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY].iloc[0]
    
    # Get sample rate from data
    data = pd.read_csv(path, nrows=2, skiprows=header_length+1, usecols=[_LABFRONT_ISO_DATE_KEY])
    tmp_data = data[_LABFRONT_ISO_DATE_KEY]
    sample_rate = (data[_LABFRONT_ISO_DATE_KEY].iloc[1] - data[_LABFRONT_ISO_DATE_KEY].iloc[0]).total_seconds()

    return first_unix_timestamp, last_unix_timestamp, sample_rate


def get_garmin_metrics_names(folder):
    pass
