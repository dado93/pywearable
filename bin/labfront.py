import datetime
import pandas as pd
from pathlib import Path

import os
import sys

sys.path.insert(0, os.path.abspath('../pylabfront'))

import pylabfront.loader as loader
import pylabfront.sleep as sleep
import pylabfront.utils as utils

BASE_FOLDER =  Path('data') / 'pmi-mini_pilot' / '4de37ee3-7baf-4592-a431-a6d01fff6bd1'

# Select participant ID
id = 'WRSD-PMI-01'

start_dt = datetime.datetime(2023,1,1)
end_dt = datetime.datetime(2023,4,28)

labfront_loader = loader.LabfrontLoader(BASE_FOLDER)

#heart_rate = loader.load_garmin_connect_pulse_ox(id)
#print(heart_rate.columns)
#plt.plot(heart_rate.isoDate, heart_rate.spo2)
#plt.show()

rem = sleep.get_rem_sleep(labfront_loader, participant_id="all")
#print(rem)

average_rem = sleep.get_average_rem_sleep(labfront_loader, participant_id="all")

ls = sleep.get_sleep_duration(labfront_loader, start_dt, end_dt, "all")

average_ls = sleep.get_average_sleep_score(labfront_loader, participant_id="all")
print(average_ls)