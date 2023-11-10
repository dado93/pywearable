.. |dataframe| replace:: :class:`pandas.DataFrame`

Metrics and Data Format
-----------------------

This page describes all the metrics that are available to be used in the `pywearable` package.
By metrics, we mean either a measurement (e.g., heart rate, oxygen saturation, ...) and processed measurements
(e.g., sleep summary, daily summary, ...). The class :class:`pywearable.loader.BaseLoader` defines
the loading functions that have to be implemented by the loaders and that support the metrics described
here below. All the metrics are then returned by the loading functions as |dataframe|.
The loading functions are then used in all the other sub-modules for analysis and visualization purposes.

.. contents:: Metrics
    :local:
    :depth: 3

sleep-summary
=============
The sleep summary metric contains summary data for sleep. 
The required fields for this metric are the following ones:

.. list-table:: Sleep summary fields
    :header-rows: 1
    
    * - Name
      - Description
      - Constant
      - Type
    * - sleepSummaryId
      - Unique identifier for a single sleep summary
      - ``pywearable.constants._SLEEP_SUMMARY_ID_COL``
      -
    * - calendarDate
      - Calendar date to which the sleep summary refers to. Date format is 'yyyy-mm-dd'
      - ``pywearable.constants._CALENDAR_DATE_COL``
      - :class:`datetime.date`
    * - timezoneOffsetInMs
      - Timezone offset in milliseconds of the sleep start time
      - ``pywearable.constants._TIMEZONEOFFSET_IN_MS_COL``
      - :class:`int`
    * - unixTimestampInMs
      - Unix timestamp in milliseconds of the sleep start time
      - ``pywearable.constants._UNIXTIMESTAMP_IN_MS_COL``
      - :class:`int`
    * - isoDate
      - Sleep start time in `ISO <https://en.wikipedia.org/wiki/ISO_8601>`__ format
      - :const:`pywearable.constants._ISODATE_COL`
      -
    * - durationInMs
      - Overall sleep duration in milliseconds, **without** counting awake stages
      - ``pywearable.constants._DURATION_IN_MS_COL``
      - :class:`int`
    * - n1SleepDurationInMs
      - Duration of N1 sleep stage in milliseconds
      - ``pywearable.constants._SLEEP_SUMMARY_N1_SLEEP_DURATION_IN_MS_COL``
      - :class:`int`
    * - n2SleepDurationInMs
      - Duration of N2 sleep stage in milliseconds
      - ``pywearable.constants._SLEEP_SUMMARY_N2_SLEEP_DURATION_IN_MS_COL``
      - :class:`int`
    * - n3SleepDurationInMs
      - Duration of N3 sleep stage in milliseconds
      - ``pywearable.constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL``
      - :class:`int`
    * - remSleepDurationInMs
      - Duration of REM sleep stage in milliseconds
      - ``pywearable.constants._SLEEP_SUMMARY_N3_SLEEP_DURATION_IN_MS_COL``
      - :class:`int`
    * - unmeasurableSleepDurationInMs
      - Duration of unmeasurable (i.e., artifacts, movements, ...) in milliseconds
      - ``pywearable.constants._SLEEP_SUMMARY_UNMEASURABLE_SLEEP_DURATION_IN_MS_COL``
      - :class:`int`
    * - awakeDurationInMs
      - Duration of awake stages in milliseconds
      - ``pywearable.constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL``
      - :class:`int`
    * - overallSleepScore
      - Overall sleep score (0-100)
      - ``pywearable.constants._SLEEP_SUMMARY_SLEEP_SCORE_COL``
      - :class:`int`

If one of the metric is not available for a given loader, the column must
still be present in the returned |dataframe| but empty (i.e., `nan`) values
must be set on the rows.

It is possible to have multiple sleep summaries for each calendar date. For example it 
could be possible to have both a night sleep and an afternoon nap with the same ``calendarDate``,
or multiple summaries for a single night sleep in case of updated sleep data.
For this reason, it is necessary to accept the ``same_day_filter`` parameter in the
:meth:`pywearable.loader.BaseLoader.load_sleep_summary` that, when set to ``True`` 
will only return a single sleep summary for each ``calendarDate``, representing
the most updated night sleep.

An example of a sleep-summary is shown in the table below.

.. list-table:: Example of sleep summary
   :widths: 25 25 25 25 25 25 25 25 25 25 25 25 25
   :header-rows: 1

   * - sleepSummaryId
     - calendarDate
     - timezoneOffsetInMs
     - unixTimestampInMs
     - isoDate
     - durationInMs
     - n1SleepDurationInMs
     - n2SleepDurationInMs
     - n3SleepDurationInMs
     - remSleepDurationInMs
     - unmeasurableSleepDurationInMs
     - awakeDurationInMs
     - overallSleepScore
   * - x35bda69-64f79cac-6888
     - 2023-09-06
     - 7200000
     - 1693949100000
     - 2023-09-05T23:25:00.000+02:00
     - 26760000
     - 19740000
     - 
     - 1620000
     - 4560000
     - 840000
     - 120000
     - 80
   * - x35bda69-64f8eae4-6630
     - 2023-09-07
     - 7200000
     - 1694034660000
     - 2023-09-06T23:11:00.000+02:00
     - 26160000
     - 19980000
     - 
     - 2280000
     - 3900000
     - 0
     - 12000
     - 75
   * - x35bda69-64f8eae4-666c
     - 2023-09-07
     - 7200000
     - 1694034660000
     - 2023-09-06T23:11:00.000+02:00
     - 26220000
     - 20160000
     - 
     - 2340000
     - 3720000
     - 0
     - 6000
     - 85

