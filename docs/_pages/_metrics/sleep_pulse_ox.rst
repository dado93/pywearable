sleep pulse ox
==============
The sleep pulse ox metric contains pulse oximetry data 
collected only during sleep periods and expressed in %. 
The required fields for this metric are the following ones:

.. list-table:: Sleep pulse ox fields
    :header-rows: 1
    
    * - Name
      - Description
      - Constant
      - Data type
    * - timezoneOffsetInMs
      - Timezone offset in milliseconds of the sleep stage start time
      - ``pywearable.constants._TIMEZONEOFFSET_IN_MS_COL``
      - :class:`int`
    * - calendarDate
      - Calendar date of the night sleep. Date format is 'yyyy-mm-dd'
      - ``pywearable.constants._CALENDAR_DATE_COL``
      - :class:`datetime.date`
    * - unixTimestampInMs
      - Unix timestamp in milliseconds of the sleep stage start time
      - ``pywearable.constants._UNIXTIMESTAMP_IN_MS_COL``
      - :class:`int`
    * - isoDate
      - Sleep start time in `ISO <https://en.wikipedia.org/wiki/ISO_8601>`_ format
      - ``pywearable.constants._ISODATE_COL``
      - :class:`datetime.datetime`
    * - spo2
      - Oxygen saturation value
      - ``pywearable.constants._SPO2_COL``
      - :class:`float`
