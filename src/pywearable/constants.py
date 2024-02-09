_METRIC_HEART_RATE = "heart-rate"
_METRIC_STRESS = "stress"
_METRIC_SLEEP_SUMMARY = "sleep-summary"
_METRIC_SLEEP_STAGE = "sleep-stage"
_METRIC_PULSE_OX = "pulse-ox"
_METRIC_RESPIRATION = "respiration"
_METRIC_SLEEP_RESPIRATION = "sleep-respiration"
_METRIC_SLEEP_PULSE_OX = "sleep-pulse-ox"
#################################################
#          CSV FILES - COLUMN NAMES             #
#################################################
# General columns #

#: Column for date in ISO format
_ISODATE_COL = "isoDate"

#: Column for unix timestamp in milliseconds
_UNIXTIMESTAMP_IN_MS_COL = "unixTimestampInMs"

#: Column for timezone offset in milliseconds
_TIMEZONEOFFSET_IN_MS_COL = "timezoneOffsetInMs"

#: Column for calendar date
_CALENDAR_DATE_COL = "calendarDate"
_SLEEP_SUMMARY_ID_COL = "sleepSummaryId"

#: Column duration expressed in milliseconds
_DURATION_IN_MS_COL = "durationInMs"

#: Column for entries in which sleep is detected
_IS_SLEEPING_COL = "isSleeping"

# spo2 columns #
_SPO2_SPO2_COL = "spo2"

# Sleep summary columns #
_SLEEP_SUMMARY_OVERALL_SLEEP_SCORE_COL = "overallSleepScore"
_SLEEP_SUMMARY_DURATION_IN_MS_COL = "durationInMs"
_SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL = "n1SleepDurationInMs"
_SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL = "n2SleepDurationInMs"
_SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL = "n3SleepDurationInMs"
_SLEEP_SUMMARY_REM_SLEEP_DURATION_IN_MS_COL = "remSleepDurationInMs"
_SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL = "awakeDurationInMs"
_SLEEP_SUMMARY_UNMEASURABLE_SLEEP_DURATION_IN_MS_COL = "unmeasurableSleepDurationInMs"

_SLEEP_SUMMARY_SLEEP_SUMMARY_ID_COL = "sleepSummaryId"

# Sleep stage columns #
_SLEEP_STAGE_SLEEP_TYPE_COL = "type"
_SLEEP_STAGE_DURATION_IN_MS_COL = "durationInMs"
_SLEEP_STAGE_SLEEP_SUMMARY_ID_COL = "sleepSummaryId"

# Stress columns #
_STRESS_STRESS_LEVEL_COL = "stressLevel"
_STRESS_BODY_BATTERY_COL = "bodyBattery"

# Daily summary columns #
_DAILY_SUMMARY_CALENDAR_DATE_COL = "calendarDate"
_DAILY_SUMMARY_STEPS_COL = "steps"
_DAILY_SUMMARY_DISTANCE_COL = "distanceInMeters"
_DAILY_SUMMARY_STEPS_GOAL_COL = "stepsGoal"
_DAILY_SUMMARY_MODERATE_INTENSITY_COL = "moderateIntensityDurationInMs"
_DAILY_SUMMARY_VIGOROUS_INTENSITY_COL = "vigorousIntensityDurationInMs"
_DAILY_SUMMARY_AVG_STRESS_IN_STRESS_LVL_COL = "averageStressInStressLevel"
_DAILY_SUMMARY_MAX_STRESS_IN_STRESS_LVL_COL = "maxStressInStressLevel"
_DAILY_SUMMARY_REST_STRESS_DURATION_IN_MS_COL = "restStressDurationInMs"
_DAILY_SUMMARY_LOW_STRESS_DURATION_IN_MS_COL = "lowStressDurationInMs"
_DAILY_SUMMARY_MEDIUM_STRESS_DURATION_IN_MS_COL = "mediumStressDurationInMs"
_DAILY_SUMMARY_HIGH_STRESS_DURATION_IN_MS_COL = "highStressDurationInMs"
_DAILY_SUMMARY_UNRELIABLE_STRESS_DURATION_IN_MS_COL = "activityStressDurationInMs"
_DAILY_SUMMARY_STRESS_SCORE_COL = "stressQualifier"

# Respiratory data columns #
_RESPIRATION_BREATHS_PER_MINUTE_COL = "breathsPerMinute"
_RESPIRATION_SLEEP_SUMMARY_ID_COL = "sleepSummaryId"
_RESPIRATION_CALENDAR_DATE_COL = "calendarDate"

# Cardiac data columns #
_SPO2_COLUMN = "spo2"
_HR_COLUMN = "beatsPerMinute"
_RESTING_HR_COLUMN = "restingHeartRateInBeatsPerMinute"
_AVG_HR_COLUMN = "averageHeartRateInBeatsPerMinute"
_MAX_HR_COLUMN = "maxHeartRateInBeatsPerMinute"
_MIN_HR_COLUMN = "minHeartRateInBeatsPerMinute"

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

# User column (for index and related)
_USER_COL = "user"

#################################################
#           CSV FILES - COLUMN VALUES          #
#################################################

# Sleep stage #
_SLEEP_STAGE_REM_STAGE_VALUE = "rem"
_SLEEP_STAGE_N1_STAGE_VALUE = "n1"
_SLEEP_STAGE_N2_STAGE_VALUE = "n2"
_SLEEP_STAGE_N3_STAGE_VALUE = "n3"
_SLEEP_STAGE_AWAKE_STAGE_VALUE = "awake"
_SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE = "unmeasurable"

# Hypnogram
_SLEEP_STAGE_REM_STAGE_MAPPED_VALUE = 4
_SLEEP_STAGE_N1_STAGE_MAPPED_VALUE = 1
_SLEEP_STAGE_N2_STAGE_MAPPED_VALUE = 2
_SLEEP_STAGE_N3_STAGE_MAPPED_VALUE = 3
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
