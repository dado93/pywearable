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

#################################################
#          CSV FILES - COLUMN NAMES             #
#################################################
# General columns #
_ISODATE_COL = "isoDate"
_UNIXTIMESTAMP_IN_MS_COL = "unixTimestampInMs"
_TIMEZONEOFFSET_IN_MS_COL = "timezoneOffsetInMs"


_GARMIN_CONNECT_TIMEZONEOFFSET_IN_MS_COL = "timezoneOffsetInMs"
_GARMIN_DEVICE_TIMEZONEOFFSET_IN_MS_COL = "timezone"
_FIRST_SAMPLE_UNIXTIMESTAMP_IN_MS_COL = "firstSampleUnixTimestampInMs"
_LAST_SAMPLE_UNIXTIMESTAMP_IN_MS_COL = "lastSampleUnixTimestampInMs"

# Sleep summary columns #
_CALENDAR_DATE_COL = "calendarDate"
_SLEEP_SUMMARY_OVERALL_SLEEP_SCORE_COL = "overallSleepScore"
_SLEEP_SUMMARY_DURATION_IN_MS_COL = "durationInMs"
_SLEEP_SUMMARY_DEEP_SLEEP_DURATION_IN_MS_COL = "deepSleepDurationInMs"
_SLEEP_SUMMARY_LIGHT_SLEEP_DURATION_IN_MS_COL = "lightSleepDurationInMs"
_SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL = "remSleepInMs"
_SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL = "awakeDurationInMs"
_SLEEP_SUMMARY_UNMEASURABLE_DURATION_IN_MS_COL = "unmeasurableDurationInMs"
_SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL = "sleepSummaryId"

# Sleep stage columns #
_SLEEP_STAGE_SLEEP_TYPE_COL = "type"
_SLEEP_STAGE_DURATION_IN_MS_COL = "durationInMs"
_SLEEP_STAGE_SLEEP_SUMMARY_ID_COL = "sleepSummaryId"

# Daily summary columns #
_DAILY_SUMMARY_CALENDAR_DATE_COL = "calendarDate"
_DAILY_SUMMARY_STEPS_COL = "steps"
_DAILY_SUMMARY_DISTANCE_COL = "distanceInMeters"
_DAILY_SUMMARY_STEPS_GOAL_COL = "stepsGoal"
_DAILY_SUMMARY_MODERATE_INTENSITY_COL = "moderateIntensityDurationInMs"
_DAILY_SUMMARY_VIGOROUS_INTENSITY_COL = "vigorousIntensityDurationInMs"

# Respiratory data columns #
_RESPIRATION_BREATHS_PER_MINUTE_COL = "breathsPerMinute"
_RESPIRATION_SLEEP_SUMMARY_ID_COL = "sleepSummaryId"
_RESPIRATION_CALENDAR_DATE_COL = "calendarDate"

# Epochs #
_EPOCH_INTENSITY_COL = "intensity"
_EPOCH_ACTIVE_TIME_MS_COL = "activeTimeInMs"

# Todo/Questionnaire columns #
_TODO_NAME_COL = "todoName"
_QUESTIONNAIRE_NAME_COL = "questionnaireName"
_QUESTIONNAIRE_QUESTION_DESCRIPTION_COL = "questionDescription"
_QUESTIONNAIRE_QUESTION_TYPE_COL = "questionType"
_QUESTIONNAIRE_SECTION_INDEX_COL = "sectionIndex"
_QUESTIONNAIRE_QUESTION_INDEX_COL = "questionIndex"
_TASK_SCHEDULE_COL = "taskScheduleRepeat"

#################################################
#           CSV FILES - COLUMN VALUES          #
#################################################

# Sleep stage #
_SLEEP_STAGE_REM_STAGE_VALUE = "rem"
_SLEEP_STAGE_LIGHT_STAGE_VALUE = "light"
_SLEEP_STAGE_DEEP_STAGE_VALUE = "deep"
_SLEEP_STAGE_AWAKE_STAGE_VALUE = "awake"
_SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE = "unmeasurable"

_SLEEP_STAGE_REM_STAGE_MAPPED_VALUE = 4
_SLEEP_STAGE_LIGHT_STAGE_MAPPED_VALUE = 1
_SLEEP_STAGE_DEEP_STAGE_MAPPED_VALUE = 3
_SLEEP_STAGE_AWAKE_STAGE_MAPPED_VALUE = 0
_SLEEP_STAGE_UNMEASURABLE_STAGE_MAPPED_VALUE = -1

# Epochs #
_EPOCH_ACTIVITY_ACTIVE_VALUE = "ACTIVE"
_EPOCH_ACTIVITY_HIGHLY_ACTIVE_VALUE = "HIGHLY_ACTIVE"
_EPOCH_ACTIVITY_SEDENTARY_VALUE = "SEDENTARY"

# Todo/Questionnaire values #
_QUESTIONNAIRE_QUESTION_TYPE_RADIO_VALUE = "radio"
_QUESTIONNAIRE_QUESTION_TYPE_MULTI_SELECT_VALUE = "multi_select"
_QUESTIONNAIRE_QUESTION_TYPE_TEXT_VALUE = "text"

#################################################
#                    REGEX                      #
#################################################
_QUESTIONNAIRE_QUESTION_NAME_REGEX = "option\dName"

#################################################
#              CSV FILES - ROWS                 #
#################################################
_CSV_STATS_SKIP_ROWS = 3
