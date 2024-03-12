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
      - :class:`str` or :class:`int`
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
      - ``pywearable.constants._ISODATE_COL``
      - :class:`datetime.datetime`
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

If one of the sleep metrics is not available for a given loader, the column must
still be present in the returned :class:`pandas.DataFrame` but empty (i.e., 
`NaN`) values must be set on the rows.

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