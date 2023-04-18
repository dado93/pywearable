import datetime
import pandas as pd
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

import os
import sys

sys.path.insert(0, os.path.abspath('../pylabfront'))

import pylabfront.loader as loader
import pylabfront.sleep as sleep
import pylabfront.utils as utils
import pylabfront.respiration as respiration

BASE_FOLDER =  Path('data') / 'pmi-mini_pilot' / '4de37ee3-7baf-4592-a431-a6d01fff6bd1'

# Select participant ID
id = 'WRSD-PMI-01'

start_dt = datetime.datetime(2023,1,1)
end_dt = datetime.datetime(2023,4,28)

labfront_loader = loader.LabfrontLoader(BASE_FOLDER)

rest_bpm = respiration.get_average_rest_breaths_per_minute_per_night(labfront_loader, start_dt, end_dt, id)
waking_bpm = respiration.get_average_waking_breaths_per_minute_per_day(labfront_loader, start_dt, end_dt, id)
all_bpm = respiration.get_average_breaths_per_minute_per_day(labfront_loader, start_dt, end_dt, id)

average_rest_bpm = respiration.get_average_rest_breaths_per_minute(labfront_loader, start_dt, end_dt, id)
average_waking_bpm = respiration.get_average_waking_breaths_per_minute(labfront_loader, start_dt, end_dt, id)

rest_bpm_df = pd.DataFrame.from_dict(rest_bpm[id], orient='index', columns=['breathsPerMinute'])
waking_bpm_df = pd.DataFrame.from_dict(waking_bpm[id], orient='index', columns=['breathsPerMinute'])
all_bpm_df = pd.DataFrame.from_dict(all_bpm[id], orient='index', columns=['breathsPerMinute'])

plt.plot(rest_bpm_df.index, rest_bpm_df.breathsPerMinute)
plt.plot(waking_bpm_df.index, waking_bpm_df.breathsPerMinute)
plt.plot(all_bpm_df.index, all_bpm_df.breathsPerMinute, '--')

plt.show()