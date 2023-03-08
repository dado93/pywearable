import os
from pathlib import Path

import utils

_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'
_LABFRONT_QUESTIONNAIRE_STRIGN = 'questionnaire'
_LABFRONT_TODO_STRING = 'todo'

BASE_FOLDER = Path('data') / 'sample_data' / \
    '9dbabd13-879e-4131-a562-66a2501435ab'

ids, lf_ids = utils.get_ids(BASE_FOLDER)

id_dict = dict(zip(ids, lf_ids))

id = '01---ipad,-green-watch'
labfront_id = id_dict[id]

path_to_data = id + '_' + labfront_id
print(os.path.join(BASE_FOLDER, path_to_data))
if not os.path.exists(os.path.join(BASE_FOLDER, path_to_data)):
    print(f'Data folder for participant {id} does not exist')

for data_folder in os.listdir(os.path.join(BASE_FOLDER, path_to_data)):
    if os.path.isdir(os.path.join(BASE_FOLDER, path_to_data, data_folder)):
        print(os.path.join(BASE_FOLDER, path_to_data, data_folder))
