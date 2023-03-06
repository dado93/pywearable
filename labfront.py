import utils
from pathlib import Path

BASE_FOLDER = Path('data') / 'sample_data' / \
    '9dbabd13-879e-4131-a562-66a2501435ab'

ids, lf_ids = utils.get_ids(BASE_FOLDER)
print(ids)

print(lf_ids)
