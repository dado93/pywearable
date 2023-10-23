import datetime
from typing import Union

import pandas as pd
import pymongo
from bson.objectid import ObjectId

from ... import constants, utils
from ..base import BaseLoader
from ..lifesnaps import constants as lifesnaps_constants

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
    },
}


class LifeSnapsLoader(BaseLoader):
    """Loader for LifeSnaps dataset.

    Parameters
    ----------
    host : str
        Host for pymongo DB instance.
    port: int
        Port of the pymongo DB instance.
    """

    def __init__(self, host: str = "localhost", port: int = 27017):
        self.host = host
        self.port = port
        self.client = pymongo.MongoClient(self.host, self.port)
        self.db = self.client[lifesnaps_constants._DB_NAME]
        self.fitbit_collection = self.db[lifesnaps_constants._DB_FITBIT_COLLECTION_NAME]

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
        return user_id

    def load_sleep_summary(
        self,
        user_id: Union[ObjectId, str],
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
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
        user_id : ObjectId or str
            Unique identifier for the user.
        start_date : datetime.datetime or datetime.date or str or None, optional
            Start date for data retrieval, by default None
        end_date : datetime.datetime or datetime.date or str or None, optional
            End date for data retrieval, by default None

        Returns
        -------
        pd.DataFrame
            DataFrame with sleep summary data.

        Raises
        ------
        ValueError
            If `user_id` is not valid.
        ValueError
            If dates are not consistent.
        """
        if str(user_id) not in self.get_user_ids():
            raise ValueError(f"f{user_id} does not exist in DB.")
        user_id = self._check_user_id(user_id)
        start_date = utils.check_date(start_date)
        end_date = utils.check_date(end_date)
        date_of_sleep_key = f"{lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY}"
        date_of_sleep_key += (
            f".{lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_DATE_OF_SLEEP_KEY}"
        )
        start_sleep_key = f"{lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY}"
        start_sleep_key += (
            f".{lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_START_TIME_KEY}"
        )
        date_filter = self._get_start_and_end_date_time_filter_dict(
            start_date_key=date_of_sleep_key,
            start_date=start_date,
            end_date=end_date,
            end_date_key=None,
        )
        filtered_coll = self.fitbit_collection.aggregate(
            [
                {
                    "$match": {
                        lifesnaps_constants._DB_FITBIT_COLLECTION_TYPE_KEY: lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_TYPE_SLEEP,
                        lifesnaps_constants._DB_FITBIT_COLLECTION_ID_KEY: user_id,
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
                k: sleep_summary[lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY][k]
                for k in set(
                    list(
                        sleep_summary[
                            lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY
                        ].keys()
                    )
                )
                - set(["levels"])
            }
            # Create a pd.DataFrame with sleep summary data
            temp_df = pd.DataFrame(
                filtered_dict,
                index=[
                    sleep_summary[lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY][
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
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_DEEP_VALUE: constants._SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL,
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_LIGHT_VALUE: constants._SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL,
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
            temp_df[constants._SLEEP_SUMMARY_UNMEASURABLE_DURATION_IN_MS_COL] = 0
            sleep_summary_df = pd.concat((sleep_summary_df, temp_df), ignore_index=True)
        if len(sleep_summary_df) > 0:
            sleep_summary_df[constants._TIMEZONEOFFSET_IN_MS_COL] = 0
            sleep_summary_df = sleep_summary_df.rename(
                columns={
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_START_TIME_KEY: constants._ISODATE_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_DATE_OF_SLEEP_KEY: constants._CALENDAR_DATE_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY: constants._SLEEP_SUMMARY_ID_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_DURATION_KEY: constants._DURATION_IN_MS_COL,
                }
            )
            # TODO Change formula to convert from datetime to Unix Timestamp using pandas suggested
            sleep_summary_df[constants._UNIXTIMESTAMP_IN_MS_COL] = sleep_summary_df[
                constants._ISODATE_COL
            ].apply(lambda x: int(x.timestamp() * 1000))
            sleep_summary_df = sleep_summary_df.sort_values(
                by=lifesnaps_constants._CALENDAR_DATE_COL, ignore_index=True
            )
            for idx, col in enumerate(
                [
                    constants._SLEEP_SUMMARY_ID_COL,
                    constants._TIMEZONEOFFSET_IN_MS_COL,
                    constants._UNIXTIMESTAMP_IN_MS_COL,
                    constants._ISODATE_COL,
                    constants._CALENDAR_DATE_COL,
                    constants._DURATION_IN_MS_COL,
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_END_TIME_KEY,
                ]
            ):
                sleep_summary_df.insert(
                    idx,
                    col,
                    sleep_summary_df.pop(col),
                )
        return sleep_summary_df

    def _merge_sleep_data_and_sleep_short_data(self, sleep_entry: dict) -> pd.DataFrame:
        # Get data
        sleep_data_dict = sleep_entry[
            lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY
        ][lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY][
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_KEY
        ]
        # Create a pd.DataFrame with sleep data
        sleep_data_df = pd.DataFrame(sleep_data_dict)
        if not (
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SHORT_DATA_KEY
            in sleep_entry[lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY][
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY
            ].keys()
        ):
            return sleep_data_df
        sleep_short_data_list = sleep_entry[
            lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY
        ][lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY][
            lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SHORT_DATA_KEY
        ]
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
        user_id: Union[ObjectId, str],
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        include_short_data: bool = True,
    ) -> pd.DataFrame:
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
        sleep_start_key = f"{lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY}"
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
                        lifesnaps_constants._DB_FITBIT_COLLECTION_TYPE_KEY: lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_TYPE_SLEEP,
                        lifesnaps_constants._DB_FITBIT_COLLECTION_ID_KEY: user_id,
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
                sleep_data_dict = sleep_entry[
                    lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY
                ][lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY][
                    lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_KEY
                ]
                # Create a pd.DataFrame with sleep data
                sleep_data_df = pd.DataFrame(sleep_data_dict)
                # Add log id to pd.DataFrame
            sleep_data_df[
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY
            ] = sleep_entry[lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY][
                lifesnaps_constants._DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY
            ]

            sleep_stage_df = pd.concat(
                (sleep_stage_df, sleep_data_df), ignore_index=True
            )
        if len(sleep_stage_df) > 0:
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
            sleep_stage_df[constants._UNIXTIMESTAMP_IN_MS_COL] = sleep_stage_df[
                constants._ISODATE_COL
            ].apply(lambda x: int(x.timestamp() * 1000))
            sleep_stage_df = sleep_stage_df.sort_values(
                by=constants._UNIXTIMESTAMP_IN_MS_COL
            ).reset_index(drop=True)
            sleep_stage_df[constants._TIMEZONEOFFSET_IN_MS_COL] = 0
        return sleep_stage_df

    def load_metric(
        self,
        metric: str,
        user_id: Union[ObjectId, str],
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        if str(user_id) not in self.get_user_ids():
            raise ValueError(f"f{user_id} does not exist in DB.")
        user_id = self._check_user_id(user_id)
        start_date = utils.check_date(start_date)
        end_date = utils.check_date(end_date)

        metric_start_key = _METRIC_DICT[metric]["start_date_key"]
        if "end_date_key" in _METRIC_DICT[metric].keys():
            metric_end_key = _METRIC_DICT[metric]["end_date_key"]
        else:
            metric_end_key = None
        if metric_start_key is None:
            metric_start_date_key_db = None
        else:
            metric_start_date_key_db = (
                lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY
                + "."
                + metric_start_key
            )
        if metric_end_key is None:
            metric_end_date_key_db = None
        else:
            metric_end_date_key_db = (
                lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY
                + "."
                + metric_end_key
            )

        date_filter_dict = self._get_start_and_end_date_time_filter_dict(
            start_date_key=metric_start_date_key_db,
            end_date_key=metric_end_date_key_db,
            start_date=start_date,
            end_date=end_date,
        )
        date_conversion_dict = self._get_date_conversion_dict(
            start_date_key=metric_start_date_key_db, end_date_key=metric_end_date_key_db
        )
        filtered_coll = self.fitbit_collection.aggregate(
            [
                {
                    "$match": {
                        lifesnaps_constants._DB_FITBIT_COLLECTION_TYPE_KEY: _METRIC_DICT[
                            metric
                        ][
                            "metric_key"
                        ],
                        lifesnaps_constants._DB_FITBIT_COLLECTION_ID_KEY: user_id,
                    }
                },
                date_conversion_dict,
                date_filter_dict,
            ]
        )
        metric_df = pd.DataFrame()
        list_of_metric_dict = [
            entry[lifesnaps_constants._DB_FITBIT_COLLECTION_DATA_KEY]
            for entry in filtered_coll
        ]

        metric_df = pd.json_normalize(list_of_metric_dict)
        if len(metric_df) > 0 and (metric_start_key is not None):
            metric_df = metric_df.sort_values(by=metric_start_key).reset_index(
                drop=True
            )
        metric_df = self._setup_datetime_columns(df=metric_df, metric=metric)
        return metric_df

    def load_steps(
        self,
        user_id: Union[ObjectId, str],
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    ) -> pd.DataFrame:
        steps = self.load_metric(
            metric=lifesnaps_constants._METRIC_STEPS,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        steps = self._reorder_datetime_columns(steps)
        if len(steps) > 0:
            steps = steps.rename(
                columns={
                    lifesnaps_constants._DB_FITBIT_COLLECTION_STEPS_VALUE_COL: lifesnaps_constants._STEPS_COL
                }
            )
            # Compute daily steps column
            steps[lifesnaps_constants._CALENDAR_DATE_COL] = pd.to_datetime(
                steps[lifesnaps_constants._ISODATE_COL].dt.strftime("%Y-%m-%d"),
            )
            steps[lifesnaps_constants._STEPS_COL] = steps[
                lifesnaps_constants._STEPS_COL
            ].astype("int64")
            steps[lifesnaps_constants._TOTAL_STEPS_COL] = steps.groupby(
                [lifesnaps_constants._CALENDAR_DATE_COL]
            )[lifesnaps_constants._STEPS_COL].cumsum()
            steps = steps.drop([lifesnaps_constants._CALENDAR_DATE_COL], axis=1)
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

    def _get_date_conversion_dict(self, start_date_key, end_date_key=None) -> dict:
        if start_date_key is None:
            date_conversion_dict = {"$addFields": {}}
        elif (not start_date_key is None) and (not end_date_key is None):
            date_conversion_dict = {
                "$addFields": {
                    start_date_key: {
                        "$convert": {
                            "input": f"${start_date_key}",
                            "to": "date",
                        }
                    },
                    end_date_key: {
                        "$convert": {
                            "input": f"${end_date_key}",
                            "to": "date",
                        }
                    },
                }
            }
        elif (not start_date_key is None) and (end_date_key is None):
            date_conversion_dict = {
                "$addFields": {
                    start_date_key: {
                        "$convert": {
                            "input": f"${start_date_key}",
                            "to": "date",
                        }
                    },
                }
            }
        return date_conversion_dict

    def _setup_datetime_columns(self, df: pd.DataFrame, metric: str):
        if len(df) > 0:
            if "start_date_key" in _METRIC_DICT[metric].keys():
                if not (_METRIC_DICT[metric]["start_date_key"] is None):
                    df = df.rename(
                        columns={
                            _METRIC_DICT[metric][
                                "start_date_key"
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
