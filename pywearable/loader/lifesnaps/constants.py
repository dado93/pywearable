##################################
#           Metric Names         #
##################################
_METRIC_SPO2 = "daily-spo2"
_METRIC_COMP_TEMP = "temprature-computed"
_METRIC_DEVICE_TEMP = "temperature-device"
_METRIC_DAILY_HRV_SUMMARY = "hrv-daily-summary"
_METRIC_HRV_DETAILS = "hrv-details"
_METRIC_PROFILE = "profile"
_METRIC_RESPIRATORY_RATE_SUMMARY = "respiratory-rate-summary"
_METRIC_STRESS = "stress"
_METRIC_WRIST_TEMPERATURE = "temperature-wrist"
_METRIC_ALTITUDE = "altitude"
_METRIC_BADGE = "badge"
_METRIC_CALORIES = "calories"
_METRIC_HRV_HISTOGRAM = "hrv-histogram"
_METRIC_DISTANCE = "distance"
_METRIC_EST_OXY_VARIATION = "estimated-oxygen-variation"
_METRIC_HEART_RATE = "heart-rate"
_METRIC_JOURNAL_ENTRIES = "journal_entries"
_METRIC_LIGHTLY_ACTIVE_MINUTES = "lightly-active-minutes"
_METRIC_MODERATELY_ACTIVE_MINUTES = "moderately-active-minutes"
_METRIC_SEDENTARY_MINUTES = "sedentary-minutes"
_METRIC_VERY_ACTIVE_MINUTES = "very_active_minutes"
_METRIC_STEPS = "steps"
_METRIC_WATER_LOGS = "water-logs"
_METRIC_RESTING_HEART_RATE = "resting-heart-rate"
_METRIC_TIME_IN_HR_ZONES = "time-in-hr-zones"
_METRIC_DEMOGRAPHIC_VO2_MAX = "demographic-vo2-max"
_METRIC_ECG = "ecg"
_METRIC_MINDFULNESS_GOALS = "mindfulness-goals"

##################################
#      General Columns           #
##################################
_UNIXTIMESTAMP_IN_MS_COL = "unixTimestampInMs"
_ISODATE_COL = "isoDate"
_TIMEZONEOFFSET_IN_MS_COL = "timezoneOffsetInMs"
_STEPS_COL = "steps"
_TOTAL_STEPS_COL = "totalSteps"
_CALENDAR_DATE_COL = "calendarDate"

##################################
#        Sleep Columns           #
##################################
_SLEEP_DEEP_DURATION_IN_MS_COL = "deepSleepDurationInMs"
_SLEEP_LIGHT_DURATION_IN_MS_COL = "lightSleepDurationInMs"
_SLEEP_REM_DURATION_IN_MS_COL = "remSleepInMs"
_SLEEP_AWAKE_DURATION_IN_MS_COL = "awakeDurationInMs"

##################################
#     HRV Histogram Columns      #
##################################
_HRV_HISTOGRAM_BUCKET_WIDTHS_COL = "bucketWidths"
_HRV_HISTOGRAM_BUCKET_VALUES_COL = "bucketValues"

##################################
#           ECG Columns          #
##################################
_ECG_SAMPLE_VALUE_COL = "value"

##################################
#           Database             #
##################################
_DB_NAME = "rais_anonymized"

##################################
#       FitBit Collection        #
##################################
_DB_FITBIT_COLLECTION_NAME = "fitbit"
_DB_FITBIT_COLLECTION_TYPE_KEY = "type"
_DB_FITBIT_COLLECTION_ID_KEY = "id"
_DB_FITBIT_COLLECTION_DATA_KEY = "data"

