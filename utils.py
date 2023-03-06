import os


def get_ids(folder):
    """
    """

    # Get the names of the folder in root_folder
    folder_names = os.listdir(folder)
    ids = []
    labfront_ids = []
    for folder_name in folder_names:
        if os.path.isdir(os.path.join(folder, folder_name)):
            labfront_ids.append(folder_name[-35:0])
            ids.append(folder_name[:(len(folder_name)-35)])

    return ids, labfront_ids


def get_garmin_metrics_names(folder):
    pass
