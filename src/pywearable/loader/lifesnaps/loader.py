import datetime
import warnings
from typing import Union

import numpy as np
import pandas as pd

try:
    import pymongo
    from bson.objectid import ObjectId
except ImportError:
    warnings.warn(
        "pymongo is required when using LifeSnapsLoader", category=ImportWarning
    )

from ... import constants, utils
from ..base import BaseLoader
from ..lifesnaps import constants as lifesnaps_constants

_METRIC_KEY = "metric"
_METRIC_START_DATE_KEY = "start_date"
_METRIC_END_DATE_KEY = "end_date"
_METRIC_COLLECTION_KEY = "collection"
_METRIC_ID_KEY = "id"
_METRIC_DATE_FORMAT_KEY = "date_format"

_METRIC_DICT = {
    lifesnaps_constants._METRIC_COMP_TEMP: {
        "metric_key": lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_TYPE_COMP_TEMP,
        "start_date_key": lifesnaps_constants._DB_FITBIT_COLLECTION_COMP_TEMP_SLEEP_START_KEY,
        "end_date_key": lifesnaps_constants._DB_FITBIT_COLLECTION_COMP_TEMP_SLEEP_END_KEY,
    },
    lifesnaps_constants._METRIC_SPO2: {
        "metric_key": lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_TYPE_DAILY_SPO2,
        "start_date_key": lifesnaps_constants._DB_FITBIT_COLLECTION_SPO2_TIMESTAMP_KEY,
    },
    lifesnaps_constants._METRIC_STEPS: {
        "metric_key": lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_TYPE_STEPS,
        "start_date_key": lifesnaps_constants._DB_FITBIT_COLLECTION_STEPS_DATETIME_COL,
        _METRIC_DATE_FORMAT_KEY: "%Y-%m-%dT%H:%M:%S",
    },
    # Questionnaires
    # - BREQ
    lifesnaps_constants._METRIC_QUESTIONNAIRE_BREQ: {
        _METRIC_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATA_TYPE_BREQ,
        _METRIC_START_DATE_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_KEY,
        _METRIC_COLLECTION_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_NAME,
        _METRIC_ID_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_USER_KEY,
        _METRIC_DATE_FORMAT_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_FORMAT,
    },
    # - STAI
    lifesnaps_constants._METRIC_QUESTIONNAIRE_STAI: {
        _METRIC_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATA_TYPE_STAI,
        _METRIC_START_DATE_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_KEY,
        _METRIC_COLLECTION_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_NAME,
        _METRIC_ID_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_USER_KEY,
        _METRIC_DATE_FORMAT_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_FORMAT,
    },
    # - PANAS
    lifesnaps_constants._METRIC_QUESTIONNAIRE_PANAS: {
        _METRIC_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATA_TYPE_PANAS,
        _METRIC_START_DATE_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_KEY,
        _METRIC_COLLECTION_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_NAME,
        _METRIC_ID_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_USER_KEY,
        _METRIC_DATE_FORMAT_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_FORMAT,
    },
    # - PERSONALITY
    lifesnaps_constants._METRIC_QUESTIONNAIRE_PERSONALITY: {
        _METRIC_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATA_TYPE_BFPT,
        _METRIC_START_DATE_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_KEY,
        _METRIC_COLLECTION_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_NAME,
        _METRIC_ID_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_USER_KEY,
        _METRIC_DATE_FORMAT_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_FORMAT,
    },
    # - STAGE AND PROCESSES OF CHANGE
    lifesnaps_constants._METRIC_QUESTIONNAIRE_TTM: {
        _METRIC_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATA_TYPE_TTMSPBF,
        _METRIC_START_DATE_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_KEY,
        _METRIC_COLLECTION_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_NAME,
        _METRIC_ID_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_USER_KEY,
        _METRIC_DATE_FORMAT_KEY: lifesnaps_constants._DB_SURVEYS_COLLECTION_DATE_FORMAT,
    },
}


