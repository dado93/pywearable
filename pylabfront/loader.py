"""
This module contains all the functions related to the loading of data from Labfront.

"""
import datetime
import os
import re
from pathlib import Path
from typing import Union, Tuple
import dateutil.parser

import pandas as pd

import pylabfront.utils as utils

# Labfront-specific constants
_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = "firstSampleUnixTimestampInMs"
_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = "lastSampleUnixTimestampInMs"
_LABFRONT_ISO_DATE_KEY = "isoDate"
_LABFRONT_CSV_STATS_SKIP_ROWS = 3
_LABFRONT_QUESTIONNAIRE_STRING = "questionnaire"
_LABFRONT_TODO_STRING = "todo"
_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY = "timezoneOffsetInMs"
_LABFRONT_GARMIN_DEVICE_TIMEZONEOFFSET_MS_KEY = "timezone"
_LABFRONT_UNIXTIMESTAMP_MS_KEY = "unixTimestampInMs"
_LABFRONT_TODO_NAME_KEY = "todoName"
_LABFRONT_QUESTIONNAIRE_NAME_KEY = "questionnaireName"

###################################################
# Garmin Connect metrics - Labfront folder names  #
###################################################
_LABFRONT_GARMIN_CONNECT_STRING = "garmin-connect"
_LABFRONT_GARMIN_CONNECT_BODY_COMPOSITION_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-body-composition"
)
_LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-daily-heart-rate"
)
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-daily-summary"
)
_LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-pulse-ox"
)
_LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-sleep-pulse-ox"
)
_LABFRONT_GARMIN_CONNECT_DAILY_RESPIRATION_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-respiration"
)
_LABFRONT_GARMIN_CONNECT_SLEEP_RESPIRATION_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-sleep-respiration"
)
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-sleep-stage"
)
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING = (
    _LABFRONT_GARMIN_CONNECT_STRING + "-sleep-summary"
)
_LABFRONT_GARMIN_CONNECT_EPOCH_STRING = _LABFRONT_GARMIN_CONNECT_STRING + "-epoch"
_LABFRONT_GARMIN_CONNECT_STRESS_STRING = _LABFRONT_GARMIN_CONNECT_STRING + "-stress"

###################################################
#  Garmin Connect metrics - Labfront folder names #
###################################################
_LABFRONT_SPO2_COLUMN = "spo2"
_LABFRONT_RESPIRATION_COLUMN = "breathsPerMinute"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL = "calendarDate"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_IN_MS_COL = "durationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL = "awakeDurationInMs"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_STAGE_COL = "type"

_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATE_COL = "calendarDate"
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SUMMARY_COL = "sleepSummaryId"


###################################################
#  Garmin Device metrics - Labfront csv columns  #
###################################################
_LABFRONT_GARMIN_DEVICE_STRING = "garmin-device"
_LABFRONT_GARMIN_DEVICE_BBI_STRING = _LABFRONT_GARMIN_DEVICE_STRING + "-bbi"
_LABFRONT_GARMIN_DEVICE_HEART_RATE_STRING = (
    _LABFRONT_GARMIN_DEVICE_STRING + "-heart-rate"
)
_LABFRONT_GARMIN_DEVICE_PULSE_OX_STRING = _LABFRONT_GARMIN_DEVICE_STRING + "-pulse-ox"
_LABFRONT_GARMIN_DEVICE_RESPIRATION_STRING = (
    _LABFRONT_GARMIN_DEVICE_STRING + "-respiration"
)
_LABFRONT_GARMIN_DEVICE_STEP_STRING = _LABFRONT_GARMIN_DEVICE_STRING + "-step"
_LABFRONT_GARMIN_DEVICE_STRESS_STRING = _LABFRONT_GARMIN_DEVICE_STRING + "-stress"

_LABFRONT_QUESTIONNAIRE_QUESTION_DESCRIPTION_COL = "questionDescription"
_LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_COL = "questionType"
_LABFRONT_QUESTIONNAIRE_QUESTION_NAME_REGEX = "option\dName"
_LABFRONT_QUESTIONNAIRE_SECTION_INDEX_COL = "sectionIndex"
_LABFRONT_QUESTIONNAIRE_QUESTION_INDEX_COL = "questionIndex"

###################################################
#         Labfront questionnaires columns         #
###################################################

_LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_RADIO_VAL = "radio"
_LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_MULTI_SELECT_VAL = "multi_select"
_LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_TEXT_VAL = "text"