# --------------------------------#
#          Document types         #
# --------------------------------#
_DB_FITBIT_COLLECTION_DATA_TYPE_SLEEP = "sleep"
_DB_FITBIT_COLLECTION_DATA_TYPE_COMP_TEMP = "Computed Temperature"
_DB_FITBIT_COLLECTION_DATA_TYPE_DAILY_HRV_SUMMARY = (
    "Daily Heart Rate Variability Summary"
)
_DB_FITBIT_COLLECTION_DATA_TYPE_DAILY_SPO2 = "Daily SpO2"
_DB_FITBIT_COLLECTION_DATA_TYPE_DEVICE_TEMP = "Device Temperature"
_DB_FITBIT_COLLECTION_DATA_TYPE_AFIB_ECG_READINGS = "Afib ECG Readings"
_DB_FITBIT_COLLECTION_DATA_TYPE_HRV_DETAILS = "Heart Rate Variability Details"
_DB_FITBIT_COLLECTION_DATA_TYPE_HRV_HISTOGRAM = "Heart Rate Variability Histogram"
_DB_FITBIT_COLLECTION_DATA_TYPE_PROFILE = "Profile"
_DB_FITBIT_COLLECTION_DATA_TYPE_RESPIRATORY_RATE_SUMMARY = "Respiratory Rate Summary"
_DB_FITBIT_COLLECTION_DATA_TYPE_STRESS_SCORE = "Stress Score"
_DB_FITBIT_COLLECTION_DATA_TYPE_WRIST_TEMPERATURE = "Wrist Temperature"
_DB_FITBIT_COLLECTION_DATA_TYPE_ALTITUDE = "altitude"
_DB_FITBIT_COLLECTION_DATA_TYPE_BADGE = "badge"
_DB_FITBIT_COLLECTION_DATA_TYPE_CALORIES = "calories"
_DB_FITBIT_COLLECTION_DATA_TYPE_DEMOGRAPHIC_VO2_MAX = "demographic_vo2_max"
_DB_FITBIT_COLLECTION_DATA_TYPE_DISTANCE = "distance"
_DB_FITBIT_COLLECTION_DATA_TYPE_ESTIMATED_OXYGEN_VARIATION = (
    "estimated_oxygen_variation"
)
_DB_FITBIT_COLLECTION_DATA_TYPE_HEART_RATE = "heart_rate"
_DB_FITBIT_COLLECTION_DATA_TYPE_JOURNAL_ENTRIES = "journal_entries"
_DB_FITBIT_COLLECTION_DATA_TYPE_LIGHTLY_ACTIVE_MINUTES = "lightly_active_minutes"
_DB_FITBIT_COLLECTION_DATA_TYPE_MODERATELY_ACTIVE_MINUTES = "moderately_active_minutes"
_DB_FITBIT_COLLECTION_DATA_TYPE_SEDENTARY_MINUTES = "sedentary_minutes"
_DB_FITBIT_COLLECTION_DATA_TYPE_VERY_ACTIVE_MINUTES = "very_active_minutes"
_DB_FITBIT_COLLECTION_DATA_TYPE_STEPS = "steps"
_DB_FITBIT_COLLECTION_DATA_TYPE_WATER_LOGS = "water_logs"
_DB_FITBIT_COLLECTION_DATA_TYPE_RESTING_HEART_RATE = "resting_heart_rate"
_DB_FITBIT_COLLECTION_DATA_TYPE_TIME_IN_HR_ZONES = "time_in_heart_rate_zones"
_DB_FITBIT_COLLECTION_DATA_TYPE_MINDFULNESS_GOALS = "mindfulness_goals"
"""
'exercise', 'mindfulness_eda_data_sessions', 
'mindfulness_sessions', ]
"""