sleep-stage
=============
The sleep stage metric contains information about sleep stages and
their duration. Each row of the returned |dataframe| represents a single
sleep stage, with its duration and type. For example, if `n1` sleep stage 
occurred from `2023-09-06T01:23:00.000+02:00` to `2023-09-06T01:26:00.000+02:00`, 
so with a total duration of 3 minutes (180000 milliseconds),
then the corresponding row in the |dataframe| would look like this:

.. list-table:: Example N1 sleep stage entry
    :header-rows: 1

   * - sleepSummaryId
     - timezoneOffsetInMs
     - unixTimestampInMs
     - isoDate
     - durationInMs
     - type
   * - x35bda69-64f79cac-6888
     - 7200000
     - 1693949100000
     - 2023-09-06T01:23:00.000+02:00
     - 180000
     - n1

The required fields for this metric are the following ones:

.. list-table:: Sleep stage fields
    :header-rows: 1
    
    * - Name
      - Description
      - Constant
    * - sleepSummaryId
      - Unique identifier for the sleep summary to which sleep stages refer to
      - ``pywearable.constants._SLEEP_SUMMARY_ID_COL``
    * - timezoneOffsetInMs
      - Timezone offset in milliseconds of the sleep stage start time
      - ``pywearable.constants._TIMEZONEOFFSET_IN_MS_COL``
    * - unixTimestampInMs
      - Unix timestamp in milliseconds of the sleep stage start time
      - ``pywearable.constants._UNIXTIMESTAMP_IN_MS_COL``
    * - isoDate
      - Sleep start time in `ISO <https://en.wikipedia.org/wiki/ISO_8601>`_ format
      - ``pywearable.constants._ISODATE_COL``
    * - durationInMs
      - Duration in milliseconds of the sleep stage
      - ``pywearable.constants._DURATION_IN_MS_COL``
    * - type
      - Type of sleep stages. Available options are:
        
        - n1 (``pywearable.constants._SLEEP_STAGE_N1_STAGE_COL``)
        - n2 (``pywearable.constants._SLEEP_STAGE_N2_STAGE_COL``)
        - n3 (``pywearable.constants._SLEEP_STAGE_N3_STAGE_COL``)
        - rem (``pywearable.constants._SLEEP_STAGE_REM_STAGE_COL``)
        - awake (``pywearable.constants._SLEEP_STAGE_AWAKE_STAGE_COL``)
        - unmeasurable (``pywearable.constants._SLEEP_STAGE_UNMEASURABLE_STAGE_VALUE``)
      - ``pywearable.constants._SLEEP_STAGE_SLEEP_TYPE_COL``

An example of a sleep-stage is shown in the table below.

.. list-table:: Example of sleep stage
   :header-rows: 1

   * - sleepSummaryId
     - timezoneOffsetInMs
     - unixTimestampInMs
     - isoDate
     - durationInMs
     - type
   * - x35bda69-64f79cac-6888
     - 7200000
     - 1693949100000
     - 2023-09-05T23:25:00.000+02:00
     - 420000
     - rem
   * - x35bda69-64f79cac-6888
     - 7200000
     - 1693949520000
     - 2023-09-05T23:32:00.000+02:00
     - 240000
     - n1
   * - x35bda69-64f79cac-6888
     - 7200000
     - 1693949760000
     - 2023-09-05T23:36:00.000+02:00
     - 420000
     - rem
   * - x35bda69-64f79cac-6888
     - 7200000
     - 1693950180000
     - 2023-09-05T23:43:00.000+02:00
     - 5520000
     - n1
   * - x35bda69-64f79cac-6888
     - 7200000
     - 1693955700000
     - 2023-09-06T01:15:00.000+02:00
     - 480000
     - rem
   * - x35bda69-64f79cac-6888
     - 7200000
     - 1693956180000
     - 2023-09-06T01:23:00.000+02:00
     - 4560000
     - n1

steps
=====
The steps metric contains information about the recorded steps as measured
by the wearable. Each row of the returned |dataframe| represents the measured
steps and the amount of type to which the measured steps refer to.

The required fields for the steps are the following ones:

.. list-table:: Steps fields
    :header-rows: 1
    
    * - Name
      - Description
      - Constant
    * - timezoneOffsetInMs
      - Timezone offset in milliseconds of the steps start time
      - ``pywearable.constants._TIMEZONEOFFSET_IN_MS_COL``
    * - unixTimestampInMs
      - Unix timestamp in milliseconds of the steps start time
      - ``pywearable.constants._UNIXTIMESTAMP_IN_MS_COL``
    * - isoDate
      - Steps start time in `ISO <https://en.wikipedia.org/wiki/ISO_8601>`_ format
      - ``pywearable.constants._ISODATE_COL``
    * - durationInMs
      - Duration in milliseconds of the collected
      - ``pywearable.constants._DURATION_IN_MS_COL``
    * - steps
      - Amount of steps recorded from 
      - ``pywearable.constants._STEPS_COL``

daily-summary
=============

heart-rate
==========

respiration
===========

pulse-ox
========
