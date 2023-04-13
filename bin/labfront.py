import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

import os
import sys



sys.path.insert(0, os.path.abspath('../pylabfront'))

import pylabfront.data as data
import pylabfront.sleep as sleep
import pylabfront.utils as utils

BASE_FOLDER =  Path('data') / 'pmi-mini_pilot' / '4de37ee3-7baf-4592-a431-a6d01fff6bd1'

# Get dictionary with participant IDs
id_dict = utils.get_ids(BASE_FOLDER, return_dict=True)

# Select participant ID
id = 'WRSD-PMI-01'
labfront_id = id_dict[id]

start_dt = datetime.datetime(2023,1,1)
end_dt = datetime.datetime(2023,4,28)

rem = sleep.get_rem_sleep(BASE_FOLDER, start_dt, end_dt, "all")
print(rem)