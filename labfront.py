import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

import utils

_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'

_LABFRONT_GARMIN_CONNECT_HEART_RATE_KEY = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-heart-rate'
_LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_KEY = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-pulse-ox'
_LABFRONT_GARMIN_CONNECT_HEART_RATE_COL = 'beatsPerMinute'
_LABFRONT_GARMIN_DEVICE_HEART_RATE_KEY = _LABFRONT_GARMIN_DEVICE_STRING + '-heart-rate'

BASE_FOLDER = Path('data') / 'sample_data' / \
    '9dbabd13-879e-4131-a562-66a2501435ab'

# Get dictionary with participant IDs
id_dict = utils.get_ids(BASE_FOLDER, return_dict=True)

# Select participant ID
id = '01---ipad,-green-watch'
labfront_id = id_dict[id]

start_dt = datetime.datetime(2023,1,18, 4,0,10)
end_dt = datetime.datetime(2023,1,19, 4, 0, 15)
p_data = utils.get_data_from_datetime(BASE_FOLDER, 
                                      id + '_' + labfront_id, _LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_KEY, 
                                      start_date=start_dt, end_date=end_dt)
plt.plot(p_data.isoDate, p_data.spo2)
plt.xlim([start_dt, end_dt])
plt.show()