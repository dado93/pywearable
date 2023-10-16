import datetime
from typing import Union

import pandas as pd


class BaseLoader:
    def load_heart_rate(
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        pass
