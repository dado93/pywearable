.. include:: ../macros.rst

sleep-stage
===========

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