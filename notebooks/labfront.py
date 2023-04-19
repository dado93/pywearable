from pathlib import Path
import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pylabfront.sleep as sleep
import pylabfront.loader as loader
import sys
import os

sys.path.insert(0, os.path.abspath('../pylabfront'))


BASE_FOLDER = Path('data') / 'pmi-mini_pilot' / \
    '4de37ee3-7baf-4592-a431-a6d01fff6bd1'

# Select participant ID
id = 'WRSD-PMI-01'

start_dt = datetime.datetime(2023, 3, 24)
end_dt = datetime.datetime(2023, 4, 28)

labfront_loader = loader.LabfrontLoader(BASE_FOLDER)

sleep_stats = sleep.get_sleep_statistics(labfront_loader, start_dt, end_dt, id)
print(sleep_stats)
