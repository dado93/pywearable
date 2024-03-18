respiration
===========
The respiration metric contains respiration data
expressed in breaths per minute. 
The required fields for this metric are the following ones:

.. list-table:: Respiration metric fields.
    :header-rows: 1
    
    * - Name
      - Description
      - Constant
      - Data type
    * - timezoneOffsetInMs
      - Timezone offset in milliseconds
      - ``pywearable.constants._TIMEZONEOFFSET_IN_MS_COL``
      - :class:`int`
    * - unixTimestampInMs
      - Unix timestamp in milliseconds
      - ``pywearable.constants._UNIXTIMESTAMP_IN_MS_COL``
      - :class:`int`
    * - isoDate
      - Time in `ISO <https://en.wikipedia.org/wiki/ISO_8601>`_ format
      - ``pywearable.constants._ISODATE_COL``
      - :class:`pd.Timestamp`
    * - breathsPerMinute
      - Breaths per Minute value
      - ``pywearable.constants._BREATHS_PER_MINUTE_COL``
      - :class:`float`


An example of a respiration data is shown in the table below.

.. list-table:: Example of respiration data.
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