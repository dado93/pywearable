pulse ox
===========
The pulse ox metric contains pulse oximetry data
expressed in %. 
The required fields for this metric are the following ones:

.. list-table:: Pulse ox fields
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
    * - spo2
      - Oxygen saturation value
      - ``pywearable.constants._SPO2_COL``
      - :class:`float`