class LabfrontLoader:
    """Loader for Labfront data.

    This is the main object for loading and analyzing data collected
    with Labfront.

    Parameters
    ----------
        data_path: str or Path
            Path to folder containing Labfront data.
    """

    def __init__(self, data_path: Union[str, Path]):
        """Constructor method"""
        self.set_path(data_path)
        self.date_column = _LABFRONT_ISO_DATE_KEY

    def set_path(self, data_path: Union[str, Path]):
        """Set path to folder containing Labfront data.

        This function allows to change the path of Labfront data
        to be loaded.

        Parameters
        ----------
        data_path : str or Path
            Path to folder containing Labfront data.
        """
        if not isinstance(data_path, Path):
            data_path = Path(data_path)
        self.data_path = data_path
        self.ids, self.labfront_ids = self.retrieve_ids()
        self.ids_dict = self.retrieve_ids(return_dict=True)
        self.full_ids = self.retrieve_full_ids()

        self.data_dictionary, self.metrics_data_dictionary = self.get_time_dictionary()
        self.tasks_dict = self.get_available_questionnaires(
            return_dict=True
        ) | self.get_available_todos(return_dict=True)

    def get_user_id(self, full_id: str) -> str:
        """Extract user ID from full ID.

        Parameters
        ----------
        full_id : str
            Full ID, composed of User ID and Labfront ID.

        Returns
        -------
        str
            User ID.

        Raises
        ------
        ValueError
            If not user ID could be extracted.
        """
        if "_" in full_id:
            # Labfront separates user ID from Labfront ID using "_"
            return full_id.split("_")[0]
        else:
            raise ValueError("Could not extract user ID.")

    def get_user_ids(self) -> list:
        """Get available user IDs.

        Returns
        -------
        list
            List of available user IDs.
        """
        return self.ids

    def get_labfront_ids(self) -> list:
        """Get available Labfront IDs.

        Returns
        -------
        list
            List of available Labfront IDs.
        """
        return self.labfront_ids

    def get_full_ids(self) -> list:
        """Get available full IDs, composed of both user and Labfront IDs.

        Returns
        -------
        list
            List of available full IDs.
        """
        return self.full_ids

    def retrieve_ids(self, return_dict: bool = False) -> Union[Tuple[list, list], dict]:
        """Get IDs of users from folder with data.

        This function returns both user IDs (set in the Labfront dashboard
        when new participants are inserted by the study coordinator)
        and Labfront IDs. You can either choose to get the IDs in a dictionary format,
        or as two separate lists.

        Parameters
        ----------
        return_dict : bool, optional
             Whether to return a dictionary or two separate lists, by default False

        Returns
        -------
        (list, list) or dict
            User IDs and Labfront IDs, as a tuple with two lists if `return_dict` was `False`,
            otherwise as a dictionary.
        """
        # Get the names of the folder in root_folder
        ids = []
        labfront_ids = []
        for folder_name in self.data_path.iterdir():
            # Check that we have a folder
            if folder_name.is_dir():
                # Check if we have a Labfront ID
                if "_" in folder_name.name:
                    labfront_id = folder_name.name.split("_")[1]
                    id = folder_name.name.split("_")[0]
                    labfront_ids.append(labfront_id)
                    ids.append(id)
        if return_dict:
            return dict(zip(ids, labfront_ids))
        return ids, labfront_ids

    def retrieve_full_ids(self) -> list:
        """Get list of users in "[user_id]_[labfront_id]" format.

        Returns
        -------
        list
            List of user IDs.
        """
        participant_ids = [
            k + "_" + v for k, v in self.retrieve_ids(return_dict=True).items()
        ]
        return participant_ids

    def get_full_id(self, id: str) -> str:
        """Get full participant ID.

        Parameters
        ----------
        id : str
            Identifier for the user. This can be either the user ID,
            the Labfront ID, or the full ID.

        Returns
        -------
        str
            Full ID for the user, composed of both user and Labfront IDs.

        Raises
        ------
        ValueError
            Multiple users exist with the same user ID.
        ValueError
            Invalid ID.
        """
        if "_" in id:
            # This is already a full ID
            return id
        elif id in self.ids:
            # This is a user ID
            # Check if we have duplicates
            if self.ids.count(id) > 1:
                raise ValueError(
                    f"Multiple users exist with ID {id}. Specificy either Labfront ID or full ID."
                )
            return id + "_" + self.ids_dict[id]
        elif id in self.labfront_ids:
            # This is a Labfront ID
            # -> Invert dictionary
            inv_ids_dict = {v: k for k, v in self.ids_dict.items()}
            return inv_ids_dict[id] + "_" + id
        else:
            raise ValueError(f"Could not get full_id from {id}")

    def get_available_questionnaires(
        self, user_id: Union[str, list] = "all", return_dict: bool = False
    ) -> list:
        """Get the list of available questionnaires.

        Parameters
        ----------
            user_id: str or list, optional
                IDs of the users for which to return available questionnaires, by default "all".
            return_dict: bool, optional
                Whether to return a dictionary of the name of the questionnaires and their full ids,
                or simply a sorted list of the available questionnaires, by default False.

        Returns
        -------
            list
                alphabetically sorted names of the questionnaires for the user(s).
        """
        if not self.data_path.exists():
            raise FileNotFoundError

        questionnaires = set()
        questionnaires_dict = {}

        participant_ids = utils.get_user_ids(self, user_id)

        for participant_id in participant_ids:
            participant_id = self.get_full_id(participant_id)
            participant_path = (
                self.data_path / participant_id / _LABFRONT_QUESTIONNAIRE_STRING
            )
            if participant_path.exists():
                participant_questionnaires = set(
                    [
                        dir
                        for dir in os.listdir(str(participant_path))
                        if os.path.isdir(participant_path / dir)
                    ]
                )
                if return_dict:
                    # for every new questionnaire
                    for questionnaire in participant_questionnaires - questionnaires:
                        # get its name
                        questionnaire_name = pd.read_csv(
                            list((participant_path / questionnaire).iterdir())[0],
                            nrows=1,
                            skiprows=_LABFRONT_CSV_STATS_SKIP_ROWS,
                        )[_LABFRONT_QUESTIONNAIRE_NAME_KEY][0]
                        questionnaires_dict[questionnaire_name.lower()] = questionnaire
                questionnaires |= participant_questionnaires

        if return_dict:
            return questionnaires_dict
        else:
            return sorted(list(questionnaires))

    def get_available_todos(
        self, user_id: Union[str, list] = "all", return_dict: bool = False
    ) -> list:
        """Get available todos for given users.

        Parameters
        ----------
        user_id : str or list, optional
            ID(s) of the users for which todos should be retrieved, by default "all"
        return_dict : bool, optional
            Whether to return a dictionary of the name of the todos
            and their full ids, or simply a sorted list of the available todos, by default False

        Returns
        -------
        list
            alphabetically sorted names of the todos for the user(s).

        Raises
        ------
        FileNotFoundError
            if data path does not exist
        """
        if not self.data_path.exists():
            raise FileNotFoundError

        todos = set()
        todos_dict = {}

        participant_ids = utils.get_user_ids(self, user_id)

        for participant_id in participant_ids:
            participant_id = self.get_full_id(participant_id)
            participant_path = self.data_path / participant_id / _LABFRONT_TODO_STRING
            if participant_path.exists():
                participant_todos = set(
                    [
                        dir
                        for dir in os.listdir(participant_path)
                        if os.path.isdir(participant_path / dir)
                    ]
                )
                if return_dict:
                    # for every new todo
                    for todo in participant_todos - todos:
                        # get its name
                        todo_name = pd.read_csv(
                            list((participant_path / todo).iterdir())[0],
                            nrows=1,
                            skiprows=_LABFRONT_CSV_STATS_SKIP_ROWS,
                        )[_LABFRONT_TODO_NAME_KEY][0]
                        todos_dict[todo_name.lower()] = todo
                todos |= participant_todos

        if return_dict:
            return todos_dict
        else:
            return sorted(list(todos))

    # """Create a dictionary with start and end times for all files for all users.
    #
    #    This function creates and returns a dictionary with start and
    #    end unix times for all the files that are present in Labfront
    #    data folder for all the participants.
    #    This is useful to easily determine, based on an
    #    input time and date, which files need to be loaded.
    #    The returned dictionary has the following structure::
    #
    #        {
    #            'participant-01': {
    #                'garmin-connect-pulse-ox':
    #                {
    #                    '000000_garmin-connect-pulse-ox_sample-participant-01_6732ab82.csv':
    #                    {
    #                        'firstSampleUnixTimestampInMs': 1672740900000
    #                        'lastSampleUnixTimestampInMs': 1675248720000
    #                    }
    #                }
    #            }
    #        }
    #
    #
    #    Returns
    #    -------
    #        class:`dict`: Dictionary with start and end times for all files.
    # """
    def get_time_dictionary(self) -> Tuple[list, list]:
        """_summary_

        Returns
        -------
        Tuple[list, list]
            _description_

        Raises
        ------
        FileNotFoundError
            _description_
        """
        if not self.data_path.exists():
            raise FileNotFoundError
        participant_dict = {}
        metrics_time_dict = {}
        for participant_folder in self.data_path.iterdir():
            # For each participant
            if participant_folder.is_dir():
                participant_dict[participant_folder.name] = {}
                metrics_time_dict[participant_folder.name] = {}
                for participant_metric_folder in participant_folder.iterdir():
                    # For each metric
                    if participant_metric_folder.is_dir():
                        participant_dict[participant_folder.name][
                            participant_metric_folder.name
                        ] = {}
                        metrics_time_dict[participant_folder.name][
                            participant_metric_folder.name
                        ] = {}
                        metrics_first_ts = None
                        metrics_last_ts = None
                        # If it is a folder, then we need to read the csv files and get first and last unix times, and min sample rate
                        for metric_data in participant_metric_folder.iterdir():
                            # For each csv folder/file
                            if metric_data.is_file() and str(metric_data).endswith(
                                "csv"
                            ):
                                # If it is a file
                                (first_ts, last_ts) = self.get_labfront_file_time_stats(
                                    metric_data
                                )
                                # Update first time stamp of the metric
                                if metrics_first_ts is None:
                                    metrics_first_ts = first_ts
                                else:
                                    if first_ts < metrics_first_ts:
                                        metrics_first_ts = first_ts
                                # Update last time stamp of the metric
                                if metrics_last_ts is None:
                                    metrics_last_ts = last_ts
                                else:
                                    if last_ts < metrics_last_ts:
                                        metrics_last_ts = last_ts
                                participant_dict[participant_folder.name][
                                    participant_metric_folder.name
                                ][metric_data.name] = {
                                    _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: first_ts,
                                    _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: last_ts,
                                }
                                metrics_time_dict[participant_folder.name][
                                    participant_metric_folder.name
                                ] = {
                                    _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: metrics_first_ts,
                                    _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: metrics_last_ts,
                                }
                            else:
                                if not metric_data.is_dir():
                                    continue
                                # For each questionnaire/task folder
                                participant_dict[participant_folder.name][
                                    participant_metric_folder.name
                                ][metric_data.name] = {}
                                for csv_file in metric_data.iterdir():
                                    if csv_file.is_file() and str(csv_file).endswith(
                                        "csv"
                                    ):
                                        if _LABFRONT_TODO_STRING == metric_data.name:
                                            is_questionnaire_or_to_do = False
                                        else:
                                            is_questionnaire_or_to_do = True
                                        # If it is a file
                                        (
                                            first_ts,
                                            last_ts,
                                        ) = self.get_labfront_file_time_stats(
                                            csv_file,
                                            is_questionnaire_or_to_do=is_questionnaire_or_to_do,
                                        )
                                        # Update first time stamp of the metric
                                        if metrics_first_ts is None:
                                            metrics_first_ts = first_ts
                                        else:
                                            if first_ts < metrics_first_ts:
                                                metrics_first_ts = first_ts
                                        # Update last time stamp of the metric
                                        if metrics_last_ts is None:
                                            metrics_last_ts = last_ts
                                        else:
                                            if last_ts < metrics_last_ts:
                                                metrics_last_ts = last_ts
                                        participant_dict[participant_folder.name][
                                            participant_metric_folder.name
                                        ][metric_data.name][csv_file.name] = {
                                            _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: first_ts,
                                            _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: last_ts,
                                        }
                        metrics_time_dict[participant_folder.name][
                            participant_metric_folder.name
                        ] = {
                            _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: metrics_first_ts,
                            _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: metrics_last_ts,
                        }

        return participant_dict, metrics_time_dict

    def get_first_unix_timestamp(self, user_id: str, metric: str) -> int:
        """Get first available unix timestamp for a given user and metric.

        Parameters
        ----------
        user_id : str
            ID of the user.
        metric : str
            Metric of interest.

        Returns
        -------
        int
            First available unix timestamp.
        """
        return self.metrics_data_dictionary[self.get_full_id(user_id)][metric][
            _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY
        ]

    def get_last_unix_timestamp(self, user_id, metric):
        """Get last available unix timestamp for a given user and metric.

        Parameters
        ----------
        user_id : str
            ID of the user.
        metric : _type_
            Metric of interest.

        Returns
        -------
        int
            Last available unix timestamp.
        """
        return self.metrics_data_dictionary[self.get_full_id(user_id)][metric][
            _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY
        ]

    def get_labfront_file_time_stats(
        self, path_to_file: Union[str, Path], is_questionnaire_or_to_do: bool = False
    ) -> Tuple[int, int]:
        """Get time statistics from Labfront csv file.

        This function retrieves first and last unix timestamps (in ms) from
        a given Labfront CSV file without reading the whole content of the
        file.

        Parameters
        ----------
        path_to_file : str or Path
            Path to the file from which stats have to be extracted
        is_questionnaire_or_to_do : bool, optional
            Whether the file is a questionnaire or not, by default False

        Returns
        -------
        Tuple[int, int]
            Tuple containing first and last unix timestamp of data in the CSV file.
        """

        # Get first and last unix timestamps from header
        header = pd.read_csv(
            path_to_file, nrows=1, skiprows=_LABFRONT_CSV_STATS_SKIP_ROWS
        )
        first_unix_timestamp = header[
            _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY
        ].iloc[0]
        last_unix_timestamp = header[
            _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY
        ].iloc[0]

        return first_unix_timestamp, last_unix_timestamp

    def get_files_from_timerange(
        self,
        user_id: str,
        metric: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        is_questionnaire: bool = False,
        is_todo: bool = False,
        task_name: str = "",
    ) -> list:
        """Get files containing daily data from within a given time range.

        This function retrieves the files that contain data in a given time range. By setting start
        and end times to the time range of interest, this function returns all the files that
        contain data within this time range. This function is based on unix timestamps, thus it
        does not take into account timezones. In order to find the files containing data within
        the timerange, 12 hours are removed (added) from the start_date (end_date).
        In case no files are available to be loaded, then an empty list is returned.

        Parameters
        ----------
        user_id : str
            User ID.
        metric : str
            Metric of interest.
        start_date : datetime.datetime or datetime.date or str or None, optional
            Start date for data retrieval, by default None
        end_date : datetime.datetime or datetime.date or str or None, optional
            End date for data retrieval, by default None
        is_questionnaire : bool, optional
            Metric of interest is a questionnaire, by default False
        is_todo : bool, optional
            Metric of interest is a todo, by default False
        task_name : str, optional
            Name of the questionnaire or of the todo, by default None

        Returns
        -------
        list
            _description_

        Raises
        ------
        ValueError
            Invalid settings for questionnaire and todos, or invalid ID.
        """
        if is_questionnaire and is_todo:
            raise ValueError("Select only questionnaire or todo.")
        if (is_questionnaire or is_todo) and (task_name == ""):
            raise ValueError("Please specify name of questionnaire or of todo.")

        if not (
            (user_id in self.ids)
            or (user_id in self.labfront_ids)
            or (user_id in self.full_ids)
        ):
            raise ValueError(f"User with ID {user_id} was not found.")

        # Get full participant_id (user + labfront)
        participant_id = self.get_full_id(user_id)

        if metric not in self.data_dictionary[participant_id].keys():
            return []

        if is_questionnaire or is_todo:
            if task_name not in self.data_dictionary[participant_id][metric].keys():
                task_name = self.get_task_full_id(task_name)
                if task_name not in self.data_dictionary[participant_id][metric].keys():
                    return []
            temp_dict = self.data_dictionary[participant_id][metric][task_name]
        else:
            temp_dict = self.data_dictionary[participant_id][metric]

        # Convert dictionary to a pandas dataframe, so that we can sort it
        temp_pd = pd.DataFrame.from_dict(temp_dict, orient="index").sort_values(
            by=_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY
        )

        if (start_date is None) and (end_date is None):
            return list(temp_pd.index)
        # Convert date to unix format: YYYY/MM/DD
        # First, make sure that we have a datetime

        # Reset index
        temp_pd = temp_pd.reset_index()
        temp_pd = temp_pd.rename(columns={"index": "fileName"})
        if len(temp_pd == 1):
            return list(temp_pd["fileName"])

        if not (start_date is None):
            start_date_unix_ms = int(datetime.datetime.timestamp(start_date) * 1000)
            temp_pd["before_start_date"] = temp_pd[
                _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY
            ].apply(lambda x: True if x < start_date_unix_ms else False)
            # Compute difference with first and last columns
            temp_pd["start_diff"] = abs(
                temp_pd[_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY]
                - start_date_unix_ms
            )

        # Create column -> True if unix is after end_date False otherwise
        if not (end_date is None):
            end_date_unix_ms = int(datetime.datetime.timestamp(end_date) * 1000)
            temp_pd["after_end_date"] = temp_pd[
                _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY
            ].apply(lambda x: True if x > end_date_unix_ms else False)
            temp_pd["end_diff"] = abs(
                temp_pd[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY]
                - end_date_unix_ms
            )
        print(temp_pd)
        if start_date == None:
            min_row = 0
        else:
            # For the first time stamp, let's check if we have some files that start before start date
            try:
                min_row = temp_pd[temp_pd["before_start_date"] == True][
                    "start_diff"
                ].idxmin()
            except:
                min_row = temp_pd["start_diff"].idxmin()

        if end_date == None:
            max_row = -1
        else:
            # For last time stamp, let's check if we have some files that start after end date
            try:
                max_row = temp_pd[temp_pd["after_end_date"] == True][
                    "end_diff"
                ].idxmin()

            except:
                max_row = temp_pd["end_diff"].idxmin()
        if max_row == (len(temp_pd) - 1):
            return list(temp_pd.iloc[min_row:]["fileName"])
        return list(temp_pd.iloc[min_row:max_row]["fileName"])

    def get_data_from_datetime(
        self,
        user_id: str,
        metric: str,
        start_date: Union[datetime.datetime, datetime.date, str, None] = None,
        end_date: Union[datetime.datetime, datetime.date, str, None] = None,
        is_questionnaire: bool = False,
        is_todo: bool = False,
        task_name: str = None,
    ) -> pd.DataFrame:
        """Load data from a given user in a given time frame.

        This function allows to load data of a given metric from a specified user
        only within a given timeframe. If `start_date` and `end_date` are set to None, then
        all data available for the user of interest are returned.
        If no data are available, then an empty :class:`pandas.DataFrame` is returned.

        Parameters
        ----------
        user_id : str
            User identifier.
        metric : str
            Metric of interest.
        start_date : datetime.datetime or datetime.date or str or None, optional
            Start date and time of interest, by default None
        end_date : datetime.datetime or datetime.date or str or None, optional
            End date and time of interest, by default None
        is_questionnaire : bool, optional
            Metric of interest is a questionnaire, by default False
        is_todo : bool, optional
            Metric of interest is a todo, by default False
        task_name : str, optional
            Name of the questionnaire or of the todo, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe with the data of interest.

        Raises
        ------
        ValueError
            Not possible to load from both questionnaires and todos at the same time.
        ValueError
            No name specified for questionnaire or todo.
        ValueError
            The ID was not found among available IDs.
        """

        # Check questionnaire or todo
        if is_questionnaire and is_todo:
            raise ValueError("Select only questionnaire or todo.")
        if (is_questionnaire or is_todo) and (task_name is None):
            raise ValueError("Specify name of questionnaire or of todo.")
        if is_questionnaire or is_todo:
            task_name = self.get_task_full_id(task_name.lower())

        if not (
            (user_id in self.ids)
            or (user_id in self.labfront_ids)
            or (user_id in self.full_ids)
        ):
            raise ValueError(f"User with ID {user_id} was not found.")

        # Check dates and times
        if not (
            (type(start_date) == datetime.datetime)
            or (type(start_date) == datetime.date)
            or (start_date is None)
        ):
            start_date = dateutil.parser.parse(start_date)
        elif type(start_date) == datetime.date:
            start_date = datetime.datetime.combine(start_date, datetime.time())

        if not (
            (type(end_date) == datetime.datetime)
            or (type(end_date) == datetime.date or (end_date is None))
        ):
            end_date = dateutil.parser.parse(end_date)
        elif type(end_date) == datetime.date:
            end_date = datetime.datetime.combine(end_date, datetime.time())

        files = self.get_files_from_timerange(
            user_id,
            metric,
            start_date,
            end_date,
            is_questionnaire,
            is_todo,
            task_name,
        )

        # Get full participant_id (user + labfront)
        participant_id = self.get_full_id(user_id)

        if len(files) == 0:
            return pd.DataFrame()
        if is_questionnaire:
            path_to_folder = (
                self.data_path
                / participant_id
                / _LABFRONT_QUESTIONNAIRE_STRING
                / task_name
            )
        elif is_todo:
            path_to_folder = (
                self.data_path / participant_id / _LABFRONT_TODO_STRING / task_name
            )
        else:
            path_to_folder = self.data_path / participant_id / metric

        n_rows_to_skip = self.get_header_length(path_to_folder / files[0])
        if is_questionnaire:
            n_rows_to_skip += self.get_key_length(path_to_folder / files[0]) + 1
        # Load data from first file
        data = pd.read_csv(path_to_folder / files[0], skiprows=n_rows_to_skip)
        for f in files[1:]:
            tmp = pd.read_csv(path_to_folder / f, skiprows=n_rows_to_skip)
            if _LABFRONT_GARMIN_CONNECT_STRING in metric:
                tmp = tmp.drop(
                    [
                        _LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY,
                        _LABFRONT_UNIXTIMESTAMP_MS_KEY,
                    ],
                    axis=1,
                )
            data = pd.concat([data, tmp], ignore_index=True)
        if _LABFRONT_GARMIN_CONNECT_STRING in metric:
            # Convert to datetime according to isoformat
            data[_LABFRONT_ISO_DATE_KEY] = (
                data[_LABFRONT_UNIXTIMESTAMP_MS_KEY]
                + data[_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY]
            )
            data[_LABFRONT_ISO_DATE_KEY] = pd.to_datetime(
                data[_LABFRONT_ISO_DATE_KEY], unit="ms", utc=True
            )
            data[_LABFRONT_ISO_DATE_KEY] = data[_LABFRONT_ISO_DATE_KEY].dt.tz_localize(
                None
            )
        else:
            # Convert unix time stamp
            data[_LABFRONT_ISO_DATE_KEY] = pd.to_datetime(
                data[_LABFRONT_UNIXTIMESTAMP_MS_KEY], unit="ms", utc=True
            )
            data[_LABFRONT_ISO_DATE_KEY] = data.groupby(
                _LABFRONT_GARMIN_DEVICE_TIMEZONEOFFSET_MS_KEY, group_keys=False
            )[_LABFRONT_ISO_DATE_KEY].apply(
                lambda x: x.dt.tz_convert(x.name).dt.tz_localize(tz=None)
            )

        # Get data only from given start and end dates
        if (start_date is None) and (not end_date is None):
            return data[(data[_LABFRONT_ISO_DATE_KEY] <= end_date)].reset_index(
                drop=True
            )
        elif (not start_date is None) and (end_date is None):
            return data[(data[_LABFRONT_ISO_DATE_KEY] >= start_date)].reset_index(
                drop=True
            )
        elif (not start_date is None) and (not end_date is None):
            return data[
                (data[_LABFRONT_ISO_DATE_KEY] >= start_date)
                & (data[_LABFRONT_ISO_DATE_KEY] <= end_date)
            ].reset_index(drop=True)
        else:
            return data.reset_index(drop=True)

    def get_questionnaire_questions(self, questionnaire_name: str) -> dict:
        """Retrieve questions and answers for a given questionnaire.

        This function returns all the questions and answers for a given
        questionnaire. The return value is a dictionary, which has questions
        numbers (1_1, 1_2, 2_1, ...) as keys and question information as
        values.::

            {
                '1_1': {
                    'type': 'radio',
                    'description': 'SLEEP QUALITY: Compared to your usual wake-up, how would you rate quality of sleep?',
                    'options': ['Much better than usual', 'Better than usual', 'As usual', 'Worse than usual', 'Much worse than usual']
                },
                '1_2': {
                    'type': 'radio',
                    'description': 'ENERGY: Compared to your usual wake-up, how would you rate your energy?',
                    'options': ['Much better than usual', 'Better than usual', 'As usual', 'Worse than usual', 'Much worse than usual']
                }
            }

        Parameters
        ----------
        questionnaire_name : str
            Name of the questionnaire for which questions must be retrieved

        Returns
        -------
        dict
            Dictionary with question number as keys and question info as values

        Raises
        ------
        ValueError
            if questionnaire name does not exist
        """
        no_user_id = True
        full_task_id = self.get_task_full_id(questionnaire_name)
        for user_id in self.data_dictionary.keys():
            if _LABFRONT_QUESTIONNAIRE_STRING in self.data_dictionary[user_id].keys():
                if (
                    full_task_id
                    in self.data_dictionary[user_id][
                        _LABFRONT_QUESTIONNAIRE_STRING
                    ].keys()
                ):
                    no_user_id = False
                    participant_id = user_id
                    break
        if no_user_id:
            raise ValueError(
                f"Could not find questions for questionnaire {questionnaire_name}"
            )

        files = self.get_files_from_timerange(
            participant_id,
            _LABFRONT_QUESTIONNAIRE_STRING,
            start_date=None,
            end_date=None,
            is_questionnaire=True,
            is_todo=False,
            task_name=questionnaire_name,
        )

        if len(files) == 0:
            return {}

        path_to_folder = (
            self.data_path
            / participant_id
            / _LABFRONT_QUESTIONNAIRE_STRING
            / full_task_id
        )

        questionnaire_info_file = path_to_folder / files[0]
        header_length = self.get_header_length(questionnaire_info_file)
        key_length = self.get_key_length(questionnaire_info_file)

        questions_df = pd.read_csv(
            questionnaire_info_file, skiprows=header_length + 2, nrows=key_length - 2
        )

        questions_dict = {}
        # For each row, we need to get the question and all the options
        option_cols = []
        for col in questions_df.columns:
            regex_match = re.search(_LABFRONT_QUESTIONNAIRE_QUESTION_NAME_REGEX, col)
            if regex_match:
                option_cols.append(col)
        for idx, row in questions_df.iterrows():
            question_id = f"{row[_LABFRONT_QUESTIONNAIRE_SECTION_INDEX_COL]}_{row[_LABFRONT_QUESTIONNAIRE_QUESTION_INDEX_COL]}"
            questions_dict[question_id] = {
                "type": row[_LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_COL],
                "description": row[_LABFRONT_QUESTIONNAIRE_QUESTION_DESCRIPTION_COL],
            }
            if (
                row[_LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_COL]
                == _LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_TEXT_VAL
            ):
                continue
            question_options = []
            for col in option_cols:
                if not pd.isna(row[col]):
                    question_options.append(row[col])
            questions_dict[question_id]["options"] = question_options
        return questions_dict

    def process_questionnaire(self, questionnaire, verbose=False):
        questionnaire_df = pd.DataFrame()
        questionnaire_questions = self.get_questionnaire_questions(questionnaire)
        questions = [
            questionnaire_questions[k]["description"]
            for k in questionnaire_questions.keys()
        ]

        for participant in self.full_ids:
            try:
                questionnaire_data = self.load_questionnaire(
                    participant, task_name=questionnaire
                )
            except KeyError:
                if verbose:
                    print(
                        f"Could not load {questionnaire} from {participant} as the questionnaire is not available."
                    )
                continue
            if len(questionnaire_data) > 0:
                questionnaire_data.loc[:, "userId"] = participant
                for question_key in questionnaire_questions.keys():
                    if (
                        questionnaire_questions[question_key]["type"]
                        == _LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_RADIO_VAL
                    ):
                        options_dict = {
                            (k + 1): v
                            for k, v in enumerate(
                                questionnaire_questions[question_key]["options"]
                            )
                        }
                        questionnaire_data[question_key] = questionnaire_data[
                            question_key
                        ].map(options_dict)
                        questionnaire_data.loc[
                            :,
                            f'{question_key}-{questionnaire_questions[question_key]["description"]}',
                        ] = questionnaire_data[question_key]
                    elif (
                        questionnaire_questions[question_key]["type"]
                        == _LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_TEXT_VAL
                    ):
                        questionnaire_data.loc[
                            :,
                            f'{question_key}-{questionnaire_questions[question_key]["description"]}',
                        ] = questionnaire_data[question_key]

                    elif (
                        questionnaire_questions[question_key]["type"]
                        == _LABFRONT_QUESTIONNAIRE_QUESTION_TYPE_MULTI_SELECT_VAL
                    ):
                        # We may have multiple options here, separated by a comma
                        # We create new columns based on question name - option name and set the values to default False
                        options_list = questionnaire_questions[question_key]["options"]
                        for option in range(len(options_list)):
                            questionnaire_data.loc[
                                :,
                                f'{question_key}-{questionnaire_questions[question_key]["description"]}-{options_list[int(option)]}',
                            ] = False
                        # If we have the option, then set the corresponding column value to True
                        for idx, row in questionnaire_data.iterrows():
                            for option in range(len(options_list)):
                                if isinstance(row[question_key], str):
                                    if str(option + 1) in row[question_key]:
                                        questionnaire_data.loc[
                                            idx,
                                            f'{question_key}-{questionnaire_questions[question_key]["description"]}-{options_list[int(option)]}',
                                        ] = True
                                elif row[question_key] == option + 1:
                                    questionnaire_data.loc[
                                        idx,
                                        f'{question_key}-{questionnaire_questions[question_key]["description"]}-{options_list[int(option)]}',
                                    ] = True
                    questionnaire_data = questionnaire_data.drop([question_key], axis=1)
                questionnaire_df = pd.concat(
                    [questionnaire_df, questionnaire_data], ignore_index=True
                )
        return questionnaire_df

    def get_header_length(self, file_path: Union[str, Path]) -> int:
        """Get header length of Labfront csv file.

        Parameters
        ----------
        file_path : str or Path
            Path to file.

        Returns
        -------
        int
            Lenght of the header.
        """
        # Read first line of file
        with open(file_path, "r", encoding="utf-8") as f:
            line = f.readline().split(",")
        header_length = int(line[1])
        return header_length

    def get_key_length(self, file_path: Union[str, Path]) -> int:
        """Get key length of Labfront questionnaire csv file.

        Parameters
        ----------
        file_path : str or Path
            Path to file.

        Returns
        -------
        int
            Lenght of the key header.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            while True:
                line = f.readline().split(",")
                if line[0] == "Key Length":
                    break
        key_length = int(line[1])
        return key_length

    def get_available_metrics(self, user_id: Union[str, list] = "all") -> list:
        """Get the list of available metrics for a given user.

        Parameters
        ----------
        user_id : str or list, optional
            ID of the user(s), by default "all"

        Returns
        -------
        list
            alphabetically sorted names of the metrics for the participant(s).
        """
        metrics = set()

        participant_ids = utils.get_user_ids(self, user_id)

        for participant_id in participant_ids:
            participant_path = self.data_path / participant_id
            participant_metrics = set(
                [
                    dir
                    for dir in os.listdir(str(participant_path))
                    if os.path.isdir(participant_path / dir)
                ]
            )
            metrics |= participant_metrics
        return sorted(list(metrics))

    def get_task_full_id(self, task_id: str) -> str:
        """Get the full ID (name and ID) of a given questionnaire or todo.

        Parameters
        ----------
        task_id : str
            ID of the task.

        Returns
        -------
        str
            Full ID of the task.
        """

        return self.tasks_dict[task_id.lower()]

    def load_garmin_connect_heart_rate(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect heart rate data.

        This function loads heart rate data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing heart rate data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING,
            start_date,
            end_date,
        )
        return data

    def load_garmin_connect_pulse_ox(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.datetime] = None,
        end_date: Union[str, datetime.date, datetime.datetime] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect pulse ox data.

        Parameters
        ----------
        user_id : str
            Identifier of the user. This can be the user ID, Labfront ID, or
            the full ID. If multiple users exist with the same user ID, then
            it is necessary to pass either the Labfront ID or the full ID.
        start_date : Union[str, datetime.date, datetime.datetime], optional
            Start date from which data should be retrieved, by default None
        end_date : Union[str, datetime.date, datetime.datetime], optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing Garmin Connect pulse ox data.
        """
        # We need to load both sleep and daily pulse ox
        daily_data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING,
            start_date,
            end_date,
        ).reset_index(drop=True)
        # Add sleep label to sleep pulse ox
        sleep_data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING,
            start_date,
            end_date,
        ).reset_index(drop=True)
        if len(sleep_data) > 0:
            sleep_data.loc[:, "sleep"] = 1
        # Merge dataframes
        # We need to merge the dataframes because the daily_data already contain sleep_data
        if len(daily_data) > 0:
            sleep_data = sleep_data.drop(
                [
                    x
                    for x in sleep_data.columns
                    if (not x in ([_LABFRONT_ISO_DATE_KEY, "sleep"]))
                ],
                axis=1,
            )
            merged_data = daily_data.merge(
                sleep_data, on=_LABFRONT_ISO_DATE_KEY, how="left"
            )
            merged_data.loc[merged_data.sleep != 1, "sleep"] = 0
            return merged_data
        else:
            return sleep_data

    def load_garmin_connect_respiration(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.datetime] = None,
        end_date: Union[str, datetime.date, datetime.datetime] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect respiratory data.

        This function loads Garmin Connect respiratory data from a given
        participant and within a specified date and time range. This
        function loads both daily and sleep respiratory data. The
        resulting data frame contains an additional column named 'sleep',
        equal to 1 for respiratory data acquired during sleep.

        Parameters
        ----------
        user_id : str
            ID of the user for which data must be loaded. This can be the user ID,
            Labfront ID, or the full ID. If multiple users exist with the same user ID,
            then it is necessary to pass either the Labfront ID or the full ID.
        start_date : str or datetime.date or datetime.datetime, optional
            Start date from which data should be retrieved, by default None
        end_date : Union[str, datetime.date, datetime.datetime], optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
             Dataframe containing Garmin Connect respiration data.
        """
        # We need to load both sleep and daily respiration
        daily_data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_DAILY_RESPIRATION_STRING,
            start_date,
            end_date,
        ).reset_index(drop=True)

        # Get sleep data
        sleep_data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_SLEEP_RESPIRATION_STRING,
            start_date,
            end_date,
        ).reset_index(drop=True)

        # Add calendar date from sleep summary
        sleep_summary = self.load_garmin_connect_sleep_summary(
            user_id,
            start_date,
            end_date,
        ).reset_index(drop=True)

        if len(sleep_summary) > 0:
            sleep_summary = sleep_summary.loc[
                :,
                [
                    _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SUMMARY_COL,
                    _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL,
                ],
            ]

        if len(sleep_data) > 0:
            sleep_data = pd.merge(
                left=sleep_data,
                right=sleep_summary,
                on=_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SUMMARY_COL,
                how="outer",
            )

            sleep_data.loc[:, "sleep"] = 1
            sleep_data = sleep_data.drop(
                [
                    x
                    for x in sleep_data.columns
                    if (
                        not x
                        in (
                            [
                                _LABFRONT_ISO_DATE_KEY,
                                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_SUMMARY_COL,
                                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL,
                                "sleep",
                            ]
                        )
                    )
                ],
                axis=1,
            )
            # Merge dataframes
            # We need to merge the dataframes because the daily_data already contain sleep_data
            merged_data = daily_data.merge(
                sleep_data, on=_LABFRONT_ISO_DATE_KEY, how="left"
            )
            merged_data.loc[merged_data.sleep != 1, "sleep"] = 0
            return merged_data
        else:
            daily_data.loc[:, "sleep"] = 0
            return daily_data

    def load_garmin_connect_sleep_stage(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect sleep stage data.

        This function loads sleep stage data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing sleep stages data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING,
            start_date,
            end_date,
        )
        return data

    def load_garmin_connect_sleep_summary(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect sleep summary data.

        This function loads sleep summary data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing sleep summary data.
        """

        # Let's add one day to the end_date and remove one day for start_date
        # TODO is this required?
        if not (start_date is None):
            if isinstance(start_date, str):
                start_date = dateutil.parser.parse(start_date)
            elif type(start_date) == datetime.date:
                start_date = datetime.datetime.combine(start_date, datetime.time())
            new_start_date = start_date - datetime.timedelta(days=1)
        else:
            new_start_date = None
        if not (end_date is None):
            if isinstance(end_date, str):
                end_date = dateutil.parser.parse(end_date)
            elif type(end_date) == datetime.date:
                end_date = datetime.datetime.combine(end_date, datetime.time())
            new_end_date = end_date + datetime.timedelta(days=1)
        else:
            new_end_date = None

        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING,
            new_start_date,
            new_end_date,
        )

        if len(data) > 0:
            data[
                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL
            ] = pd.to_datetime(
                data[_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL],
                format="%Y-%m-%d",
            ).dt.date
            if (start_date is None) and (end_date is None):
                return data
            else:
                start_date = None if (start_date is None) else start_date.date()
                end_date = None if (end_date is None) else end_date.date()
                if (start_date is None) and (not (end_date is None)):
                    return data[
                        (
                            data[
                                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL
                            ]
                            <= end_date
                        )
                    ]
                elif (not (start_date is None)) and (end_date is None):
                    return data[
                        (
                            data[
                                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL
                            ]
                            >= start_date
                        )
                    ]
                else:
                    return data[
                        (
                            data[
                                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL
                            ]
                            >= start_date
                        )
                        & (
                            data[
                                _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_CALENDAR_DATE_COL
                            ]
                            <= end_date
                        )
                    ]
        else:
            return pd.DataFrame()

    def load_garmin_connect_stress(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect stress data.

        This function loads stress data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing stress data.
        """
        data = self.get_data_from_datetime(
            user_id, _LABFRONT_GARMIN_CONNECT_STRESS_STRING, start_date, end_date
        )
        return data

    def load_garmin_device_heart_rate(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Device (SDK) heart rate data.

        This function loads heart rate data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing heart rate data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_DEVICE_HEART_RATE_STRING,
            start_date,
            end_date,
        )
        return data

    def load_garmin_device_pulse_ox(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Device (SDK) pulse ox data.

        This function loads pulse ox data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing pulse ox data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_DEVICE_PULSE_OX_STRING,
            start_date,
            end_date,
        )
        return data

    def load_garmin_device_respiration(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Device respiration data.

        This function loads steps data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing respiration data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_DEVICE_RESPIRATION_STRING,
            start_date,
            end_date,
        )
        return data

    def load_garmin_device_step(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Device (SDK) steps data.

        This function loads steps data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing steps data.
        """
        data = self.get_data_from_datetime(
            user_id, _LABFRONT_GARMIN_DEVICE_STEP_STRING, start_date, end_date
        )
        return data

    def load_garmin_device_stress(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin device (SDK) stress data.

        This function loads stress data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing BBI data.
        """
        data = self.get_data_from_datetime(
            user_id, _LABFRONT_GARMIN_DEVICE_STRESS_STRING, start_date, end_date
        )
        return data

    def load_garmin_device_bbi(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load BBI data.

        This function loads Beat to Beat Intervals (BBI) data from a given
        user and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing BBI data.
        """
        data = self.get_data_from_datetime(
            user_id, _LABFRONT_GARMIN_DEVICE_BBI_STRING, start_date, end_date
        )
        return data

    def load_garmin_connect_body_composition(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect body composition data.

        This function loads Garmin Connect body composition data from a given
        participant and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing Garmin Connect body composition data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_BODY_COMPOSITION_STRING,
            start_date,
            end_date,
        )
        return data

    def load_garmin_connect_daily_summary(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect daily summary data.

        This function loads Garmin Connect daily summary data from a given
        participant and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing Garmin Connect daily summary data.
        """
        new_start_date = start_date - datetime.timedelta(days=1)
        new_end_date = end_date + datetime.timedelta(days=1)
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STRING,
            new_start_date,
            new_end_date,
        )
        start_date = datetime.datetime(
            year=start_date.year, month=start_date.month, day=start_date.day
        )
        end_date = datetime.datetime(
            year=end_date.year, month=end_date.month, day=end_date.day
        )
        if len(data) > 0:
            data[
                _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATE_COL
            ] = pd.to_datetime(
                data[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATE_COL],
                format="%Y-%m-%d",
            )

            data = data[
                (
                    data[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATE_COL]
                    >= start_date
                )
                & (
                    data[_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_CALENDAR_DATE_COL]
                    <= end_date
                )
            ]

        return data

    def load_garmin_connect_epoch(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
    ) -> pd.DataFrame:
        """Load Garmin Connect epoch data.

        This function loads Garmin Connect epoch data from a given
        participant and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user.
        start_date : str or datetime.date or datetime.date, optional
            Start date from which data should be retrieved, by default None
        end_date : str or datetime.date or datetime.date, optional
            End date from which data should be retrieved, by default None

        Returns
        -------
        pd.DataFrame
            Dataframe containing Garmin Connect epoch data.
        """
        data = self.get_data_from_datetime(
            user_id, _LABFRONT_GARMIN_CONNECT_EPOCH_STRING, start_date, end_date
        )
        return data

    def load_todo(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
        todo_name: str = None,
    ):
        """Load todo data.

        This function loads todo data from a given
        participant and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user for which todo data have to be loaded.
            This can be the user ID, Labfront ID, or
            the full ID. If multiple users exist with the same user ID, then
            it is necessary to pass either the Labfront ID or the full ID.
        start_date : str or datetime.date or datetime.date, optional
            Start data for data loading, by default None
        end_date : str or datetime.date or datetime.date, optional
            End data for data loading, by default None
        todo_name : str, optional
            Name of the todo to be loaded, by default None

        Returns
        -------
        pd.DataFrame
            Todo data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_TODO_STRING,
            start_date,
            end_date,
            is_todo=True,
            task_name=todo_name,
        )
        return data

    def load_questionnaire(
        self,
        user_id: str,
        start_date: Union[str, datetime.date, datetime.date] = None,
        end_date: Union[str, datetime.date, datetime.date] = None,
        questionnaire_name: str = None,
    ) -> pd.DataFrame:
        """Load questionnaire data.

        This function loads questionnaire data from a given
        participant and within a specified date and time range.

        Parameters
        ----------
        user_id : str
            ID of the user for which questionnaire data have to be loaded.
            This can be the user ID, Labfront ID, or
            the full ID. If multiple users exist with the same user ID, then
            it is necessary to pass either the Labfront ID or the full ID.
        start_date : str or datetime.date or datetime.date, optional
            Start data for data loading, by default None
        end_date : str or datetime.date or datetime.date, optional
            End data for data loading, by default None
        questionnaire_name : str, optional
            Name of the questionnaire to be loaded, by default None

        Returns
        -------
        pd.DataFrame
            Questionnaire data.
        """
        data = self.get_data_from_datetime(
            user_id,
            _LABFRONT_QUESTIONNAIRE_STRING,
            start_date,
            end_date,
            is_questionnaire=True,
            task_name=questionnaire_name,
        )
        return data

    def load_hypnogram(
        self,
        user_id: str,
        calendar_day: Union[str, datetime.date, datetime.datetime],
        resolution: int = 1,
    ) -> pd.DataFrame:
        """Load hypnogram for given user for a given day.

        Parameters
        ----------
        participant_id : str
            Unique identifier of the user.
        calendar_day : str or datetime.date or datetime.date
            Calendar day for which hypnogram has to be provided.
        resolution : int, optional
            Desired resolution (in minutes) requested for the hypnogram, by default 1

        Returns
        -------
        pd.DataFrame
            Hypnogram data.

        Raises
        ------
        ValueError
            If date is passed as str and cannot be parsed.
        """

        if isinstance(calendar_day, str):
            try:
                calendar_day = dateutil.parser.parse(calendar_day)
            except:
                raise ValueError(
                    f"Could not parse {calendar_day} into a valid calendar day"
                )
        elif type(calendar_day) == datetime.datetime:
            calendar_day = calendar_day.date()
        # Get start and end days from calendar date
        start_date = calendar_day - datetime.timedelta(days=1)
        end_date = calendar_day + datetime.timedelta(days=1)
        # Load sleep summary and sleep stages data
        sleep_summary = self.load_garmin_connect_sleep_summary(
            user_id=user_id, start_date=start_date, end_date=end_date
        )

        sleep_summary_row = (
            sleep_summary[sleep_summary.calendarDate == calendar_day]
            .reset_index(drop=True)
            .iloc[0]
        )

        sleep_start_time = datetime.datetime.utcfromtimestamp(
            (
                sleep_summary_row[_LABFRONT_UNIXTIMESTAMP_MS_KEY]
                + sleep_summary_row[_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY]
            )
            / 1000
        )

        sleep_end_time = datetime.datetime.utcfromtimestamp(
            (
                sleep_summary_row[_LABFRONT_UNIXTIMESTAMP_MS_KEY]
                + sleep_summary_row[_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY]
                + sleep_summary_row[
                    _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_DURATION_IN_MS_COL
                ]
                + sleep_summary_row[
                    _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL
                ]
            )
            / 1000
        )
        sleep_stages = self.load_garmin_connect_sleep_stage(
            user_id=user_id,
            start_date=sleep_start_time,
            end_date=sleep_end_time,
        )

        intervals = int(
            divmod((sleep_end_time - sleep_start_time).total_seconds(), 60)[0]
        )
        time_delta_intervals = [
            sleep_start_time + i * datetime.timedelta(minutes=resolution)
            for i in range(intervals)
        ]

        hypnogram = pd.DataFrame(data={_LABFRONT_ISO_DATE_KEY: time_delta_intervals})

        hypnogram = hypnogram.merge(
            sleep_stages.loc[
                :,
                [
                    _LABFRONT_ISO_DATE_KEY,
                    _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_STAGE_COL,
                ],
            ],
            how="left",
            on=_LABFRONT_ISO_DATE_KEY,
        )

        hypnogram[
            _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_STAGE_COL
        ] = hypnogram.loc[
            :, _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_STAGE_COL
        ].fillna(
            method="ffill"
        )

        hypnogram["stage"] = hypnogram[
            _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_SLEEP_STAGE_COL
        ].apply(self._convert_sleep_stages)

        return hypnogram

    def _convert_sleep_stages(self, x: str):
        """Convert Garmin sleep stages from Garmin-specific to yasa values.

        The implemented convention is as follows:
            - REM: Yasa state 4
            - awake: Yasa state 0
            - deep: Yasa state 3
            - others: Yasa state 1

        Parameters
        ----------
        x : str
            Garmin sleep stage.

        Returns
        -------
        int
            Yasa sleep stage.
        """
        if x == "rem":
            return 4
        elif x == "awake":
            return 0
        elif x == "deep":
            return 3
        else:
            return 1
