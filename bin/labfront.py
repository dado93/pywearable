import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

import os
import sys

sys.path.insert(0, os.path.abspath('../pylabfront'))

import pylabfront.data as data
import pylabfront.utils as utils

BASE_FOLDER =  Path('data') / 'pmi-mini_pilot' / '4de37ee3-7baf-4592-a431-a6d01fff6bd1'

# Get dictionary with participant IDs
id_dict = utils.get_ids(BASE_FOLDER, return_dict=True)

# Select participant ID
id = 'WRSD-PMI-01'
labfront_id = id_dict[id]

start_dt = datetime.datetime(2023,1,1)
end_dt = datetime.datetime(2023,4,28)

data = utils.get_data_from_datetime(BASE_FOLDER, id + '_' + labfront_id, 'questionnaire', start_date=start_dt, end_date = end_dt,
                                        is_questionnaire=True, task_name='Morning-questionnair')

#p_data = data.load_garmin_device_heart_rate(BASE_FOLDER,
#                                             id + '_' + labfront_id,
#                                             start_dt,
#                                             end_dt)

#print(p_data.head())

#plt.figure()
#plt.plot(p_data.isoDate.dt.tz_localize(None), p_data.beatsPerMinute)
#plt.xlim([start_dt, end_dt])
#plt.show()