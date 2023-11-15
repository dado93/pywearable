import datetime
import os
from pathlib import Path
from typing import Union

import pandas as pd

from ..base import BaseLoader


class TryTerraExportLoader(BaseLoader):
    def __init__(self, data_folder: Union[str, Path]) -> None:
        self.data_folder = data_folder
        try:
            self.data_folder = Path(self.data_folder)
            if not self.data_folder.is_dir():
                raise ValueError(f"{self.data_folder} is not a folder.")
        except:
            raise ValueError(f"f{self.data_folder} is not a valid path.")
        self.user_ids = [x.name for x in self.data_folder.iterdir() if x.is_dir()]

        # Let's create a dictionary with information retrieved from the metadata
        # field in the JSON files
        # - start
        # - end time stamp

    def get_user_ids(self) -> list:
        return self.user_ids

    def load_sleep_summary(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        same_day_filter: bool = True,
    ) -> pd.DataFrame:
        # TODO add check on user-id
        pass
