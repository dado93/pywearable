bbi
===

The BBI metric contains beat-to-beat intervals (BBI)
expressed in milliseconds. 
The required fields for this metric are the following ones:

.. list-table:: Heart rate fields
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
    * - bbi
      - Beat-to-Beat Intervals
      - ``pywearable.constants._BBI_COL``
      - :class:`float`
