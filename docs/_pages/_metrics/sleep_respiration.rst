sleep-respiration
=================
The sleep respiration metric contains respiration data
collected only during sleep periods and expressed in 
breaths per minute. 
The required fields for this metric are the following ones:

.. list-table:: Sleep respiration metric fields.
    :header-rows: 1
    
    * - Name
      - Description
      - Constant
      - Data type
    * - timezoneOffsetInMs
      - Timezone offset in milliseconds of the measurement
      - ``pywearable.constants._TIMEZONEOFFSET_IN_MS_COL``
      - :class:`int`
    * - unixTimestampInMs
      - Unix timestamp in milliseconds of the measurement
      - ``pywearable.constants._UNIXTIMESTAMP_IN_MS_COL``
      - :class:`int`
    * - isoDate
      - Measurement time in `ISO <https://en.wikipedia.org/wiki/ISO_8601>`_ format
      - ``pywearable.constants._ISODATE_COL``
      - :class:`pd.Timestamp`
    * - breathsPerMinute
      - Breaths per Minute value
      - ``pywearable.constants._BREATHS_PER_MINUTE_COL``
      - :class:`float`
    * - calendarDate
      - Calendar date to which the sleep refers to. Date format is 'yyyy-mm-dd'
      - ``pywearable.constants._CALENDAR_DATE_COL``
      - :class:`pd.Timestamp`


An example of sleep respiration data is shown in the table below.

.. list-table:: Example of sleep respiration data.
   :header-rows: 1

   * - timezoneOffsetInMs
     - unixTimestampInMs
     - isoDate
     - breathsPerMinute
   * - 3600000
     - 1703459580000
     - 2023-12-25T00:13:00.000+01:00
     - 13.7
   * - 3600000
     - 1703459640000
     - 2023-12-25T00:14:00.000+01:00
     - 13.29
   * - 3600000
     - 1703459700000
     - 2023-12-25T00:15:00.000+01:00
     - 13.98