import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

import utils

BASE_FOLDER = Path('data') / 'sample_data' / \
    '9dbabd13-879e-4131-a562-66a2501435ab'

# Get dictionary with participant IDs
id_dict = utils.get_ids(BASE_FOLDER, return_dict=True)

# Select participant ID
id = '01---ipad,-green-watch'
labfront_id = id_dict[id]

start_dt = datetime.datetime(2023,1,18)
end_dt = datetime.datetime(2023,1,19)

p_data = utils.get_data_from_datetime(BASE_FOLDER, 
                                      id + '_' + labfront_id, 'garmin-device-stress', 
                                      start_date=start_dt, end_date=end_dt)

plt.figure()
plt.plot(p_data[p_data.stressLevel > -1].isoDate.dt.tz_localize(None), p_data.stressLevel[p_data.stressLevel > -1])
plt.xlim([start_dt, end_dt])
plt.show()