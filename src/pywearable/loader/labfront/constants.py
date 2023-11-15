##################################################
#               FOLDER NAMES                     #
##################################################

# Garmin Connect metrics - Folder names #
_GARMIN_CONNECT_BASE_FOLDER = "garmin-connect"
_GARMIN_CONNECT_BODY_COMPOSITION_FOLDER = (
    _GARMIN_CONNECT_BASE_FOLDER + "-body-composition"
)
_GARMIN_CONNECT_HEART_RATE_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-daily-heart-rate"
_GARMIN_CONNECT_DAILY_SUMMARY_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-daily-summary"
_GARMIN_CONNECT_DAILY_PULSE_OX_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-pulse-ox"
_GARMIN_CONNECT_SLEEP_PULSE_OX_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-sleep-pulse-ox"
_GARMIN_CONNECT_DAILY_RESPIRATION_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-respiration"
_GARMIN_CONNECT_SLEEP_RESPIRATION_FOLDER = (
    _GARMIN_CONNECT_BASE_FOLDER + "-sleep-respiration"
)
_GARMIN_CONNECT_SLEEP_STAGE_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-sleep-stage"
_GARMIN_CONNECT_SLEEP_SUMMARY_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-sleep-summary"
_GARMIN_CONNECT_EPOCH_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-epoch"
_GARMIN_CONNECT_STRESS_FOLDER = _GARMIN_CONNECT_BASE_FOLDER + "-stress"

# Garmin Device metrics - Folder names #
_GARMIN_DEVICE_FOLDER = "garmin-device"
_GARMIN_DEVICE_BBI_FOLDER = _GARMIN_DEVICE_FOLDER + "-bbi"
_GARMIN_DEVICE_HEART_RATE_FOLDER = _GARMIN_DEVICE_FOLDER + "-heart-rate"
_GARMIN_DEVICE_PULSE_OX_FOLDER = _GARMIN_DEVICE_FOLDER + "-pulse-ox"
_GARMIN_DEVICE_RESPIRATION_FOLDER = _GARMIN_DEVICE_FOLDER + "-respiration"
_GARMIN_DEVICE_STEP_FOLDER = _GARMIN_DEVICE_FOLDER + "-step"
_GARMIN_DEVICE_STRESS_FOLDER = _GARMIN_DEVICE_FOLDER + "-stress"

# Questionnaire and Todo - Folder names #
_QUESTIONNAIRE_FOLDER = "questionnaire"
_TODO_FOLDER = "todo"

# Labfront-specific CSV columns
_GARMIN_CONNECT_TIMEZONEOFFSET_IN_MS_COL = "timezoneOffsetInMs"
_GARMIN_DEVICE_TIMEZONEOFFSET_IN_MS_COL = "timezone"
_FIRST_SAMPLE_UNIXTIMESTAMP_IN_MS_COL = "firstSampleUnixTimestampInMs"
_LAST_SAMPLE_UNIXTIMESTAMP_IN_MS_COL = "lastSampleUnixTimestampInMs"

##################################################
#            Sleep Summary Columns               #
##################################################
_SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL = "deepSleepDurationInMs"
_SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL = "lightSleepDurationInMs"
_SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL = "remSleepInMs"
_SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL = "awakeDurationInMs"
_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_DURATION_IN_MS_COL = "unmeasurableSleepInMs"

##################################################
#         Sleep Stages - Type values             #
##################################################
_SLEEP_STAGE_LIGHT_STAGE_VALUE = "light"
_SLEEP_STAGE_DEEP_STAGE_VALUE = "deep"
_SLEEP_STAGE_REM_STAGE_VALUE = "rem"
_SLEEP_STAGE_AWAKE_STAGE_VALUE = "awake"
_SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE = "unmeasurable"
