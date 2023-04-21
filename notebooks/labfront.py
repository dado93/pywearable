import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import pylabfront.loader as loader

# import pylabfront.sleep as sleep
import pylabfront.respiration as respiration

BASE_FOLDER = Path("data") / "pmi-mini_pilot" / "4de37ee3-7baf-4592-a431-a6d01fff6bd1"

# Select participant ID
id = "WRSD-PMI-01"

start_dt = datetime.datetime(2023, 3, 24)
end_dt = datetime.datetime(2023, 3, 30)

labfront_loader = loader.LabfrontLoader(BASE_FOLDER)
"""
sleep_stats = sleep.get_sleep_statistics(
    labfront_loader, start_dt, end_dt, id, average=True
)

print(sleep_stats)

tib = sleep.get_time_in_bed(labfront_loader, start_dt, end_dt, id, average=False)
print(tib)
tib_df = pd.DataFrame.from_dict(tib[id], orient="index")
sleep_stats = sleep.get_sleep_statistics(
    labfront_loader, start_dt, end_dt, id, average=False
)
print(sleep_stats[id])

sleep_stats_df = pd.DataFrame.from_dict(
    {
        (i, j): sleep_stats[id][i][j]
        for i in sleep_stats[id].keys()
        for j in sleep_stats[id][i].keys()
        if j is not None
    },
    orient="index",
)

print(sleep_stats_df.head())

plt.plot(sleep_stats_df.iloc[:, "TIB"], label="TIB")
plt.plot(sleep_stats_df.iloc[:, "SPT"], label="SPT")
plt.plot(sleep_stats_df.iloc[:, "WASO"], label="WASO")
plt.legend()

"""

respiratory_data = labfront_loader.load_garmin_connect_respiration(id, None, None)
print(respiratory_data)

breaths_per_minute = respiration.get_rest_breaths_per_minute(
    labfront_loader,
    user_id=id,
    start_date=None,
    end_date=None,
    average=False,
)
print(breaths_per_minute)


plt.show()
