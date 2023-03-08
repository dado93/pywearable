import os

_LABFRONT_ID_LENGHT = 37


def get_ids(folder):
    """Get participant IDs from folder with data.

    Args:
        folder (str): Path to folder containing data from participants.

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
            labfront_ids.append(folder_name[-_LABFRONT_ID_LENGHT+1:])
            ids.append(folder_name[:(len(folder_name)-_LABFRONT_ID_LENGHT)])

    return ids, labfront_ids


def get_garmin_metrics_names(folder):
    pass
