import datetime
from typing import Union

import pandas as pd

from ..base import BaseLoader


class TryTerraLoader(BaseLoader):
    def __init__(self, data_folder) -> None:
        self.data_folder = data_folder
        pass

    def load_sleep_summary(
        self,
        user_id: str,
        start_date: Union(datetime.datetime, datetime.date, str, None) = None,
        end_date: Union(datetime.datetime, datetime.date, str, None) = None,
    ) -> pd.DataFrame:
        pass
