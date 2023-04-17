"""
This module contains all the functions related to handling of data from Labfront.
"""
import datetime
import os
from pathlib import Path

import pandas as pd

import pylabfront.utils as utils

# Labfront-specific constants
_LABFRONT_ID_LENGHT = 37
_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = 'firstSampleUnixTimestampInMs'
_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY = 'lastSampleUnixTimestampInMs'
_LABFRONT_ISO_DATE_KEY = 'isoDate'
_LABFRONT_CSV_STATS_SKIP_ROWS = 3
_LABFRONT_QUESTIONNAIRE_STRING = 'questionnaire'
_LABFRONT_TODO_STRING = 'todo'
_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY = 'timezoneOffsetInMs'
_LABFRONT_GARMIN_DEVICE_TIMEZONEOFFSET_MS_KEY = 'timezone'
_LABFRONT_UNIXTIMESTAMP_MS_KEY = 'unixTimestampInMs'

###################################################
# Garmin Connect metrics - Labfront folder names  #
###################################################
_LABFRONT_GARMIN_CONNECT_STRING = 'garmin-connect'
_LABFRONT_GARMIN_CONNECT_BODY_COMPOSITION_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-body-composition'
_LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-heart-rate'
_LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-daily-summary'
_LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-pulse-ox'
_LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-pulse-ox'
_LABFRONT_GARMIN_CONNECT_DAILY_RESPIRATION_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-respiration'
_LABFRONT_GARMIN_CONNECT_SLEEP_RESPIRATION_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-respiration'
_LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-stage'
_LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING = _LABFRONT_GARMIN_CONNECT_STRING + '-sleep-summary'
_LABFRONT_GARMIN_CONNECT_EPOCH_STRING = _LABFRONT_GARMIN_CONNECT_STRING  + "-epoch"

###################################################
#  Garmin Connect metrics - Labfront csv columns  #
###################################################
_LABFRONT_SPO2_COLUMN = 'spo2'
_LABFRONT_RESPIRATION_COLUMN = 'breathsPerMinute'

# Garmin device metrics - Labfront folder names
_LABFRONT_GARMIN_DEVICE_STRING = 'garmin-device'
_LABFRONT_GARMIN_DEVICE_BBI_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-bbi'
_LABFRONT_GARMIN_DEVICE_HEART_RATE_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-heart-rate'
_LABFRONT_GARMIN_DEVICE_PULSE_OX_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-pulse-ox'
_LABFRONT_GARMIN_DEVICE_RESPIRATION_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-respiration'
_LABFRONT_GARMIN_DEVICE_STEP_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-step'
_LABFRONT_GARMIN_DEVICE_STRESS_STRING = _LABFRONT_GARMIN_DEVICE_STRING + '-stress'

