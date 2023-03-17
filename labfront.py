import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns

import data
import utils

BASE_FOLDER = Path('data') / 'sample_data' / \
    '9dbabd13-879e-4131-a562-66a2501435ab'

# Get dictionary with participant IDs
id_dict = utils.get_ids(BASE_FOLDER, return_dict=True)

# Select participant ID
id = '02---nokia,-white-watch'
labfront_id = id_dict[id]

start_dt = datetime.datetime(2023,1,24)
end_dt = datetime.datetime(2023,1,25)

p_data = data.load_garmin_connect_body_composition(BASE_FOLDER,
                                             id + '_' + labfront_id,
                                             start_dt,
                                             end_dt)

print(p_data.head())

#plt.figure()
#plt.plot(p_data.isoDate.dt.tz_localize(None), p_data.bbi)
#plt.xlim([start_dt, end_dt])
#plt.show()