# --------------------------------#
#         Sleep Documents         #
# --------------------------------#
_DB_FITBIT_COLLECTION_SLEEP_DATA_LOG_ID_KEY = "logId"
_DB_FITBIT_COLLECTION_SLEEP_DATA_DATE_OF_SLEEP_KEY = "dateOfSleep"
_DB_FITBIT_COLLECTION_SLEEP_DATA_START_TIME_KEY = "startTime"
_DB_FITBIT_COLLECTION_SLEEP_DATA_END_TIME_KEY = "endTime"
_DB_FITBIT_COLLECTION_SLEEP_DATA_DURATION_KEY = "duration"
_DB_FITBIT_COLLECTION_SLEEP_DATA_MIN_TO_FALL_ASLEEP_KEY = "minutesToFallAsleep"
_DB_FITBIT_COLLECTION_SLEEP_DATA_MIN_ASLEEP_KEY = "minutesAsleep"
_DB_FITBIT_COLLECTION_SLEEP_DATA_MIN_AWAKE_KEY = "minutesAwake"
_DB_FITBIT_COLLECTION_SLEEP_DATA_MIN_AFTER_WAKEUP_KEY = "minutesAfterWakeup"
_DB_FITBIT_COLLECTION_SLEEP_DATA_TIME_IN_BED_KEY = "timeInBed"
_DB_FITBIT_COLLECTION_SLEEP_DATA_EFFICIENCY_KEY = "efficiency"
_DB_FITBIT_COLLECTION_SLEEP_DATA_MAIN_SLEEP_KEY = "mainSleep"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_KEY = "levels"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SUMMARY_KEY = "summary"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SUMMARY_DEEP_KEY = "deep"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SUMMARY_LIGHT_KEY = "light"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SUMMARY_REM_KEY = "rem"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SUMMARY_WAKE_KEY = "wake"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_KEY = "data"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_DATETIME_KEY = "dateTime"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_SECONDS_KEY = "seconds"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_DATA_LEVEL_KEY = "level"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LEVELS_SHORT_DATA_KEY = "shortData"
_DB_FITBIT_COLLECTION_SLEEP_DATA_TYPE_KEY = "type"
_DB_FITBIT_COLLECTION_SLEEP_DATA_INFO_CODE_KEY = "infoCode"
_DB_FITBIT_COLLECTION_SLEEP_DATA_DEEP_COUNT_KEY = "deepCount"
_DB_FITBIT_COLLECTION_SLEEP_DATA_DEEP_MIN_KEY = "deepMinutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_DEEP_30_DAYS_AVG_MIN_KEY = "deepThirtydayavgminutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_WAKE_COUNT_KEY = "wakeCount"
_DB_FITBIT_COLLECTION_SLEEP_DATA_WAKE_MIN_KEY = "wakeMinutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_WAKE_30_DAYS_AVG_MIN_KEY = "wakeThirtydayavgminutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LIGHT_COUNT_KEY = "lightCount"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LIGHT_MIN_KEY = "lightMinutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_LIGHT_30_DAYS_AVG_MIN_KEY = "lightThirtydayavgminutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_REM_COUNT_KEY = "remCount"
_DB_FITBIT_COLLECTION_SLEEP_DATA_REM_MIN_KEY = "remMinutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_REM_30_DAYS_AVG_MIN_KEY = "remThirtydayavgminutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_RESTLESS_COUNT_KEY = "restlessCount"
_DB_FITBIT_COLLECTION_SLEEP_DATA_RESTLESS_MIN_KEY = "restlessMinutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_AWAKE_COUNT_KEY = "awakeCount"
_DB_FITBIT_COLLECTION_SLEEP_DATA_AWAKE_MIN_KEY = "awakeMinutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_ASLEEP_COUNT_KEY = "asleepCount"
_DB_FITBIT_COLLECTION_SLEEP_DATA_ASLEEP_MIN_KEY = "asleepMinutes"
_DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_WAKE_VALUE = "wake"
_DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_DEEP_VALUE = "deep"
_DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_LIGHT_VALUE = "light"
_DB_FITBIT_COLLECTION_SLEEP_DATA_STAGE_REM_VALUE = "rem"

# ---------------------------------------------#
#      Converted Temperature Documents         #
# ---------------------------------------------#
_DB_FITBIT_COLLECTION_COMP_TEMP_SLEEP_START_KEY = "sleep_start"
_DB_FITBIT_COLLECTION_COMP_TEMP_SLEEP_END_KEY = "sleep_end"

# --------------------------------#
#          SPo2 Documents         #
# --------------------------------#
_DB_FITBIT_COLLECTION_SPO2_TIMESTAMP_KEY = "timestamp"

# --------------------------------#
#  Device Temperature Documents   #
# --------------------------------#
_DB_FITBIT_COLLECTION_DEVICE_TEMP_RECORDED_TIME_KEY = "recorded_time"

