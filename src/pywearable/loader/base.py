import datetime
from typing import Union

import pandas as pd

from .. import constants


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
        raise NotImplementedError

    def load_sleep_summary(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def load_sleep_stage(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def load_heart_rate(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        raise NotImplementedError

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
        raise NotImplementedError

    def load_hypnogram(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        resolution: float = 1,
        map_hypnogram: bool = True,
    ) -> pd.DataFrame:
        """Load hypnogram for given user for a given day.

        This function allows to load sleep hypnograms starting from sleep data
        with a given resolution in minutes. The function returns a
        dictionary, with each key being a :class:`datetime.date`, and each value
        a :class:`numpy.array` that contains the hypnogram values.
        The hypnogram can be kept with standard Garmin values for sleep stages,
        or these values can be mapped to number according to the following
        convention:

            - unmeasurable -> -1
            - awake -> 0
            - light -> 1
            - deep -> 3
            - rem -> 4

        Parameters
        ----------
        user_id : str
            Unique identifier of the user.
        start_date : str or datetime.date or datetime.date or None
            Start date for hypnogram loading.
        end_date : str or datetime.date or datetime.date or None
            End date for hypnogram loading.
        resolution : int, optional
            Desired resolution (in minutes) requested for the hypnogram, by default 1

        Returns
        -------
        dict
            Dictionary with hypnogram values, one per each day.

        Raises
        ------
        ValueError
            If date is passed as str and cannot be parsed.
        """

        # Load sleep summary and sleep stages data
        sleep_summaries = self.load_sleep_summary(
            user_id=user_id, start_date=start_date, end_date=end_date
        )

        if len(sleep_summaries) == 0:
            return {}

        sleep_start_time = sleep_summaries.iloc[0][constants._ISODATE_COL]

        sleep_end_time = pd.to_datetime(
            (
                sleep_summaries.iloc[-1][constants._UNIXTIMESTAMP_IN_MS_COL]
                + sleep_summaries.iloc[-1][constants._TIMEZONEOFFSET_IN_MS_COL]
                + sleep_summaries.iloc[-1][constants._SLEEP_SUMMARY_DURATION_IN_MS_COL]
                + sleep_summaries.iloc[-1][
                    constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL
                ]
            ),
            unit="ms",
            utc=True,
        ).tz_localize(None)

        sleep_start_time = sleep_start_time.to_pydatetime()
        sleep_end_time = sleep_end_time.to_pydatetime()

        sleep_stages = self.load_sleep_stage(
            user_id=user_id,
            start_date=sleep_start_time,
            end_date=sleep_end_time,
        )

        # Keep only sleep stages with correct sleep summaries
        sleep_stages = (
            sleep_stages[
                sleep_stages[constants._SLEEP_STAGE_SLEEP_SUMMARY_ID_COL].isin(
                    sleep_summaries[
                        constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL
                    ].unique()
                )
            ]
            .sort_values(by=[constants._UNIXTIMESTAMP_IN_MS_COL])
            .reset_index(drop=True)
        )

        # set index on sleep summaries
        sleep_summaries = sleep_summaries.set_index(
            constants._SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL
        )
        hypnograms = {}
        for sleep_summary_id, sleep_summary in sleep_summaries.iterrows():
            calendar_day = sleep_summary[constants._CALENDAR_DATE_COL]
            sleep_start_time = sleep_summary[constants._ISODATE_COL]
            sleep_end_time = pd.to_datetime(
                (
                    sleep_summary[constants._UNIXTIMESTAMP_IN_MS_COL]
                    + sleep_summary[constants._TIMEZONEOFFSET_IN_MS_COL]
                    + sleep_summary[constants._SLEEP_SUMMARY_DURATION_IN_MS_COL]
                    + sleep_summary[constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL]
                ),
                unit="ms",
                utc=True,
            ).tz_localize(None)

            intervals = int(
                divmod(
                    (sleep_end_time - sleep_start_time).total_seconds(), 60 * resolution
                )[0]
            )
            time_delta_intervals = [
                sleep_start_time + i * datetime.timedelta(minutes=resolution)
                for i in range(intervals)
            ]

            daily_sleep_stages = sleep_stages.loc[
                sleep_stages[constants._SLEEP_STAGE_SLEEP_SUMMARY_ID_COL]
                == sleep_summary_id
            ]

            hypnogram = pd.DataFrame(
                data={constants._ISODATE_COL: time_delta_intervals}
            )

            hypnogram = hypnogram.merge(
                daily_sleep_stages.loc[
                    :,
                    [
                        constants._ISODATE_COL,
                        constants._SLEEP_STAGE_SLEEP_TYPE_COL,
                    ],
                ],
                how="left",
                on=constants._ISODATE_COL,
            )

            hypnogram[constants._SLEEP_STAGE_SLEEP_TYPE_COL] = hypnogram.loc[
                :, constants._SLEEP_STAGE_SLEEP_TYPE_COL
            ].ffill()
            if map_hypnogram:
                hypnogram[constants._SLEEP_STAGE_SLEEP_TYPE_COL] = hypnogram[
                    constants._SLEEP_STAGE_SLEEP_TYPE_COL
                ].map(
                    {
                        constants._SLEEP_STAGE_REM_STAGE_VALUE: constants._SLEEP_STAGE_REM_STAGE_MAPPED_VALUE,
                        constants._SLEEP_STAGE_AWAKE_STAGE_VALUE: constants._SLEEP_STAGE_AWAKE_STAGE_MAPPED_VALUE,
                        constants._SLEEP_STAGE_N3_STAGE_VALUE: constants._SLEEP_STAGE_N3_STAGE_MAPPED_VALUE,
                        constants._SLEEP_STAGE_N1_STAGE_VALUE: constants._SLEEP_STAGE_N1_STAGE_MAPPED_VALUE,
                        constants._SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE: constants._SLEEP_STAGE_UNMEASURABLE_STAGE_MAPPED_VALUE,
                    }
                )
            hypnograms[calendar_day] = {}
            hypnograms[calendar_day]["start_time"] = sleep_start_time.to_pydatetime()
            hypnograms[calendar_day]["end_time"] = sleep_end_time.to_pydatetime()
            hypnograms[calendar_day]["values"] = hypnogram[
                constants._SLEEP_STAGE_SLEEP_TYPE_COL
            ].values

        return hypnograms

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