class LifeSnapsLoader(BaseLoader):
    """Loader for LifeSnaps dataset.

    Parameters
    ----------
    host : str
        Host address of pymongo DB instance.
    port: int
        Port of the pymongo DB instance.
    """

    def __init__(self, host: str = "localhost", port: int = 27017):
        try:
            import pymongo
        except ImportError:
            raise ("pymongo is required to use LifeSnapsLoader.")
        self.host = host
        self.port = port
        self.client = pymongo.MongoClient(self.host, self.port)
        self.db = self.client[lifesnaps_constants._DB_NAME]
        self.fitbit_collection = self.db[lifesnaps_constants._DB_FITBIT_COLLECTION_NAME]
        self.surveys_collection = self.db[
            lifesnaps_constants._DB_SURVEYS_COLLECTION_NAME
        ]
        # self.sema_collection =

    def get_user_ids(self) -> list:
        """Get available user ids.

        This function gets available user ids in the DB.

        Returns
        -------
        list
            List of strings of unique user ids.
        """
        return [str(x) for x in self.fitbit_collection.distinct("id")]

    def get_full_id(self, user_id):
        # TODO remove this function, where do we use it?
        return user_id

    def load_sleep_summary(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        same_day_filter: bool = True,
    ) -> pd.DataFrame:
        """Load sleep summary data.

        This function load sleep summary data from the Mongo DB dataset.
        The returned data comes in the form of a :class:`pd.DataFrame`,
        with each row representing an unique entry of sleep data for
        the given `user_id`. If no sleep data are available for the
        provided `user_id`, then an empty :class:`pd.DataFrame` is
        returned.

        Parameters
        ----------
        user_id : :class:`str`
            Unique identifier for the user.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
            Start date for data retrieval, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
            End date for data retrieval, by default None
        same_day_filter: :class:`bool`
            Whether to return only a single sleep for each calendar date, by default True

        Returns
        -------
        :class:`pd.DataFrame`
            DataFrame with sleep summary data.

        Raises
        ------
        ValueError
            If `user_id` is not valid or dates are not consistent.
        """
        if str(user_id) not in self.get_user_ids():
            raise ValueError(f"f{user_id} does not exist in DB.")
        # Check users
        user_id = self._check_user_id(user_id)
        start_date = utils.check_date(start_date)
        end_date = utils.check_date(end_date)
        # Get some constants for ease of access
        date_of_sleep_key = f"{lifesnaps_constants._DB_DATA_KEY}"
        date_of_sleep_key += (
            f".{lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_DATE_OF_SLEEP_KEY}"
        )
        start_sleep_key = f"{lifesnaps_constants._DB_DATA_KEY}"
        start_sleep_key += (
            f".{lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_START_TIME_KEY}"
        )
        # Set up filter for dates and times
        date_filter = self._get_start_and_end_date_time_filter_dict(
            start_date_key=date_of_sleep_key,
            start_date=start_date,
            end_date=end_date,
            end_date_key=None,
        )
        # Aggregate data
        filtered_coll = self.fitbit_collection.aggregate(
            [
                {
                    "$match": {
                        lifesnaps_constants._DB_TYPE_KEY: lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_TYPE_SLEEP,
                        lifesnaps_constants._DB_ID_KEY: user_id,
                    }
                },
                {
                    "$addFields": {
                        date_of_sleep_key: {
                            "$convert": {
                                "input": f"${date_of_sleep_key}",
                                "to": "date",
                            }
                        },
                        start_sleep_key: {
                            "$convert": {
                                "input": f"${start_sleep_key}",
                                "to": "date",
                            }
                        },
                    }
                },
                date_filter,
            ]
        )
        # Convert to dataframe
        sleep_summary_df = pd.DataFrame()
        for sleep_summary in filtered_coll:
            # For each row, save all fields except sleep levels
            filtered_dict = {
                k: sleep_summary[lifesnaps_constants._DB_DATA_KEY][k]
                for k in set(
                    list(sleep_summary[lifesnaps_constants._DB_DATA_KEY].keys())
                )
                - set(["levels"])
            }
            # Create a pd.DataFrame with sleep summary data
            temp_df = pd.DataFrame(
                filtered_dict,
                index=[
                    sleep_summary[lifesnaps_constants._DB_DATA_KEY][
                        lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY
                    ]
                ],
            )
            # Get sleep stages
            sleep_stages_df = self._merge_sleep_data_and_sleep_short_data(sleep_summary)
            # Get duration for each sleep stage
            sleep_stages_duration = sleep_stages_df.groupby(
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_LEVEL_KEY
            )[
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_SECONDS_KEY
            ].sum()
            # Create dictionary with sleep_stage : duration column name
            stage_value_col_dict = {
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_DEEP_VALUE: constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL,
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_LIGHT_VALUE: constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL,
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_REM_VALUE: constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL,
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_WAKE_VALUE: constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL,
            }
            # Save stage duration in sleep summary with ms unit
            for sleep_stage in stage_value_col_dict.keys():
                if sleep_stage in sleep_stages_duration.index:
                    temp_df[stage_value_col_dict[sleep_stage]] = (
                        sleep_stages_duration.loc[sleep_stage] * 1000
                    )
                else:
                    temp_df[stage_value_col_dict[sleep_stage]] = 0

            sleep_summary_df = pd.concat((sleep_summary_df, temp_df), ignore_index=True)
        if len(sleep_summary_df) > 0:
            # Set up columns according to pywearable format
            sleep_summary_df[constants._TIMEZONEOFFSET_IN_MS_COL] = 0
            sleep_summary_df[
                constants._SLEEP_SUMMARY_UNMEASURABLE_SLEEP_DURATION_IN_MS_COL
            ] = 0
            sleep_summary_df[
                constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL
            ] = np.nan

            sleep_summary_df = sleep_summary_df.rename(
                columns={
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_START_TIME_KEY: constants._ISODATE_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_DATE_OF_SLEEP_KEY: constants._CALENDAR_DATE_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY: constants._SLEEP_SUMMARY_ID_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_DURATION_KEY: constants._DURATION_IN_MS_COL,
                }
            )

            sleep_summary_df[constants._DURATION_IN_MS_COL] = (
                sleep_summary_df[constants._DURATION_IN_MS_COL]
                - sleep_summary_df[constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL]
            )

            sleep_summary_df[constants._UNIXTIMESTAMP_IN_MS_COL] = (
                sleep_summary_df[constants._ISODATE_COL] - pd.Timestamp("1970-01-01")
            ) // pd.Timedelta("1ms")

            sleep_summary_df = sleep_summary_df.sort_values(
                by=constants._CALENDAR_DATE_COL, ignore_index=True
            )

            if same_day_filter:
                # Keep only sleep summary with main sleep as True
                sleep_summary_df = sleep_summary_df[
                    sleep_summary_df[
                        lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_MAIN_SLEEP_KEY
                    ]
                    == True
                ].reset_index(drop=True)
                # Keep sleep summary with longest duration
                sleep_summary_df = sleep_summary_df.sort_values(
                    [constants._CALENDAR_DATE_COL, constants._DURATION_IN_MS_COL],
                    ascending=True,
                    ignore_index=True,
                )
                sleep_summary_df = sleep_summary_df.drop_duplicates(
                    subset=[constants._CALENDAR_DATE_COL],
                    keep="last",
                    ignore_index=True,
                )

            # Reorder sleep summary columns
            sleep_summary_df = sleep_summary_df.loc[
                :,
                [
                    constants._SLEEP_SUMMARY_ID_COL,
                    constants._TIMEZONEOFFSET_IN_MS_COL,
                    constants._UNIXTIMESTAMP_IN_MS_COL,
                    constants._ISODATE_COL,
                    constants._CALENDAR_DATE_COL,
                    constants._DURATION_IN_MS_COL,
                    constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL,
                    constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL,
                    constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL,
                    constants._SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL,
                    constants._SLEEP_SUMMARY_UNMEASURABLE_SLEEP_DURATION_IN_MS_COL,
                    constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL,
                ],
            ]
        return sleep_summary_df

    def _merge_sleep_data_and_sleep_short_data(self, sleep_entry: dict) -> pd.DataFrame:
        # Get data
        sleep_data_dict = sleep_entry[lifesnaps_constants._DB_DATA_KEY][
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY
        ][lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_KEY]
        # Create a pd.DataFrame with sleep data
        sleep_data_df = pd.DataFrame(sleep_data_dict)
        if not (
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SHORT_DATA_KEY
            in sleep_entry[lifesnaps_constants._DB_DATA_KEY][
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY
            ].keys()
        ):
            return sleep_data_df
        sleep_short_data_list = sleep_entry[lifesnaps_constants._DB_DATA_KEY][
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY
        ][lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SHORT_DATA_KEY]
        # Just store column names
        datetime_col = (
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_DATETIME_KEY
        )
        seconds_col = (
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_SECONDS_KEY
        )
        level_col = (
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_LEVEL_KEY
        )
        # Create a pd.DataFrame with sleep data

        # We need to inject sleep short data in data
        # 1. Get start and end of sleep from sleep data
        sleep_data_df[datetime_col] = pd.to_datetime(sleep_data_df[datetime_col])
        sleep_start_dt = sleep_data_df.iloc[0][datetime_col]
        sleep_end_dt = sleep_data_df.iloc[-1][datetime_col] + datetime.timedelta(
            seconds=int(sleep_data_df.iloc[-1][seconds_col])
        )

        sleep_data_df = sleep_data_df.set_index(datetime_col)

        # 2. Create new list with short data using 30 seconds windows
        sleep_short_data_list_copy = []
        for sleep_short_data_entry in sleep_short_data_list:
            start_dt = datetime.datetime.strptime(
                sleep_short_data_entry[datetime_col], "%Y-%m-%dT%H:%M:%S.%f"
            )
            if sleep_short_data_entry[seconds_col] > 30:
                n_to_add = int(sleep_short_data_entry[seconds_col] / 30)
                for i in range(n_to_add):
                    sleep_short_data_list_copy.append(
                        {
                            datetime_col: start_dt + i * datetime.timedelta(seconds=30),
                            level_col: lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_WAKE_VALUE,
                            seconds_col: 30,
                        }
                    )
            else:
                sleep_short_data_list_copy.append(
                    {
                        datetime_col: start_dt,
                        level_col: lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_WAKE_VALUE,
                        seconds_col: sleep_short_data_entry[seconds_col],
                    }
                )
        # 3. Create DataFrame with sleep short data and get start and end sleep data
        sleep_short_data_df = pd.DataFrame(sleep_short_data_list_copy)
        sleep_short_data_df[datetime_col] = pd.to_datetime(
            sleep_short_data_df[datetime_col]
        )
        sleep_short_data_start_dt = sleep_short_data_df.iloc[0][datetime_col]
        sleep_short_data_end_dt = sleep_short_data_df.iloc[-1][
            datetime_col
        ] + datetime.timedelta(seconds=int(sleep_short_data_df.iloc[-1][seconds_col]))
        sleep_short_data_df = sleep_short_data_df.set_index(datetime_col)

        # 4. Let's create a new dataframe that goes from min sleep time to max sleep time
        min_sleep_dt = (
            sleep_start_dt
            if sleep_start_dt < sleep_short_data_start_dt
            else sleep_short_data_start_dt
        )
        max_sleep_dt = (
            sleep_end_dt
            if sleep_end_dt > sleep_short_data_end_dt
            else sleep_short_data_end_dt
        )

        new_sleep_data_df_index = pd.Index(
            [
                min_sleep_dt + i * datetime.timedelta(seconds=30)
                for i in range(int((max_sleep_dt - min_sleep_dt).total_seconds() / 30))
            ]
        )
        new_sleep_data_df = pd.DataFrame(index=new_sleep_data_df_index)
        new_sleep_data_df.loc[new_sleep_data_df.index, level_col] = sleep_data_df[
            level_col
        ]
        new_sleep_data_df[level_col] = new_sleep_data_df.ffill()
        new_sleep_data_df[seconds_col] = 30

        # 5. Inject short data into new dataframe
        new_sleep_data_df.loc[
            sleep_short_data_df.index, level_col
        ] = sleep_short_data_df[level_col]

        # 6. Create new column with levels and another one for their changes
        new_sleep_data_df["levelMap"] = pd.factorize(new_sleep_data_df[level_col])[0]
        new_sleep_data_df["levelMapDiff"] = new_sleep_data_df["levelMap"].diff()

        # 7. Create new column with id for each sleep stage
        new_sleep_data_df["levelGroup"] = (
            new_sleep_data_df["levelMap"] != new_sleep_data_df["levelMap"].shift()
        ).cumsum()
        new_sleep_data_df = new_sleep_data_df.reset_index(names=datetime_col)
        # 8. Get rows when change is detected
        final_sleep_df = (
            new_sleep_data_df[new_sleep_data_df["levelMapDiff"] != 0]
            .copy()
            .reset_index(drop=True)
        )

        # 9. Get total seconds with isoDate information
        final_sleep_df[seconds_col] = (
            (
                new_sleep_data_df.groupby("levelGroup")[datetime_col].last()
                + datetime.timedelta(seconds=30)
                - new_sleep_data_df.groupby("levelGroup")[datetime_col].first()
            )
            .dt.total_seconds()
            .reset_index(drop=True)
        )
        sleep_data_df = final_sleep_df.copy()

        sleep_data_df = sleep_data_df.drop(
            ["levelMap", "levelMapDiff", "levelGroup"], axis=1
        )
        return sleep_data_df

    def load_sleep_stage(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        include_short_data: bool = True,
    ) -> pd.DataFrame:
        """Load sleep stage data.

        This function loads sleep stage data for a given user
        and timeframe. If ``include_short_data`` is `True`, then
        also sleep stages with a duration lower than 30 seconds
        are returned.


        Parameters
        ----------
        user_id : :class:`str`
            Unique identifier for the user.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
            Start date for data retrieval, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
            End date for data retrieval, by default None

        Returns
        -------
        :class:`pd.DataFrame`
            DataFrame with sleep stages data.

        Raises
        ------
        ValueError
            If user or dates are invalid.
        """
        # We need to load sleep data -> then levels.data and levels.shortData
        # After getting levels.shortData, we merge everything together
        # with 30 seconds resolution
        if str(user_id) not in self.get_user_ids():
            raise ValueError(f"f{user_id} does not exist in DB.")
        user_id = self._check_user_id(user_id)
        start_date = utils.check_date(start_date)
        end_date = utils.check_date(end_date)
        if not utils.check_start_and_end_dates(start_date, end_date):
            raise ValueError(f"{start_date} is greater than {end_date}")
        # Get sleep start key
        sleep_start_key = f"{lifesnaps_constants._DB_DATA_KEY}"
        sleep_start_key += (
            f".{lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_START_TIME_KEY}"
        )
        date_filter = self._get_start_and_end_date_time_filter_dict(
            start_date_key=sleep_start_key,
            end_date_key=None,
            start_date=start_date,
            end_date=end_date,
        )
        filtered_coll = self.fitbit_collection.aggregate(
            [
                {
                    "$match": {
                        lifesnaps_constants._DB_TYPE_KEY: lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_TYPE_SLEEP,
                        lifesnaps_constants._DB_ID_KEY: user_id,
                    }
                },
                {
                    "$addFields": {
                        sleep_start_key: {
                            "$convert": {
                                "input": f"${sleep_start_key}",
                                "to": "date",
                            }
                        }
                    }
                },
                date_filter,
            ]
        )
        # Convert to dataframe
        sleep_stage_df = pd.DataFrame()
        for sleep_entry in filtered_coll:
            # Get shortData if they are there
            if include_short_data:
                sleep_data_df = self._merge_sleep_data_and_sleep_short_data(sleep_entry)
            else:
                # Get data
                sleep_data_dict = sleep_entry[lifesnaps_constants._DB_DATA_KEY][
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY
                ][lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_KEY]
                # Create a pd.DataFrame with sleep data
                sleep_data_df = pd.DataFrame(sleep_data_dict)
                # Add log id to pd.DataFrame
            sleep_data_df[
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY
            ] = sleep_entry[lifesnaps_constants._DB_DATA_KEY][
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY
            ]

            sleep_stage_df = pd.concat(
                (sleep_stage_df, sleep_data_df), ignore_index=True
            )
        if len(sleep_stage_df) > 0:
            # Get isodate column
            sleep_stage_df[constants._ISODATE_COL] = pd.to_datetime(
                sleep_stage_df[
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_DATETIME_KEY
                ],
                utc=True,
            ).dt.tz_localize(None)

            sleep_stage_df = sleep_stage_df.drop(
                [
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_DATETIME_KEY
                ],
                axis=1,
            )
            # Get unix timestamp in milliseconds
            sleep_stage_df[constants._UNIXTIMESTAMP_IN_MS_COL] = (
                sleep_stage_df[constants._ISODATE_COL] - pd.Timestamp("1970-01-01")
            ) // pd.Timedelta("1ms")

            sleep_stage_df = sleep_stage_df.sort_values(
                by=constants._UNIXTIMESTAMP_IN_MS_COL
            ).reset_index(drop=True)

            sleep_stage_df = sleep_stage_df.rename(
                columns={
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY: constants._SLEEP_SUMMARY_ID_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_SECONDS_KEY: constants._DURATION_IN_MS_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_LEVEL_KEY: constants._SLEEP_STAGE_SLEEP_TYPE_COL,
                }
            )
            sleep_stage_df[constants._TIMEZONEOFFSET_IN_MS_COL] = 0
            # Convert duration to milliseconds
            sleep_stage_df[constants._DURATION_IN_MS_COL] *= 1000
            sleep_stage_df[constants._SLEEP_STAGE_SLEEP_TYPE_COL] = sleep_stage_df[
                constants._SLEEP_STAGE_SLEEP_TYPE_COL
            ].map(
                {
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_REM_VALUE: constants._SLEEP_STAGE_REM_STAGE_VALUE,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_LIGHT_VALUE: constants._SLEEP_STAGE_N1_STAGE_VALUE,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_DEEP_VALUE: constants._SLEEP_STAGE_N3_STAGE_VALUE,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_WAKE_VALUE: constants._SLEEP_STAGE_AWAKE_STAGE_VALUE,
                }
            )
            sleep_stage_df = sleep_stage_df.loc[
                :,
                [
                    constants._SLEEP_SUMMARY_ID_COL,
                    constants._TIMEZONEOFFSET_IN_MS_COL,
                    constants._UNIXTIMESTAMP_IN_MS_COL,
                    constants._ISODATE_COL,
                    constants._DURATION_IN_MS_COL,
                    constants._SLEEP_STAGE_SLEEP_TYPE_COL,
                ],
            ]
        return sleep_stage_df

    def load_metric(
        self,
        metric: str,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        if str(user_id) not in self.get_user_ids():
            raise ValueError(f"f{user_id} does not exist in DB.")
        user_id = self._check_user_id(user_id)
        start_date = utils.check_date(start_date)
        end_date = utils.check_date(end_date)

        metric_start_key = _METRIC_DICT[metric][_METRIC_START_DATE_KEY]
        if _METRIC_END_DATE_KEY in _METRIC_DICT[metric].keys():
            metric_end_key = _METRIC_DICT[metric][_METRIC_END_DATE_KEY]
        else:
            metric_end_key = None
        if metric_start_key is None:
            metric_start_date_key_db = None
        else:
            metric_start_date_key_db = (
                lifesnaps_constants._DB_DATA_KEY + "." + metric_start_key
            )
        if metric_end_key is None:
            metric_end_date_key_db = None
        else:
            metric_end_date_key_db = (
                lifesnaps_constants._DB_DATA_KEY + "." + metric_end_key
            )
        if _METRIC_ID_KEY in _METRIC_DICT[metric].keys():
            user_id_key = _METRIC_DICT[metric][_METRIC_ID_KEY]
        else:
            user_id_key = lifesnaps_constants._DB_ID_KEY
        if metric_end_key is None:
            metric_end_date_key_db = None
        else:
            metric_end_date_key_db = (
                lifesnaps_constants._DB_DATA_KEY + "." + metric_end_key
            )

        # Setup dictionary for date conversion
        if _METRIC_DATE_FORMAT_KEY in _METRIC_DICT[metric].keys():
            date_conversion_dict = self._get_date_conversion_dict(
                start_date_key=metric_start_date_key_db,
                end_date_key=metric_end_date_key_db,
                date_format=_METRIC_DICT[metric][_METRIC_DATE_FORMAT_KEY],
            )
        else:
            date_conversion_dict = self._get_date_conversion_dict(
                start_date_key=metric_start_date_key_db,
                end_date_key=metric_end_date_key_db,
            )
        # Setup dictionary to filter by time
        date_filter_dict = self._get_start_and_end_date_time_filter_dict(
            start_date_key=metric_start_date_key_db,
            end_date_key=metric_end_date_key_db,
            start_date=start_date,
            end_date=end_date,
        )

        if not _METRIC_COLLECTION_KEY in _METRIC_DICT[metric].keys():
            collection = self.fitbit_collection
        else:
            if _METRIC_DICT[metric][_METRIC_COLLECTION_KEY] == "surveys":
                collection = self.surveys_collection
            elif _METRIC_DICT[metric][_METRIC_COLLECTION_KEY] == "fitbit":
                collection = self.fitbit_collection
            else:
                raise ValueError("Could not find valid collection for metric {metric}")
        filtered_coll = collection.aggregate(
            [
                {
                    "$match": {
                        lifesnaps_constants._DB_TYPE_KEY: _METRIC_DICT[metric][
                            _METRIC_KEY
                        ],
                        user_id_key: user_id,
                    }
                },
                date_conversion_dict,
                date_filter_dict,
            ]
        )
        metric_df = pd.DataFrame()
        list_of_metric_dict = [
            entry[lifesnaps_constants._DB_DATA_KEY] for entry in filtered_coll
        ]
        metric_df = pd.json_normalize(list_of_metric_dict)
        if len(metric_df) > 0:
            if metric_start_key is not None:
                metric_df = metric_df.sort_values(by=metric_start_key).reset_index(
                    drop=True
                )
        metric_df = self._setup_datetime_columns(df=metric_df, metric=metric)
        metric_df = self._reorder_datetime_columns(metric_df)
        return metric_df

    def load_steps(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        steps = self.load_metric(
            metric=lifesnaps_constants._METRIC_STEPS,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        if len(steps) > 0:
            steps = steps.rename(
                columns={
                    lifesnaps_constants._DB_FITBIT_COLLECTION_STEPS_VALUE_COL: constants._STEPS_STEPS_COL
                }
            )
            # Compute daily steps column
            steps[constants._CALENDAR_DATE_COL] = pd.to_datetime(
                steps[constants._ISODATE_COL].dt.strftime("%Y-%m-%d"),
            )
            steps[constants._STEPS_STEPS_COL] = steps[
                constants._STEPS_STEPS_COL
            ].astype("int64")
            steps[constants._STEPS_TOTAL_STEPS_COL] = steps.groupby(
                [constants._CALENDAR_DATE_COL]
            )[constants._STEPS_STEPS_COL].cumsum()
            steps = steps.drop([constants._CALENDAR_DATE_COL], axis=1)
        return steps

    def _get_start_and_end_date_time_filter_dict(
        self, start_date_key, end_date_key=None, start_date=None, end_date=None
    ) -> dict:
        if end_date_key is None:
            end_date_key = start_date_key
        if (not (start_date is None)) and (not (end_date is None)):
            if end_date < start_date:
                raise ValueError(f"{end_date} must be greater than {start_date}")
            date_filter = {
                "$match": {
                    "$and": [
                        {start_date_key: {"$gte": start_date}},
                        {end_date_key: {"$lte": end_date}},
                    ]
                }
            }
        elif (start_date is None) and (not (end_date is None)):
            date_filter = {"$match": {end_date_key: {"$lte": end_date}}}
        elif (not (start_date is None)) and (end_date is None):
            date_filter = {"$match": {start_date_key: {"$gte": start_date}}}
        else:
            date_filter = {"$match": {}}

        return date_filter

    def _get_date_conversion_dict(
        self, start_date_key, end_date_key=None, date_format="%Y-%m-%dT%H:%M%S.%f"
    ) -> dict:
        if start_date_key is None:
            date_conversion_dict = {"$addFields": {}}
        else:
            if not end_date_key is None:
                date_conversion_dict = {
                    "$addFields": {
                        start_date_key: {
                            "$dateFromString": {
                                "dateString": f"${start_date_key}",
                                "format": date_format,
                            }
                        },
                        end_date_key: {
                            "$dateFromString": {
                                "dateString": f"${end_date_key}",
                                "format": date_format,
                            }
                        },
                    }
                }
            else:
                date_conversion_dict = {
                    "$addFields": {
                        start_date_key: {
                            "$dateFromString": {
                                "dateString": f"${start_date_key}",
                                "format": date_format,
                            }
                        },
                    }
                }
        return date_conversion_dict

    def _setup_datetime_columns(self, df: pd.DataFrame, metric: str):
        if len(df) > 0:
            if _METRIC_START_DATE_KEY in _METRIC_DICT[metric].keys():
                if not (_METRIC_DICT[metric][_METRIC_START_DATE_KEY] is None):
                    df = df.rename(
                        columns={
                            _METRIC_DICT[metric][
                                _METRIC_START_DATE_KEY
                            ]: constants._ISODATE_COL
                        }
                    )
                    df[constants._UNIXTIMESTAMP_IN_MS_COL] = df[
                        constants._ISODATE_COL
                    ].apply(lambda x: int(x.timestamp() * 1000))
                    df[constants._TIMEZONEOFFSET_IN_MS_COL] = 0
        return df

    def _reorder_datetime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reorder date and time columns in dataframe.

        This function reorders the columns in a
        dataframe to the default ordering of:

        - timezoneOffsetInMs
        - unixTimestampInMs
        - isoDate

        Parameters
        ----------
        df : :class:`pd.DataFrame`
            DataFrame for which columns order has to be changed.

        Returns
        -------
        :class:`pd.DataFrame`
            DataFrame with columns order changed.
        """
        if len(df) > 0:
            if {
                constants._ISODATE_COL,
                constants._UNIXTIMESTAMP_IN_MS_COL,
                constants._TIMEZONEOFFSET_IN_MS_COL,
            }.issubset(df.columns):
                for col_idx, col in enumerate(
                    [
                        constants._TIMEZONEOFFSET_IN_MS_COL,
                        constants._UNIXTIMESTAMP_IN_MS_COL,
                        constants._ISODATE_COL,
                    ]
                ):
                    df.insert(col_idx, col, df.pop(col))
        return df

    def _check_user_id(self, user_id):
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)
        return user_id

    def load_questionnaire(
        self,
        user_id: str,
        questionnaire_name: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        """Loads a questionnaire from LifeSnaps dataset.

        This function loads a given questionnaire from the LifeSnaps
        dataset, and returns it into a formatted :class:`pd.DataFrame`.

        Parameters
        ----------
        user_id : :class:`str`
            Ths identifier of the user for which the questionnaire have to be loaded.
        questionnaire_name : :class:`str`
            Name of the questionnaire to be loaded. The value must be the same
            that is present in the MongoDB database.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            Start date for which the answers to the questionnaire have to be loaded, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            End date for which the answers to the questionnaire have to be loaded, by default None

        Returns
        -------
        :class:`pd.DataFrame`
            A formatted :class:`pd.DataFrame` with each row containing the answers to a given
            questionnaire request. Each column represents a given question, and the row values
            are the answer to the the question.
        """
        questionnaire_df = self.load_metric(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            metric=questionnaire_name,
        )
        return questionnaire_df

    def load_breq_questionnaire(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        map_questions: bool = True,
    ) -> pd.DataFrame:
        """Load BREQ questionnaire.

        This function loads the Behavioural Regulations in Exercise Questionnaire (BREQ)
        from a given user and dates. The functions returns the answers to the
        questionnaire in a :class:`pd.DataFrame`. The :class:`pd.DataFrame` contains
        one column per each questionnaire question, and the column values
        represent the answers to the questionaire. It is possible to map the
        column names (i.e., the questions) to the proper questionnaire questions
        by setting the ``map_questions`` parameter to ``True``. Otherwise, the default
        encoding used in the LifeSnaps is used for the column names:

            - engage[SQ001]: I exercise because other people say I should
            - engage[SQ002]: I feel guilty when I don't exercise
            - engage[SQ003]: I value the benefits of exercise
            - engage[SQ004]: I exercise because it's fun
            - engage[SQ005]: I don't see why I should have to exercise
            - engage[SQ006]: I take part in exercise because my friends/family/partner say I should
            - engage[SQ007]: I feel ashamed when I miss an exercise session
            - engage[SQ008]: It's important to me to exercise regularly
            - engage[SQ009]: I can't see why I should bother exercising
            - engage[SQ010]: I enjoy my exercise sessions
            - engage[SQ011]: I exercise because others will not be pleased with me if I don't
            - engage[SQ012]: I don't see the point in exercising
            - engage[SQ013]: I feel like a failure when I haven't exercised in a while
            - engage[SQ014]: I think it is important to make the effort to exercise regularly
            - engage[SQ015]: I find exercise a pleasurable activity
            - engage[SQ016]: I feel under pressure from my friends/family to exercise
            - engage[SQ017]: I get restless if I don't exercise regularly
            - engage[SQ018]: I get pleasure and satisfaction from participating in exercise
            - engage[SQ019]: I think exercising is a waste of time

        Parameters
        ----------
        user_id : :class:`str`
            Ths identifier of the user for which the BREQ questionnaire have to be loaded.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            Start date for which the answers to the BREQ questionnaire have to be loaded, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            End date for which the answers to the BREQ questionnaire have to be loaded, by default None
        map_questions: :class:`bool`, optional
            Whether to map the BREQ questions (``True``) or leave the default
            LifeSnaps encoding (``False``), by default True

        Returns
        -------
        :class:`pd.DataFrame`
            A formatted :class:`pd.DataFrame` with each row containing the answers to a given BREQ
            questionnaire request. Each column represents a given question, and the row values
            are the answer to the the question.
        """
        breq_questionnaire_df = self.load_metric(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            metric=lifesnaps_constants._METRIC_QUESTIONNAIRE_BREQ,
        )
        if map_questions:
            breq_questionnaire_df = breq_questionnaire_df.rename(
                columns={
                    "engage[SQ001]": "I exercise because other people say I should",
                    "engage[SQ002]": "I feel guilty when I don't exercise",
                    "engage[SQ003]": "I value the benefits of exercise",
                    "engage[SQ004]": "I exercise because it's fun",
                    "engage[SQ005]": "I don't see why I should have to exercise",
                    "engage[SQ006]": "I take part in exercise because my friends/family/partner say I should",
                    "engage[SQ007]": "I feel ashamed when I miss an exercise session",
                    "engage[SQ008]": "It's important to me to exercise regularly",
                    "engage[SQ009]": "I can't see why I should bother exercising",
                    "engage[SQ010]": "I enjoy my exercise sessions",
                    "engage[SQ011]": "I exercise because others will not be pleased with me if I don't",
                    "engage[SQ012]": "I don't see the point in exercising",
                    "engage[SQ013]": "I feel like a failure when I haven't exercised in a while",
                    "engage[SQ014]": "I think it is important to make the effort to exercise regularly",
                    "engage[SQ015]": "I find exercise a pleasurable activity",
                    "engage[SQ016]": "I feel under pressure from my friends/family to exercise",
                    "engage[SQ017]": "I get restless if I don't exercise regularly",
                    "engage[SQ018]": "I get pleasure and satisfaction from participating in exercise",
                    "engage[SQ019]": "I think exercising is a waste of time",
                }
            )

        return breq_questionnaire_df

    def load_panas_questionnaire(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        map_questions: bool = True,
    ) -> pd.DataFrame:
        """Load PANAS questionnaire.

        This function loads the Positive and Negative Affect Schedule (PANAS)
        questionnaire from a given user and dates. The PANAS questionnaire asks
        to *"Indicate the extent you have felt this way over the past week"*
        on a 5-point Likert scale (from *Very slightly or not at all* to *Extremely*).
        This function returns the answers to the questionnaire in a :class:`pd.DataFrame`.
        The :class:`pd.DataFrame` contains one column per each questionnaire question,
        and the column values represent the answers to the questionaire.
        It is possible to map the column names (i.e., the questions) to the
        proper questionnaire questions by setting the ``map_questions`` parameter to ``True``.
        Otherwise, the default encoding used in the LifeSnaps is used for the column names:

            - P1[SQ001]: Interested
            - P1[SQ002]: Distressed
            - P1[SQ003]: Excited
            - P1[SQ004]: Upset
            - P1[SQ005]: Strong
            - P1[SQ006]: Guilty
            - P1[SQ007]: Scared
            - P1[SQ008]: Hostile
            - P1[SQ009]: Enthusiastic
            - P1[SQ010]: Proud
            - P1[SQ011]: Irritable
            - P1[SQ012]: Alert
            - P1[SQ013]: Ashamed
            - P1[SQ014]: Inspired
            - P1[SQ015]: Nervous
            - P1[SQ016]: Determined
            - P1[SQ017]: Attentive
            - P1[SQ018]: Jittery
            - P1[SQ019]: Active
            - P1[SQ020]: Afraid

        Parameters
        ----------
        user_id : :class:`str`
            Ths identifier of the user for which the PANAS questionnaire have to be loaded.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            Start date for which the answers to the PANAS questionnaire have to be loaded, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            End date for which the answers to the PANAS questionnaire have to be loaded, by default None
        map_questions: :class:`bool`, optional
            Whether to map the PANAS questions (``True``) or leave the default
            LifeSnaps encoding (``False``), by default True

        Returns
        -------
        :class:`pd.DataFrame`
            A formatted :class:`pd.DataFrame` with each row containing the answers to a given PANAS
            questionnaire request. Each column represents a given question, and the row values
            are the answer to the the question.
        """
        panas_questionnaire = self.load_questionnaire(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            questionnaire_name=lifesnaps_constants._METRIC_QUESTIONNAIRE_PANAS,
        )
        if map_questions:
            panas_questionnaire = panas_questionnaire.rename(
                columns={
                    "P1[SQ001]": "Interested",
                    "P1[SQ002]": "Distressed",
                    "P1[SQ003]": "Excited",
                    "P1[SQ004]": "Upset",
                    "P1[SQ005]": "Strong",
                    "P1[SQ006]": "Guilty",
                    "P1[SQ007]": "Scared",
                    "P1[SQ008]": "Hostile",
                    "P1[SQ009]": "Enthusiastic",
                    "P1[SQ010]": "Proud",
                    "P1[SQ011]": "Irritable",
                    "P1[SQ012]": "Alert",
                    "P1[SQ013]": "Ashamed",
                    "P1[SQ014]": "Inspired",
                    "P1[SQ015]": "Nervous",
                    "P1[SQ016]": "Determined",
                    "P1[SQ017]": "Attentive",
                    "P1[SQ018]": "Jittery",
                    "P1[SQ019]": "Active",
                    "P1[SQ020]": "Afraid",
                }
            )
        return panas_questionnaire

    def load_stai_questionnaire(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        map_questions: bool = True,
    ) -> pd.DataFrame:
        """Load STAI questionnaire.

        This function loads the State-Trait Anxiety Inventory (STAI)
        questionnaire from a given user and dates. The functions returns the answers to the
        questionnaire in a :class:`pd.DataFrame`. The :class:`pd.DataFrame` contains
        one column per each questionnaire question, and the column values
        represent the answers to the questionaire. It is possible to map the
        column names (i.e., the questions) to the proper questionnaire questions
        by setting the ``map_questions`` parameter to ``True``. Otherwise, the default
        encoding used in the LifeSnaps is used for the column names:

            - STAI[SQ001]: I feel calm
            - STAI[SQ002]: I feel secure
            - STAI[SQ003]: I am tense
            - STAI[SQ004]: I feel strained
            - STAI[SQ005]: I feel at ease
            - STAI[SQ006]: I feel upset
            - STAI[SQ007]: I am presently worrying over possible misfortunes
            - STAI[SQ008]: I feel satisfied
            - STAI[SQ009]: I feel frightened
            - STAI[SQ010]: I feel comfortable
            - STAI[SQ011]: I feel self-confident
            - STAI[SQ012]: I feel nervous
            - STAI[SQ013]: I am jittery
            - STAI[SQ014]: I feel indecisive
            - STAI[SQ015]: I am relaxed
            - STAI[SQ016]: I feel content
            - STAI[SQ017]: I am worried
            - STAI[SQ018]: I feel confused
            - STAI[SQ019]: I feel steady
            - STAI[SQ020]: I feel pleasant

        Parameters
        ----------
        user_id : :class:`str`
            Ths identifier of the user for which the STAI questionnaire have to be loaded.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            Start date for which the answers to the STAI questionnaire have to be loaded, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            End date for which the answers to the STAI questionnaire have to be loaded, by default None
        map_questions: :class:`bool`, optional
            Whether to map the STAI questions (``True``) or leave the default
            LifeSnaps encoding (``False``), by default True

        Returns
        -------
        :class:`pd.DataFrame`
            A formatted :class:`pd.DataFrame` with each row containing the answers to a given STAI
            questionnaire request. Each column represents a given question, and the row values
            are the answer to the the question.
        """
        stai_questionnaire = self.load_questionnaire(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            questionnaire_name=lifesnaps_constants._METRIC_QUESTIONNAIRE_STAI,
        )
        if map_questions:
            stai_questionnaire = stai_questionnaire.rename(
                columns={
                    "STAI[SQ001]": "I feel calm",
                    "STAI[SQ002]": "I feel secure",
                    "STAI[SQ003]": "I am tense",
                    "STAI[SQ004]": "I feel strained",
                    "STAI[SQ005]": "I feel at ease",
                    "STAI[SQ006]": "I feel upset",
                    "STAI[SQ007]": "I am presently worrying over possible misfortunes",
                    "STAI[SQ008]": "I feel satisfied",
                    "STAI[SQ009]": "I feel frightened",
                    "STAI[SQ010]": "I feel comfortable",
                    "STAI[SQ011]": "I feel self-confident",
                    "STAI[SQ012]": "I feel nervous",
                    "STAI[SQ013]": "I am jittery",
                    "STAI[SQ014]": "I feel indecisive",
                    "STAI[SQ015]": "I am relaxed",
                    "STAI[SQ016]": "I feel content",
                    "STAI[SQ017]": "I am worried",
                    "STAI[SQ018]": "I feel confused",
                    "STAI[SQ019]": "I feel steady",
                    "STAI[SQ020]": "I feel pleasant",
                }
            )
        return stai_questionnaire

    def load_personality_questionnaire(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        map_questions: bool = True,
    ) -> pd.DataFrame:
        """Load Big Five Personality questionnaire.

        This function loads the Big Five Personality Test (BFPT) from a given user and dates.
        The functions returns the answers to the questionnaire in a :class:`pd.DataFrame`.
        The :class:`pd.DataFrame` contains one column per each questionnaire question,
        and the column values represent the answers to the questionaire. It is possible
        to map the column names (i.e., the questions) to the proper questionnaire questions
        by setting the ``map_questions`` parameter to ``True``. Otherwise, the default
        encoding used in the LifeSnaps is used for the column names:

            - ipip[SQ001]: Am the life of the party
            - ipip[SQ002]: Feel little concern for others
            - ipip[SQ003]: Am always prepared
            - ipip[SQ004]: Get stressed out easily
            - ipip[SQ005]: Have a rich vocabulary
            - ipip[SQ006]: Don't talk a lot
            - ipip[SQ007]: Am interested in people
            - ipip[SQ008]: Leave my belongings around
            - ipip[SQ009]: Am relaxed most of the time
            - ipip[SQ010]: Have difficulty understanding abstract ideas
            - ipip[SQ011]: Feel comfortable around people
            - ipip[SQ012]: Insult people
            - ipip[SQ013]: Pay attention to details
            - ipip[SQ014]: Worry about things
            - ipip[SQ015]: Have a vivid imagination
            - ipip[SQ016]: Keep in the background
            - ipip[SQ017]: Sympathize with others' feelings
            - ipip[SQ018]: Make a mess of things
            - ipip[SQ019]: Seldom feel blue
            - ipip[SQ020]: Am not interested in abstract ideas
            - ipip[SQ021]: Start conversations
            - ipip[SQ022]: Am not interested in other people's problems
            - ipip[SQ023]: Get chores done right away
            - ipip[SQ024]: Am easily disturbed
            - ipip[SQ025]: Have excellent ideas
            - ipip[SQ026]: Have little to say
            - ipip[SQ027]: Have a soft heart
            - ipip[SQ028]: Often forget to put things back in their proper place
            - ipip[SQ029]: Get upset easily
            - ipip[SQ030]: Do not have a good imagination
            - ipip[SQ031]: Talk to a lot of different people at parties
            - ipip[SQ032]: Am not really interested in others
            - ipip[SQ033]: Like order
            - ipip[SQ034]: Change my mood a lot
            - ipip[SQ035]: Am quick to understand things
            - ipip[SQ036]: Don't like to draw attention to myself
            - ipip[SQ037]: Take time out for others
            - ipip[SQ038]: Shirk my duties
            - ipip[SQ039]: Have frequent mood swings
            - ipip[SQ040]: Use difficult words
            - ipip[SQ041]: Don't mind being the centre of attention
            - ipip[SQ042]: Feel others' emotions
            - ipip[SQ043]: Follow a schedule
            - ipip[SQ044]: Get irritated easily
            - ipip[SQ045]: Spend time reflecting on things
            - ipip[SQ046]: Am quiet around strangers
            - ipip[SQ047]: Make people feel at ease
            - ipip[SQ048]: Am exacting in my work
            - ipip[SQ049]: Often feel blue
            - ipip[SQ050]: Am full of ideas

        Parameters
        ----------
        user_id : :class:`str`
            Ths identifier of the user for which the BFPT have to be loaded.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            Start date for which the answers to the BFPT have to be loaded, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            End date for which the answers to the BFPT have to be loaded, by default None
        map_questions: :class:`bool`, optional
            Whether to map the BFPT questions (``True``) or leave the default
            LifeSnaps encoding (``False``), by default True

        Returns
        -------
        :class:`pd.DataFrame`
            A formatted :class:`pd.DataFrame` with each row containing the answers to a given BFPT
            questionnaire request. Each column represents a given question, and the row values
            are the answer to the the question.
        """
        bfpt_questionnaire = self.load_questionnaire(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            questionnaire_name=lifesnaps_constants._METRIC_QUESTIONNAIRE_PERSONALITY,
        )
        if map_questions:
            bfpt_questionnaire = bfpt_questionnaire.rename(
                columns={
                    "ipip[SQ001]": "Am the life of the party",
                    "ipip[SQ002]": "Feel little concern for others",
                    "ipip[SQ003]": "Am always prepared",
                    "ipip[SQ004]": "Get stressed out easily",
                    "ipip[SQ005]": "Have a rich vocabulary",
                    "ipip[SQ006]": "Don't talk a lot",
                    "ipip[SQ007]": "Am interested in people",
                    "ipip[SQ008]": "Leave my belongings around",
                    "ipip[SQ009]": "Am relaxed most of the time",
                    "ipip[SQ010]": "Have difficulty understanding abstract ideas",
                    "ipip[SQ011]": "Feel comfortable around people",
                    "ipip[SQ012]": "Insult people",
                    "ipip[SQ013]": "Pay attention to details",
                    "ipip[SQ014]": "Worry about things",
                    "ipip[SQ015]": "Have a vivid imagination",
                    "ipip[SQ016]": "Keep in the background",
                    "ipip[SQ017]": "Sympathize with others' feelings",
                    "ipip[SQ018]": "Make a mess of things",
                    "ipip[SQ019]": "Seldom feel blue",
                    "ipip[SQ020]": "Am not interested in abstract ideas",
                    "ipip[SQ021]": "Start conversations",
                    "ipip[SQ022]": "Am not interested in other people's problems",
                    "ipip[SQ023]": "Get chores done right away",
                    "ipip[SQ024]": "Am easily disturbed",
                    "ipip[SQ025]": "Have excellent ideas",
                    "ipip[SQ026]": "Have little to say",
                    "ipip[SQ027]": "Have a soft heart",
                    "ipip[SQ028]": "Often forget to put things back in their proper place",
                    "ipip[SQ029]": "Get upset easily",
                    "ipip[SQ030]": "Do not have a good imagination",
                    "ipip[SQ031]": "Talk to a lot of different people at parties",
                    "ipip[SQ032]": "Am not really interested in others",
                    "ipip[SQ033]": "Like order",
                    "ipip[SQ034]": "Change my mood a lot",
                    "ipip[SQ035]": "Am quick to understand things",
                    "ipip[SQ036]": "Don't like to draw attention to myself",
                    "ipip[SQ037]": "Take time out for others",
                    "ipip[SQ038]": "Shirk my duties",
                    "ipip[SQ039]": "Have frequent mood swings",
                    "ipip[SQ040]": "Use difficult words",
                    "ipip[SQ041]": "Don't mind being the centre of attention",
                    "ipip[SQ042]": "Feel others' emotions",
                    "ipip[SQ043]": "Follow a schedule",
                    "ipip[SQ044]": "Get irritated easily",
                    "ipip[SQ045]": "Spend time reflecting on things",
                    "ipip[SQ046]": "Am quiet around strangers",
                    "ipip[SQ047]": "Make people feel at ease",
                    "ipip[SQ048]": "Am exacting in my work",
                    "ipip[SQ049]": "Often feel blue",
                    "ipip[SQ050]": "Am full of ideas",
                }
            )
        return bfpt_questionnaire

    def load_ttm_questionnaire(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        map_questions: bool = True,
    ) -> pd.DataFrame:
        """Load Stages and Processes of Change Questionnaire.

        This function loads the Stages and Processes of Change (TTMSPBF) Questionnaire from a given user and dates.
        The functions returns the answers to the questionnaire in a :class:`pd.DataFrame`.
        The :class:`pd.DataFrame` contains one column per each questionnaire question,
        and the column values represent the answers to the questionaire. It is possible
        to map the column names (i.e., the questions) to the proper questionnaire questions
        by setting the ``map_questions`` parameter to ``True``. Otherwise, the default
        encoding used in the LifeSnaps is used for the column names:

            - processes[SQ002]: I read articles to learn more about physical activity.
            - processes[SQ003]: I get upset when I see people who would benefit from physical activity but choose not to do physical activity.
            - processes[SQ004]: I realize that if I don't do physical activity regularly, I may get ill and be a burden to others.
            - processes[SQ005]: I feel more confident when I do physical activity regularly.
            - processes[SQ006]: I have noticed that many people know that physical activity is good for them.
            - processes[SQ007]: When I feel tired, I make myself do physical activity anyway because I know I will feel better afterwards.
            - processes[SQ008]: I have a friend who encourages me to do physical activity when I don't feel up to it.
            - processes[SQ009]: One of the rewards of regular physical activity is that it improves my mood.
            - processes[SQ010]: I tell myself that I can keep doing physically activity if I try hard enough.
            - processes[SQ011]: I keep a set of physical activity clothes with me so I can do physical activity whenever I get the time.
            - processes[SQ012]: I look for information related to physical activity.
            - processes[SQ013]: I am afraid of the results to my health if I do not do physical activity.
            - processes[SQ014]: I think that by doing regular physical activity I will not be a burden to the healthcare system.
            - processes[SQ015]: I believe that regular physical activity will make me a healthier, happier person.
            - processes[SQ016]: I am aware of more and more people who are making physical activity a part of their lives.
            - processes[SQ017]: Instead of taking a nap after work, I do physical activity.
            - processes[SQ018]: I have someone who encourages me to do physical activity.
            - processes[SQ019]: I try to think of physical activity as a time to clear my mind as well as a workout for my body.
            - processes[SQ020]: I make commitments to do physical activity.
            - processes[SQ021]: I use my calendar to schedule my physical activity time.
            - processes[SQ022]: I find out about new methods of being physically active.
            - processes[SQ023]: I get upset when I realize that people I love would have better health if they were physically active.
            - processes[SQ024]: I think that regular physical activity plays a role in reducing health care costs.
            - processes[SQ025]: I feel better about myself when I do physical activity.
            - processes[SQ026]: I notice that famous people often say that they do physical activity regularly.
            - processes[SQ027]: Instead of relaxing by watching TV or eating, I take a walk or am physically active.
            - processes[SQ028]: My friends encourage me to do physical activity.
            - processes[SQ029]: If I engage in regular physical activity, I find that I get the benefit of having more energy.
            - processes[SQ030]: I believe that I can do physical activity regularly.
            - processes[SQ031]: I make sure I always have a clean set of physical activity clothes.

        Parameters
        ----------
        user_id : :class:`str`
            Ths identifier of the user for which the TTMSPBF have to be loaded.
        start_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            Start date for which the answers to the TTMSPBF have to be loaded, by default None
        end_date : :class:`datetime.datetime` or :class:`datetime.date` :class:`str` or None, optional
            End date for which the answers to the TTMSPBF have to be loaded, by default None
        map_questions: :class:`bool`, optional
            Whether to map the TTMSPBF questions (``True``) or leave the default
            LifeSnaps encoding (``False``), by default True

        Returns
        -------
        :class:`pd.DataFrame`
            A formatted :class:`pd.DataFrame` with each row containing the answers to a given TTMSPBF
            questionnaire request. Each column represents a given question, and the row values
            are the answer to the the question.
        """
        ttm_questionnaire = self.load_questionnaire(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            questionnaire_name=lifesnaps_constants._METRIC_QUESTIONNAIRE_TTM,
        )
        if map_questions:
            ttm_questionnaire = ttm_questionnaire.rename(
                columns={
                    "processes[SQ002]": "I read articles to learn more about physical activity.",
                    "processes[SQ003]": "I get upset when I see people who would benefit from physical activity but choose not to do physical activity.",
                    "processes[SQ004]": "I realize that if I don't do physical activity regularly, I may get ill and be a burden to others.",
                    "processes[SQ005]": "I feel more confident when I do physical activity regularly.",
                    "processes[SQ006]": "I have noticed that many people know that physical activity is good for them.",
                    "processes[SQ007]": "When I feel tired, I make myself do physical activity anyway because I know I will feel better afterwards.",
                    "processes[SQ008]": "I have a friend who encourages me to do physical activity when I don't feel up to it.",
                    "processes[SQ009]": "One of the rewards of regular physical activity is that it improves my mood.",
                    "processes[SQ010]": "I tell myself that I can keep doing physically activity if I try hard enough.",
                    "processes[SQ011]": "I keep a set of physical activity clothes with me so I can do physical activity whenever I get the time.",
                    "processes[SQ012]": "I look for information related to physical activity.",
                    "processes[SQ013]": "I am afraid of the results to my health if I do not do physical activity.",
                    "processes[SQ014]": "I think that by doing regular physical activity I will not be a burden to the healthcare system.",
                    "processes[SQ015]": "I believe that regular physical activity will make me a healthier, happier person.",
                    "processes[SQ016]": "I am aware of more and more people who are making physical activity a part of their lives.",
                    "processes[SQ017]": "Instead of taking a nap after work, I do physical activity.",
                    "processes[SQ018]": "I have someone who encourages me to do physical activity.",
                    "processes[SQ019]": "I try to think of physical activity as a time to clear my mind as well as a workout for my body.",
                    "processes[SQ020]": "I make commitments to do physical activity.",
                    "processes[SQ021]": "I use my calendar to schedule my physical activity time.",
                    "processes[SQ022]": "I find out about new methods of being physically active.",
                    "processes[SQ023]": "I get upset when I realize that people I love would have better health if they were physically active.",
                    "processes[SQ024]": "I think that regular physical activity plays a role in reducing health care costs.",
                    "processes[SQ025]": "I feel better about myself when I do physical activity.",
                    "processes[SQ026]": "I notice that famous people often say that they do physical activity regularly.",
                    "processes[SQ027]": "Instead of relaxing by watching TV or eating, I take a walk or am physically active.",
                    "processes[SQ028]": "My friends encourage me to do physical activity.",
                    "processes[SQ029]": "If I engage in regular physical activity, I find that I get the benefit of having more energy.",
                    "processes[SQ030]": "I believe that I can do physical activity regularly.",
                    "processes[SQ031]": "I make sure I always have a clean set of physical activity clothes.",
                }
            )
        return ttm_questionnaire

    def load_sema(
        self,
        user_id: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        pass