# --------------------------------#
#   Daily HRV Summary Documents   #
# --------------------------------#
_DB_FITBIT_COLLECTION_DAILY_HRV_SUMMARY_TIMESTAMP_KEY = "timestamp"
_DB_FITBIT_COLLECTION_DAILY_HRV_SUMMARY_RMSSD_KEY = "rmssd"
_DB_FITBIT_COLLECTION_DAILY_HRV_SUMMARY_NREMHR_KEY = "nremhr"
_DB_FITBIT_COLLECTION_DAILY_HRV_SUMMARY_ENTROPY_KEY = "entropy"

# --------------------------------#
#    HRV Details Documents        #
# --------------------------------#
_DB_FITBIT_COLLECTION_HRV_DETAILS_TIMESTAMP_KEY = "timestamp"
_DB_FITBIT_COLLECTION_HRV_DETAILS_COVERAGE_KEY = "coverage"
_DB_FITBIT_COLLECTION_HRV_DETAILS_LOW_FREQUENCY_KEY = "low_frequency"
_DB_FITBIT_COLLECTION_HRV_DETAILS_HIGH_FREQUENCY_KEY = "high_frequency"
_DB_FITBIT_COLLECTION_HRV_DETAILS_RMSSD_KEY = "rmssd"

# --------------------------------#
#       Profile Documents         #
# --------------------------------#
_DB_FITBIT_COLLECTION_PROFILE_GENDER_COL = "gender"
_DB_FITBIT_COLLECTION_PROFILE_BMI_COL = "bmi"
_DB_FITBIT_COLLECTION_PROFILE_AGE_COL = "age"

# ------------------------------------#
#  Respiratory Rate Summary Documents #
# ------------------------------------#
_DB_FITBIT_COLLECTION_RESP_RATE_SUMMARY_FULL_SLEEP_BREATHING_RATE_COL = (
    "full_sleep_breathing_rate"
)
_DB_FITBIT_COLLECTION_RESP_RATE_SUMMARY_TIMESTAMP_COL = "timestamp"

# --------------------------------#
#     Stress Score Documents      #
# --------------------------------#
_DB_FITBIT_COLLECTION_STRESS_SCORE_DATE_COL = "DATE"

# --------------------------------#
#     Wrist Temperature Docs      #
# --------------------------------#
_DB_FITBIT_COLLECTION_WRIST_TEMP_RECORDED_TIME_COL = "recorded_time"
_DB_FITBIT_COLLECTION_WRIST_TEMP_TEMP_COL = "temperature"

# --------------------------------#
#     Wrist Temperature Docs      #
# --------------------------------#
_DB_FITBIT_COLLECTION_ALTITUDE_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_ALTITUDE_ALTITUDE_COL = "value"

# --------------------------------#
#     Wrist Temperature Docs      #
# --------------------------------#
_DB_FITBIT_COLLECTION_BADGE_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_BADGE_TYPE_COL = "badgeType"
_DB_FITBIT_COLLECTION_BADGE_VALUE_COL = "value"


# --------------------------------#
#          Calories Docs          #
# --------------------------------#
_DB_FITBIT_COLLECTION_CALORIES_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_CALORIES_VALUE_COL = "value"

# --------------------------------#
#          Distance Docs          #
# --------------------------------#
_DB_FITBIT_COLLECTION_DISTANCE_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_DISTANCE_VALUE_COL = "value"

# ----------------------------------#
#  Estimated Oxygen Variation Docs  #
# ----------------------------------#
_DB_FITBIT_COLLECTION_EST_OXY_VAR_DATETIME_COL = "timestamp"
_DB_FITBIT_COLLECTION_EST_OXY_VAR_VALUE_COL = "Infrared to Red Signal Ratio"

# ----------------------------------#
#        Heart Rate Docs            #
# ----------------------------------#
_DB_FITBIT_COLLECTION_HEART_RATE_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_HEART_RATE_VALUE_KEY = "value"
_DB_FITBIT_COLLECTION_HEART_RATE_VALUE_BPM_COL = "bpm"
_DB_FITBIT_COLLECTION_HEART_RATE_VALUE_CONFIDENCE_COL = "confidence"