class LabfrontLoader:
    """This class is required to manage all the loading operations of 
    Labfront data.

    Args:
        data_path (str): Path to folder containing Labfront data.
    """

    def __init__(self, data_path):
        """Constructor method
        """
        self.set_path(data_path)

    def set_path(self, data_path):
        """Set path of Labfront data.

        Args:
            data_path (str): Path to folder containing Labfront data.
        """
        if not isinstance(data_path, Path):
            data_path = Path(data_path)
        self.data_path = data_path
        self.ids, self.labfront_ids = self.get_ids()
        self.ids_dict = self.get_ids(return_dict=True)
        self.ids_list = self.get_participant_list()
        self.data_dictionary = self.get_time_dictionary()

    def get_user_ids(self):
        return self.ids
    
    def get_labfront_ids(self):
        return self.labfront_ids

    def get_ids(self, return_dict=False):
        """Get participant IDs from folder with data.

        Args:
            folder (str): Path to folder containing data from participants.
            return_dict (bool): Whether to return a dictionary or two lists. Defaults to False.

        Returns:
            list: IDs of participants (set by study coordinator)
            list: Labfront IDs of participants
        """
        # Get the names of the folder in root_folder
        folder_names = os.listdir(self.data_path)
        ids = []
        labfront_ids = []
        for folder_name in folder_names:
            # Check that we have a folder
            if os.path.isdir(os.path.join(self.data_path, folder_name)):
                labfront_id = folder_name[-_LABFRONT_ID_LENGHT+1:]
                labfront_ids.append(labfront_id)
                id = folder_name[:(len(folder_name)-_LABFRONT_ID_LENGHT)]
                ids.append(id)
        if return_dict:
            return dict(zip(ids, labfront_ids))
        return ids, labfront_ids
    
    def get_participant_list(self):
        """Get list of participants in "[user_id]_[labfront_id]" format.

        Returns:
            list: List of participants IDs
        """
        participant_ids = [k+"_"+v for k,v in self.get_ids(return_dict=True).items()]
        return participant_ids

    def get_available_questionnaires(self, participant_ids="all"):
        """Get the list of available questionnaires.

        Args:
            participant_ids (list):  IDs of participants. Defaults to "all".
        
        Returns:
            list: alphabetically sorted names of the questionnaires for the participant(s).
        """
        if not self.data_path.exists():
            raise FileNotFoundError
        
        questionnaires = set()

        if participant_ids == "all":
            participant_ids = self.get_user_ids()

        if not isinstance(participant_ids, list):
            raise TypeError("participant_ids must be a list.")
        
        for participant_id in participant_ids:
            participant_id = self.get_full_id(participant_id)
            participant_path = self.data_path / participant_id / _LABFRONT_QUESTIONNAIRE_STRING
            if participant_path.exists():
                participant_questionnaires = set(os.listdir(str(participant_path)))
                questionnaires |= participant_questionnaires
        
        return sorted(list(questionnaires))
    
    def get_available_todos(self, participant_ids="all"):
        """ Get the lit of available todos.
        
        Args:
            participant_ids (list):  IDs of participants. Defaults to "all",
        
        Returns:
            list: alphabetically sorted names of the todos for the participant(s).
        """

        if not self.data_path.exists():
            raise FileNotFoundError
        
        todos = set()

        if participant_ids == "all":
            participant_ids = self.get_user_ids()

        if not isinstance(participant_ids, list):
            raise TypeError("participant_ids has to be a list.")
        
        for participant_id in participant_ids:
            participant_id = self.get_full_id(participant_id)
            participant_path = self.data_path / participant_id / _LABFRONT_TODO_STRING
            if participant_path.exists():
                participant_todos = set(os.listdir(str(participant_path)))
                todos |= participant_todos
        
        return sorted(list(todos))
    
    def get_time_dictionary(self):
        """Create a dictionary with start and end times for all files.

        This function creates and returns a dictionary with start and
        end unix times for all the files that are present in data folder.
        This is useful to easily determine, based on an
        input time and date, which files need to be loaded.
            
        Returns:
            dict: Dictionary with start and end times for all files.
        """
        
        if not self.data_path.exists():
            raise FileNotFoundError
        participant_dict = {}
        for participant_folder in self.data_path.iterdir():
            # For each participant
            participant_dict[participant_folder.name] = {}
            if participant_folder.is_dir():
                for participant_metric_folder in participant_folder.iterdir():
                    # For each metric
                    if participant_metric_folder.is_dir():
                        participant_dict[participant_folder.name][participant_metric_folder.name] = {}
                        # If it is a folder, then we need to read the csv files and get first and last unix times, and min sample rate
                        for metric_data in participant_metric_folder.iterdir():
                            # For each csv folder/file
                            if metric_data.is_file() and str(metric_data).endswith('csv'):
                                # If it is a file
                                first_ts, last_ts = self.get_labfront_file_time_stats(metric_data)
                                participant_dict[participant_folder.name][participant_metric_folder.name][metric_data.name] = {
                                    _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: first_ts,
                                    _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: last_ts
                                }
                            else:
                                # For each questionnaire/task folder
                                participant_dict[participant_folder.name][participant_metric_folder.name][metric_data.name] = {}
                                for csv_file in metric_data.iterdir():
                                    if csv_file.is_file() and str(csv_file).endswith('csv'):
                                        # If it is a file
                                        first_ts, last_ts = self.get_labfront_file_time_stats(csv_file)
                                        participant_dict[participant_folder.name][participant_metric_folder.name][metric_data.name][csv_file.name] = {
                                            _LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: first_ts,
                                            _LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY: last_ts
                                        }
        return participant_dict

    def get_labfront_file_time_stats(self, path_to_file):
        """Get time statistics from Labfront csv file.

        Args:
            path_to_file (str): Path to the file from which stats have to be extracted

        Returns:
            int: First unix timestamp of data in csv file
            int: Last unix timestamp of data in csv file
        """

        # Get first and last unix timestamps from header
        header = pd.read_csv(path_to_file, nrows=1, skiprows=_LABFRONT_CSV_STATS_SKIP_ROWS)
        first_unix_timestamp = header[_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY].iloc[0]
        last_unix_timestamp = header[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY].iloc[0]
        
        return first_unix_timestamp, last_unix_timestamp

    def get_files_timerange(self, participant_id, metric, start_date, end_date, 
                            is_questionnaire=False, is_todo=False, task_name = None):
        """Get files containing daily data from within a given time range.

        This function retrieves the files that contain data in a given time range. By setting start 
        and end times to the time range of interest, this function returns all the files that
        contain data within this time range. This function is based on unix timestamps, thus it
        does not take into account timezones. In order to find the files containing data within
        the timerange, 12 hours are removed (added) from the start_date (end_date).

        Args:
            participant_id (str): Unique participant identifier, set by study coordinator.
            metric (str): Metric of interest
            start_date (datetime): Start date and time of interest
            end_date (datetime): End date and time of interest
            is_questionnaire (bool, optional): Metric of interest is a questionnaire. Defaults to False.
            is_todo (bool, optional): Metric of interest is a todo. Defaults to False.
            task_name (str, optional): Name of the questionnaire or of the todo. Defaults to None.

        Raises:
            ValueError: _description_

        Returns:
            list: Array with files that are closest to the requested datetime.
        """
        if is_questionnaire and is_todo:
            with ValueError as e:
                raise e + "Select only questionnaire or todo."
        if (is_questionnaire or is_todo) and (task_name is None):
            with ValueError as e:
                raise e + "Please specify name of questionnaire or of todo."
        
        if participant_id not in self.ids:
            return []
        
        # Get full participant_id (user + labfront)
        participant_id = self.get_full_id(participant_id)

        if metric not in self.data_dictionary[participant_id].keys():
            return []
        
        if is_questionnaire or is_todo:
            if task_name not in self.data_dictionary[participant_id][metric].keys():
                return []
            temp_dict = self.data_dictionary[participant_id][metric][task_name]
        else:
            temp_dict = self.data_dictionary[participant_id][metric]
        # Convert dictionary to a pandas dataframe, so that we can sort it
        temp_pd = pd.DataFrame.from_dict(temp_dict, orient='index').sort_values(by=_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY)
        if (start_date is None) and (end_date is None):
            return list(temp_pd.index)
        # Convert date to unix format: YYYY/MM/DD
        # First, make sure that we have a datetime
        if not isinstance(start_date, datetime.datetime):
            start_dt = datetime.datetime.strptime(start_date, "%Y/%m/%d")
        else:
            start_dt = start_date
        if not isinstance(end_date, datetime.datetime):
            end_dt = datetime.datetime.strptime(end_date, "%Y/%m/%d")
        else:
            end_dt = end_date

        # Then, convert it to UNIX timestamp
        start_dt_timestamp = (start_dt - datetime.timedelta(hours=12)).timestamp()
        end_dt_timestamp = (end_dt + datetime.timedelta(hours=12)).timestamp()
        # Compute difference with first and last columns
        temp_pd['min_diff'] = temp_pd[_LABFRONT_FIRST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] - start_dt_timestamp
        temp_pd['max_diff'] = temp_pd[_LABFRONT_LAST_SAMPLE_UNIX_TIMESTAMP_IN_MS_KEY] - end_dt_timestamp

        # For the first time stamp, let's check if we have some files that start before date
        temp_pd_min = temp_pd[temp_pd['min_diff'] < 0]
        if len(temp_pd_min) > 0:
            min_row = temp_pd_min['min_diff'].idxmin()
        else:
            min_row = temp_pd['min_diff'].idxmin()
        
        # For last time stamp, let's check if we have some files that start after date
        temp_pd_max = temp_pd[temp_pd['max_diff'] > 0]
        # Find rows with lowest difference
        if len(temp_pd_max) > 0:
            max_row = temp_pd_max['max_diff'].idxmin()
        else:
            max_row = temp_pd['max_diff'].idxmin()

        return list(temp_pd.loc[min_row:max_row].index)

    def get_data_from_datetime(self, participant_id, metric, start_date=None, 
                                end_date=None, is_questionnaire=False, is_todo=False, task_name = None):
        """Load data from a given participant in a given time frame.

        This function allows to load data of a given metric from a specified participant
        only within a given timeframe. If start_date and end_date are set to None, then
        all data are returned.

        Args:
            participant_id (str): Unique participant identifier, set by study coordinator. 
            metric (str): Metric of interest
            start_date (datetime): Start date and time of interest. Defaults to None.
            end_date (datetime): End date and time of interest. Defaults to None.
            is_questionnaire (bool, optional): Metric of interest is a questionnaire. Defaults to False.
            is_todo (bool, optional): Metric of interest is a todo. Defaults to False.
            task_name (str, optional): Name of the questionnaire or of the todo. Defaults to None.

        Raises:
            ValueError: Not possible to load from both questionnaires and todos at the same time.
            ValueError: No name specified for questionnaire or todo.
            ValueError: The ID of the participant was not found among available IDs.

        Returns:
            pd.DataFrame: Dataframe with the data.
        """
        
        if is_questionnaire and is_todo:
            raise ValueError("Select only questionnaire or todo.")
        if (is_questionnaire or is_todo) and (task_name is None):
            raise ValueError("Specify name of questionnaire or of todo.")
        
        if participant_id not in self.ids:
            raise ValueError(f"participant_id {participant_id} not found.")

        files = self.get_files_timerange(participant_id, metric, start_date, end_date, 
                                         is_questionnaire, is_todo, task_name)
        
        # Get full participant_id (user + labfront)
        participant_id = self.get_full_id(participant_id)

        if len(files) == 0:
            return pd.DataFrame()
        if is_questionnaire:
            path_to_folder = self.data_path / participant_id / _LABFRONT_QUESTIONNAIRE_STRING / task_name
        elif is_todo:
            path_to_folder = self.data_path  / participant_id / _LABFRONT_TODO_STRING / task_name
        else:
            path_to_folder = self.data_path  / participant_id / metric

        n_rows_to_skip= self.get_header_length(path_to_folder / files[0])
        if is_questionnaire:
            n_rows_to_skip += (self.get_key_length(path_to_folder / files[0]) + 1)
        # Load data from first file
        data = pd.read_csv(path_to_folder / files[0], skiprows=n_rows_to_skip)
        for f in files[1:]:
            tmp = pd.read_csv(path_to_folder / f, skiprows=n_rows_to_skip)
            if _LABFRONT_GARMIN_CONNECT_STRING in metric:
                tmp = tmp.drop([_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY, _LABFRONT_UNIXTIMESTAMP_MS_KEY], axis=1)
            data = pd.concat([data, tmp], ignore_index=True)
        if _LABFRONT_GARMIN_CONNECT_STRING in metric:
            # Convert to datetime according to isoformat
            data[_LABFRONT_ISO_DATE_KEY] =  data[_LABFRONT_UNIXTIMESTAMP_MS_KEY] + data[_LABFRONT_GARMIN_CONNECT_TIMEZONEOFFSET_MS_KEY]
            data[_LABFRONT_ISO_DATE_KEY] =  pd.to_datetime(data[_LABFRONT_ISO_DATE_KEY], unit='ms', utc=True)
            data[_LABFRONT_ISO_DATE_KEY] = data[_LABFRONT_ISO_DATE_KEY].dt.tz_localize(None)
        else:
            # Convert unix time stamp
            data[_LABFRONT_ISO_DATE_KEY] = pd.to_datetime(data[_LABFRONT_UNIXTIMESTAMP_MS_KEY], unit='ms', utc=True)
            data[_LABFRONT_ISO_DATE_KEY] = data.groupby(_LABFRONT_GARMIN_DEVICE_TIMEZONEOFFSET_MS_KEY, group_keys=False)[_LABFRONT_ISO_DATE_KEY].apply(lambda x: x.dt.tz_convert(x.name).dt.tz_localize(tz=None))
        # Get data only from given start and end dates
        if (start_date is None) and (not end_date is None):
            return data[(data[_LABFRONT_ISO_DATE_KEY] <= end_date)].reset_index(drop=True)
        elif (not start_date is None) and (end_date is None):
            return data[(data[_LABFRONT_ISO_DATE_KEY] >= start_date)].reset_index(drop=True)
        elif (not start_date is None) and (not end_date is None):
            return data[(data[_LABFRONT_ISO_DATE_KEY] >= start_date)
                        & (data[_LABFRONT_ISO_DATE_KEY] <= end_date)].reset_index(drop=True)
        else:
            return data.reset_index(drop=True)
        
    def get_header_length(self, file_path):
        """Get header length of Labfront csv file.

        Args:
            file_path (str): Path to csv file.
        """
        # Read first line of file
        with open(file_path, 'r') as f:
            line = f.readline().split(',')
        header_length = int(line[1])
        return header_length

    def get_key_length(self, file_path):
        """Get key length of Labfront questionnaire csv file.

        Args:
            file_path (str): Path to csv file of the questionnaire.
        """
        with open(file_path, 'r') as f:
            while True:
                line = f.readline().split(',')
                if line[0] == "Key Length":
                    break
        key_length = int(line[1])
        return key_length

    def get_available_metrics(self, participant_ids="all"):
        """
        Args:
            participant_ids (list):  IDs of participants. Defaults to "all".
        
        Returns:
            list: alphabetically sorted names of the metrics for the participant(s).
        """        
        metrics = set()

        if participant_ids == "all":
            # get all participant ids automatically
            participant_ids = self.get_user_ids()

        if isinstance(participant_ids, str):
            participant_ids = [participant_ids]

        if not isinstance(participant_ids, list):
            raise TypeError("participant_ids has to be a list.")
        
        for participant_id in participant_ids:
            participant_id = self.get_full_id(participant_id)
            participant_path = self.data_path / participant_id
            participant_metrics = set(os.listdir(str(participant_path)))
            metrics |= participant_metrics
        return sorted(list(metrics))

    def get_full_id(self, id):
        """Get full participant ID.

        Args:
            id (str): Unique identifier for the participant.

        Returns:
            str: Full participant ID.
        """
        return id + "_" + self.ids_dict[id]

    def load_garmin_connect_heart_rate(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect heart rate data.

        This function loads Garmin Connect heart rate data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect heart rate data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_HEART_RATE_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_connect_pulse_ox(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect pulse ox data.

        This function loads Garmin Connect pulse ox data from a given
        participant and within a specified date and time range. This
        function loads both daily and sleep pulse ox data. The 
        resulting data frame contains an additional column named 'sleep',
        equal to 1 for pulse ox data acquired during sleep.

        Args:
            data_path (str): Path to the folder containing Labfront data.
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect pulse ox data.
        """
        # We need to load both sleep and daily pulse ox
        daily_data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_DAILY_PULSE_OX_STRING, 
                                                start_date, end_date).reset_index(drop=True)
        # Add sleep label to sleep pulse ox
        sleep_data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_PULSE_OX_STRING, 
                                                start_date, end_date).reset_index(drop=True)
        if len(sleep_data) > 0:
            sleep_data.loc[:,'sleep'] = 1
        # Merge dataframes
        merged_data = pd.merge(daily_data, sleep_data, on=_LABFRONT_ISO_DATE_KEY, how='left')
        merged_data.loc[:,_LABFRONT_SPO2_COLUMN] = merged_data[_LABFRONT_SPO2_COLUMN + '_x']
        merged_data = merged_data.drop([_LABFRONT_SPO2_COLUMN + '_x', _LABFRONT_SPO2_COLUMN + '_y'], axis=1)
        return merged_data

    def load_garmin_connect_respiration(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect respiratory data.

        This function loads Garmin Connect respiratory data from a given
        participant and within a specified date and time range. This
        function loads both daily and sleep respiratory data. The 
        resulting data frame contains an additional column named 'sleep',
        equal to 1 for respiratory data acquired during sleep.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect respiration data.
        """
        # We need to load both sleep and daily pulse ox
        daily_data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_DAILY_RESPIRATION_STRING, 
                                                start_date, end_date).reset_index(drop=True)
        # Add sleep label to sleep pulse ox
        sleep_data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_RESPIRATION_STRING, 
                                                start_date, end_date).reset_index(drop=True)
        if len(sleep_data) > 0:
            sleep_data.loc[:,'sleep'] = 1
        # Merge dataframes
        merged_data = pd.merge(daily_data, sleep_data, on=_LABFRONT_ISO_DATE_KEY, how='left')
        merged_data.loc[:,_LABFRONT_RESPIRATION_COLUMN] = merged_data[_LABFRONT_RESPIRATION_COLUMN + '_x']
        merged_data = merged_data.drop([_LABFRONT_RESPIRATION_COLUMN + '_x', _LABFRONT_RESPIRATION_COLUMN + '_y'], axis=1)
        return merged_data

    def load_garmin_connect_sleep_stage(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect sleep stage data.

        This function loads Garmin Connect sleep stage data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect sleep stage data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_connect_sleep_summary(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect sleep summary data.

        This function loads Garmin Connect sleep summary data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect sleep summary data.
        """
        if _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING in self.get_available_metrics(participant_id):
            data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_SUMMARY_STRING, 
                                                start_date, end_date)
        else:
            data = pd.DataFrame()
        return data

    def load_garmin_connect_stress(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect stress data.

        This function loads Garmin Connect stress data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect stress data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_connect_stress(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect stress data.

        This function loads Garmin Connect stress data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect stress data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_SLEEP_STAGE_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_device_heart_rate(self, participant_id, start_date=None, end_date=None):
        """Load Garmin device heart rate data.

        This function loads Garmin device heart rate data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin device heart rate data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_DEVICE_HEART_RATE_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_device_pulse_ox(self, participant_id, start_date=None, end_date=None):
        """Load Garmin device pulse ox data.

        This function loads Garmin device pulse ox data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin device pulse ox data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_DEVICE_PULSE_OX_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_device_respiration(self, participant_id, start_date=None, end_date=None):
        """Load Garmin device respiratory data.

        This function loads Garmin device respiratory data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin device respiratory data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_DEVICE_RESPIRATION_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_device_step(self, participant_id, start_date=None, end_date=None):
        """Load Garmin device step data.

        This function loads Garmin device step data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin device step data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_DEVICE_STEP_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_device_stress(self, participant_id, start_date=None, end_date=None):
        """Load Garmin device stress data.

        This function loads Garmin device stress data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin device stress data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_DEVICE_STRESS_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_device_stress(self, participant_id, start_date=None, end_date=None):
        """Load Garmin device stress data.

        This function loads Garmin device stress data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin device stress data.
        """
        data = utils.get_data_from_datetime(self, participant_id, _LABFRONT_GARMIN_DEVICE_STRESS_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_device_bbi(self, participant_id, start_date=None, end_date=None):
        """Load Garmin device BBI data.

        This function loads Garmin device beat-to-beat interval (BBI) data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin device BBI data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_DEVICE_BBI_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_connect_body_composition(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect body composition data.

        This function loads Garmin Connect body composition data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect body composition data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_BODY_COMPOSITION_STRING, 
                                                start_date, end_date)
        return data

    def load_garmin_connect_daily_summary(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect daily summary data.

        This function loads Garmin Connect daily summary data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect daily summary data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_DAILY_SUMMARY_STRING, 
                                                start_date, end_date)
        return data
    
    def load_garmin_connect_epoch(self, participant_id, start_date=None, end_date=None):
        """Load Garmin Connect epoch data.

        This function loads Garmin Connect epoch data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing Garmin Connect epoch data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_GARMIN_CONNECT_EPOCH_STRING, 
                                                start_date, end_date)
        return data

    def load_todo(self, participant_id, start_date=None, end_date=None, task_name=None):
        """Load todo data.

        This function loads todo data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.
            task_name (str, optional): Name of the todo of interest. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing todo data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_TODO_STRING, 
                                                start_date, end_date, is_todo=True, task_name=task_name)
        return data

    def load_questionnaire(self, participant_id, start_date=None, end_date=None, task_name=None):
        """Load questionnaire data.

        This function loads questionnaire data from a given
        participant and within a specified date and time range.

        Args:
            participant_id (str): Full ID of the participant
            start_date (datetime, optional): Start date from which data should be retrieved. Defaults to None.
            end_date (datetime, optional): End date from which data should be retrieved. Defaults to None.
            task_name (str, optional): Name of the questionnaire of interest. Defaults to None.

        Returns:
            pd.DataFrame: Dataframe containing questionnaire data.
        """
        data = self.get_data_from_datetime(participant_id, _LABFRONT_QUESTIONNAIRE_STRING, 
                                                start_date, end_date, is_questionnaire=True, task_name=task_name)
        return data