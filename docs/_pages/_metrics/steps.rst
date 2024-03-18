.. include:: ../macros.rst
    
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