# ----------------------------------#
#       Journal Entries Docs        #
# ----------------------------------#
_DB_FITBIT_COLLECTION_JOURNAL_ENTRIES_LOG_TIME_COL = "log_time"
_DB_FITBIT_COLLECTION_JOURNAL_ENTRIES_LOG_TYPE_COL = "log_type"
_DB_FITBIT_COLLECTION_JOURNAL_ENTRIES_PLATFORM_COL = "platform"
_DB_FITBIT_COLLECTION_JOURNAL_ENTRIES_SOURCE_COL = "source"

# ----------------------------------#
#    Lightly Active Minutes Docs    #
# ----------------------------------#
_DB_FITBIT_COLLECTION_LIGHTLY_ACTIVE_MIN_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_LIGHTLY_ACTIVE_MIN_VALUE_COL = "value"

# ----------------------------------#
#   Moderately Active Minutes Docs  #
# ----------------------------------#
_DB_FITBIT_COLLECTION_MODERATELY_ACTIVE_MIN_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_MODERATELY_ACTIVE_MIN_VALUE_COL = "value"

# ----------------------------------#
#    Very Active Minutes Docs       #
# ----------------------------------#
_DB_FITBIT_COLLECTION_VERY_ACTIVE_MIN_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_VERY_ACTIVE_MIN_VALUE_COL = "value"

# ----------------------------------#
#     Sedentary Minutes Docs        #
# ----------------------------------#
_DB_FITBIT_COLLECTION_SEDENTARY_MIN_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_SEDENTARY_MIN_VALUE_COL = "value"

# ----------------------------------#
#           Steps Docs              #
# ----------------------------------#
_DB_FITBIT_COLLECTION_STEPS_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_STEPS_VALUE_COL = "value"

# ----------------------------------#
#       Water Logs Docs             #
# ----------------------------------#
_DB_FITBIT_COLLECTION_WATER_LOGS_DATE_COL = "date"
_DB_FITBIT_COLLECTION_WATER_LOGS_WATER_AMOUNT_COL = "waterAmount"
_DB_FITBIT_COLLECTION_WATER_LOGS_MEASUREMENT_UNIT_COL = "measurementUnit"

# ----------------------------------#
#    Resting Heart Rate Docs        #
# ----------------------------------#
_DB_FITBIT_COLLECTION_RESTING_HEART_RATE_DATETIME_COL = "dateTime"
_DB_FITBIT_COLLECTION_RESTING_HEART_RATE_VALUE_KEY = "value"
_DB_FITBIT_COLLECTION_RESTING_HEART_RATE_VALUE_VALUE_COL = "value"
_DB_FITBIT_COLLECTION_RESTING_HEART_RATE_VALUE_ERROR_COL = "error"
_DB_FITBIT_COLLECTION_RESTING_HEART_RATE_VALUE_DATE_COL = "date"

# ----------------------------------#
#      Time in HR Zones Docs        #
# ----------------------------------#
_DB_FITBIT_COLLECTION_TIME_IN_HR_ZONES_DATETIME_COL = "dateTime"

# ----------------------------------#
#        HRV Histogram Docs         #
# ----------------------------------#
_DB_FITBIT_COLLECTION_HRV_HISTOGRAM_TIMESTAMP_COL = "timestamp"
_DB_FITBIT_COLLECTION_HRV_HISTOGRAM_BUCKET_VALUES_COL = "bucket_values"

# ----------------------------------#
#    Demographic VO2 Max Docs       #
# ----------------------------------#
_DB_FITBIT_COLLECTION_DEMOGRAPHIC_VO2_MAX_DATETIME_COL = "dateTime"

# ----------------------------------#
#       ECG Recordings Docs         #
# ----------------------------------#
_DB_FITBIT_COLLECTION_AFIB_ECG_READINGS_DATETIME_COL = "reading_time"
_DB_FITBIT_COLLECTION_AFIB_ECG_READINGS_WAVEFORM_SAMPLES_COL = "waveform_samples"

# ----------------------------------#
#     Mindfulness Goals Docs        #
# ----------------------------------#
_DB_FITBIT_COLLECTION_MINDFULNESS_GOALS_DATE_COL = "date"
