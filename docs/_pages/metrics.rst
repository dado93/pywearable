.. include:: macros.rst

Metrics and Data Format
-----------------------

This page describes all the metrics that are available to be used in the `pywearable` package.
By metrics, we mean either a measurement (e.g., heart rate, oxygen saturation, ...) and processed measurements
(e.g., sleep summary, daily summary, ...). The class :class:`pywearable.loader.BaseLoader` defines
the loading functions that have to be implemented by the loaders and that support the metrics described
here below. All the metrics are then returned by the loading functions as |dataframe|.
The loading functions are then used in all the other sub-modules for analysis and visualization purposes.

For ease of use, we provide here below a table with the association between 
the metric names and the corresponding loading function defined in the
:class:`pywearable.loader.BaseLoader` and that must be implemented by loaders:

.. list-table:: Sleep pulse ox fields
    :header-rows: 1

    * - Metric
      - Loading function
    * - daily-summary
      - ``loader.load_daily_summary()``
    * - pulse-ox
      - ``loader.load_pulse_ox()``
    * - respiration
      - ``loader.load_respiration()``  
    * - sleep-pulse-ox
      - ``loader.load_sleep_pulse_ox()``
    * - sleep-respiration
      - ``loader.load_sleep_respiration()``
    * - sleep-stage
      - ``loader.load_sleep_stage()``
    * - sleep-summary
      - ``loader.load_sleep_summary()``


Metrics
=======

.. toctree::
    :maxdepth: 2

    _metrics/daily_heart_rate.rst
    _metrics/daily_summary.rst
    _metrics/pulse_ox.rst
    _metrics/respiration.rst
    _metrics/sleep_pulse_ox.rst
    _metrics/sleep_respiration.rst
    _metrics/sleep_stage.rst
    _metrics/sleep_summary.rst
    _metrics/steps.rst


questionnaire
=============

Questionnaires are commonly used in studies with wearable data, as they allow to
capture subjective and contextual information from uses. The aim of this metric
is to standardize the format of collected responses from questionnaires. The 
format is open to the following types of questions:

single choice
^^^^^^^^^^^^^
*How do you feel today?*

- Better than usual
- Usual
- Worse than usual

multiple choice
^^^^^^^^^^^^^^^

*Did you walk today?*

- Yes, in the morning
- Yes, in the afternoon
- Yes, in the evening
- No

free text
^^^^^^^^^

*Describe your symptoms*

.. list-table:: Questionnaire fields
    :header-rows: 1
    
    * - Name
      - Description
      - Constant
    * - timezoneOffsetInMs
      - Timezone offset in milliseconds of the time at which the questionnaire was filled in
      - ``pywearable.constants._TIMEZONEOFFSET_IN_MS_COL``
    * - unixTimestampInMs
      - Unix timestamp in milliseconds of the time at which the questionnaire was filled in
      - ``pywearable.constants._UNIXTIMESTAMP_IN_MS_COL``
    * - isoDate
      - Questionnaire fill in time in `ISO <https://en.wikipedia.org/wiki/ISO_8601>`_ format
      - ``pywearable.constants._ISODATE_COL``

The remaining columns have to be filled with the actual questionnaire questions. For 
single choice question, the name of the column is the question itself, and the content of the
column are the actual responses. In case of multiple choice question, the name of the column contains
both the question and one of the possible answers, and the column values are either ``True`` or ``False``
depending on whether that answer was checked or not. In case of free text, 

timezone,unixTimestampInMs,isoDate,Compared to your usual sleep, how would you rate tonight sleep?,
Europe/Rome,1683599224781,2023-05-09 04:27:04.781,As usual
Europe/Budapest,1683698097137,2023-05-10 07:54:57.137,Worse than usual
Europe/Budapest,1683784544642,2023-05-11 07:55:44.642,As usual
Europe/Berlin,1683870934322,2023-05-12 07:55:34.322,Worse than usual