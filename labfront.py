import os
from pathlib import Path

import numpy as np
import pandas as pd
import utils
import matplotlib.pyplot as plt

_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'

_LABFRONT_GARMIN_CONNECT_HEART_RATE_KEY = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-heart-rate'
_LABFRONT_GARMIN_CONNECT_HEART_RATE_COL = 'beatsPerMinute'
_LABFRONT_GARMIN_DEVICE_HEART_RATE_KEY = _LABFRONT_GARMIN_DEVICE_STRING + '-heart-rate'

_LABFRONT_QUESTIONNAIRE_STRIGN = 'questionnaire'
_LABFRONT_TODO_STRING = 'todo'
_LABFRONT_TIMEZONEOFFSET_MS = 'timezoneOffsetInMs'
_LABFRONT_UNIXTIMESTAMP_MS = 'unixTimestampInMs'
_LABFRONT_ISODATE = 'isoDate'


_LABFRONT_PHYSIO_CSV = ['garmin-connect-daily-heart-rate','garmin-device-heart-rate',
                            'garmin-connect-pulse-ox', 'garmin-connect-sleep-pulse-ox',
                            'garmin-device-pulse-ox',
                            'garmin-connect-respiration', 'garmin-connect-sleep-respiration',
                            'garmin-device-respiratorion',
                            #'garmin-connect-stress', 
                            'garmin-device-stress']

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


# Physiological data extraction
for participant_data_folder in (BASE_FOLDER / path_to_data).iterdir():
    # For each data folder of the participant
    if participant_data_folder.is_dir():
        # If it is a folder, then we need to read the csv files and get first and last unix times, and min sample rate
        first_run = True
        for csv_file in participant_data_folder.iterdir():
            if csv_file.is_file() and str(participant_data_folder.name) in _LABFRONT_PHYSIO_CSV:
                # Interested only in physiological signals
                h_length = utils.get_header_length(csv_file)
                first_ts, last_ts, sample_rate = utils.get_labfront_file_stats(csv_file, h_length)
                if first_run:
                    participant_summary_dict[participant_data_folder.name] = {}
                    participant_summary_dict[participant_data_folder.name]['fullPath'] = participant_data_folder
                    min_unix_timestamp = first_ts
                    max_unix_timestamp = last_ts
                    min_sample_rate = sample_rate
                    first_run = False
                else:
                    if first_ts < min_unix_timestamp:
                        min_unix_timestamp = first_ts
                    if last_ts > max_unix_timestamp:
                        max_unix_timestamp = last_ts
                    if sample_rate < min_sample_rate:
                        min_sample_rate = sample_rate
                participant_summary_dict[participant_data_folder.name][utils._LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] = min_unix_timestamp
                participant_summary_dict[participant_data_folder.name][utils._LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] = max_unix_timestamp
                participant_summary_dict[participant_data_folder.name]['sampleRate'] = min_sample_rate

print(participant_summary_dict)

# Now, we need to find the first unix time stamp, and last unix time stamp
min_first_unix_key = min(participant_summary_dict, key=lambda x: participant_summary_dict[x][utils._LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY])
max_last_unix_key = max(participant_summary_dict, key=lambda x: participant_summary_dict[x][utils._LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY])
min_unix_timestamp = participant_summary_dict[min_first_unix_key][utils._LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY]
max_unix_timestamp = participant_summary_dict[max_last_unix_key][utils._LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY]
# .. and the lowest sample rate
min_sample_rate_key = min(participant_summary_dict, key=lambda x: participant_summary_dict[x]['sampleRate'])
min_sample_rate = participant_summary_dict[min_sample_rate_key]['sampleRate']

# Let's set up the dataframe for the participant
time_values = np.linspace(min_unix_timestamp, max_unix_timestamp, 
                            int((max_unix_timestamp-min_unix_timestamp)/(min_sample_rate*1000)), 
                            dtype=np.int64,
                            endpoint=True)
participant_df = pd.DataFrame(data={
    _LABFRONT_UNIXTIMESTAMP_MS: time_values,
})
#participant_df['isoDate'] = pd.to_datetime(participant_df[_LABFRONT_UNIXTIMESTAMP_MS], unit='ms')

# garmin-connect-heart-rate
if _LABFRONT_GARMIN_CONNECT_HEART_RATE_KEY in participant_summary_dict.keys():
    for csv_file in participant_summary_dict[_LABFRONT_GARMIN_CONNECT_HEART_RATE_KEY]['fullPath'].iterdir():
        h_length = utils.get_header_length(csv_file)
        tmp = pd.read_csv(csv_file, skiprows = h_length, usecols = [_LABFRONT_TIMEZONEOFFSET_MS, 
                                                                    _LABFRONT_UNIXTIMESTAMP_MS,
                                                                    _LABFRONT_GARMIN_CONNECT_HEART_RATE_COL])
        
        tmp.columns = [_LABFRONT_GARMIN_CONNECT_HEART_RATE_KEY + '-' + _LABFRONT_TIMEZONEOFFSET_MS,
                            _LABFRONT_UNIXTIMESTAMP_MS, 
                            _LABFRONT_GARMIN_CONNECT_HEART_RATE_KEY + '-' + _LABFRONT_GARMIN_CONNECT_HEART_RATE_COL]
        participant_df = participant_df.merge(tmp, 'outer', on=_LABFRONT_UNIXTIMESTAMP_MS)
        participant_df.to_csv('test.csv')