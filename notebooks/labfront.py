
import sys
import os

sys.path.insert(0, os.path.abspath('../pylabfront'))


import pylabfront.loader as loader
import pylabfront.sleep as sleep
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from pathlib import Path
import pandas as pd


BASE_FOLDER = Path('data') / 'pmi-mini_pilot' / \
    '4de37ee3-7baf-4592-a431-a6d01fff6bd1'

# Select participant ID
id = 'WRSD-PMI-01'

start_dt = datetime.datetime(2023, 3, 24)
end_dt = datetime.datetime(2023, 3, 30)

labfront_loader = loader.LabfrontLoader(BASE_FOLDER)

sleep_stats = sleep.get_sleep_statistics(labfront_loader, start_dt, end_dt, id, average=True)
#print(sleep_stats[id])

#sleep_stats_df = pd.DataFrame.from_dict(sleep_stats[id], orient='index')

print(sleep_stats)

tib = sleep.get_time_in_bed(labfront_loader, start_dt, end_dt, id, average=False)
print(tib)