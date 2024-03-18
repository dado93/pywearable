import datetime
from typing import Union

import pandas as pd


class BaseLoader:
    """Abstract class for the implementation of loader classes."""

    def __init__(self):
        pass

    def load_daily_summary(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        pass

    def load_sleep_summary(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        pass

    def load_sleep_stage(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        pass

    def load_heart_rate(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        pass

    def load_pulse_ox(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def load_respiration(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        """Load respiration data.

        This function loads respiration data from
        a given user and for a given time frame, from
        ``start_date`` to ``end_date``.

        Parameters
        ----------
        user_id : str
            User id for which data have to be loaded.
        start_date : datetime.datetime or datetime.date or str or None, optional
            Start date for data retrieval, by default None
        end_date : datetime.datetime or datetime.date or str or None, optional
            End date for data retrieval, by default None

        Returns
        -------
        :class:`pd.DataFrame`
            DataFrame with respiration data.

        Raises
        ------
        NotImplementedError
            Method must be implement by loaders.
        """
        raise NotImplementedError

    def load_sleep_pulse_ox(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        """Load sleep pulse ox data.

        This function loads sleep pulse ox data from
        a given user and for a given time frame, from
        ``start_date`` to ``end_date``.

        Parameters
        ----------
        user_id : str
            User id for which data have to be loaded.
        start_date : datetime.datetime or datetime.date or str or None, optional
            Start date for data retrieval, by default None
        end_date : datetime.datetime or datetime.date or str or None, optional
            End date for data retrieval, by default None

        Returns
        -------
        :class:`pd.DataFrame`
            DataFrame with sleep pulse ox data.

        Raises
        ------
        NotImplementedError
            Method must be implement by loaders.
        """
        raise NotImplementedError

    def load_sleep_respiration(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        """Load sleep respiration data.

        This function loads sleep respiration data from
        a given user and for a given time frame, from
        ``start_date`` to ``end_date``.

        Parameters
        ----------
        user_id : str
            User id for which data have to be loaded.
        start_date : datetime.datetime or datetime.date or str or None, optional
            Start date for data retrieval, by default None
        end_date : datetime.datetime or datetime.date or str or None, optional
            End date for data retrieval, by default None

        Returns
        -------
        :class:`pd.DataFrame`
            DataFrame with sleep respiration data.

        Raises
        ------
        NotImplementedError
            Method must be implement by loaders.
        """
        raise NotImplementedError

    def load_bbi(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        pass

    def get_user_ids(self) -> list:
        """Get list of available user IDs.

        This function is used in sub-modules when
        the ``user_id`` parameter is set to ``"all"``.

        Returns
        -------
        :class:`list`
            List of available user IDs.
        """
        pass
