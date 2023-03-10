import os
from pathlib import Path

import utils

_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'
_LABFRONT_QUESTIONNAIRE_STRIGN = 'questionnaire'
_LABFRONT_TODO_STRING = 'todo'

BASE_FOLDER = Path('data') / 'sample_data' / \
    '9dbabd13-879e-4131-a562-66a2501435ab'

# Get dictionary with participant IDs
id_dict = utils.get_ids(BASE_FOLDER, return_dict=True)

# Select participant ID
id = '01---ipad,-green-watch'
labfront_id = id_dict[id]

# Create folder name based on IDs
path_to_data = id + '_' + labfront_id

# Check that folder exists
if not (BASE_FOLDER / path_to_data).exists():
    print(f'Data folder for participant {id} does not exist')

# This is the summary dictionary of the participant
participant_summary_dict = {}

for participant_data_folder in (BASE_FOLDER / path_to_data).iterdir():
    # For each data folder of the participant
    if participant_data_folder.is_dir():
        # If it is a folder, then we need to read the csv files
        for csv_file in participant_data_folder.iterdir():
            if csv_file.is_file():
                # Get header length
                h_length = utils.get_header_length(csv_file)
                print(h_length)
                participant_summary_dict[participant_data_folder.name] = {}
            elif csv_file.is_dir():
                if _LABFRONT_QUESTIONNAIRE_STRIGN in csv_file:
                    # We have questionnaires
                    pass
                elif _LABFRONT_TODO_STRING in csv_file:
                    # We have todos
                    pass

print(participant_summary_dict)
