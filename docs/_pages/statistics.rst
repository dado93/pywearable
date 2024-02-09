.. include:: macros.rst

Statistics
==========
The overall ``pywearable`` package aims at extracting statistics (i.e., features) from
wearable data in an harmonized way. Each processing module exposes functions that
extract statistics from a single or multiple data sources, using functions defined
by the loaders available in the sub-module ``pywearable.loader`` or defined externally,
but exposing the same loading functions defined in :class:`pywearable.loader.BaseLoader`
with the same signature.

Statistics Format
^^^^^^^^^^^^^^^^^
The output format of the statistics returned by ``pywearable`` depends on the 
parameter ``return_df`` that can be set to each function of the
type ``pywearable.[sub-module].get_xx()``. When the parameter ``return_df`` is 
set to ``True``, then a |dataframe| is returned. When it is set to ``False``,
a :class:`dict` is instead returned.

Dictionary
----------
Statistics can be provided in a standardized nested
:class:`dict` format if the parameter
``return_df`` of the statistics functions is set to
``False``. The first ``key`` of the nested dictionary
is always the identifier of the user. The second
``key`` instead is the ``calendarDate``, while the 
structure of the deepest level depends on the number of statistics
that are returned by the function. In case a single statistic
is returned, then the deepest level of the nested 
:class:`dict` will be composed of ``calendarDate``:``value`` pairs, with
each ``value`` corresponding to the statistic of interest.
Instead if multiple statistics are returned, then the deepest
level will be composed of ``statistic``:``value`` pairs, with each metric
having the name of the statistic to which the ``value`` refers to. 

As an example, the function :func:`pywearable.sleep.get_time_in_bed`: would 
return a :class:`dict` of the following type when called with ``return_df`` set to
``False``::

    >> loader = pywearable.loader.LabfrontLoader(path_to_labfront_data)
    >> pywearable.sleep.get_time_in_bed(loader, user_id="all", return_df=False)
    {
        'user_01': {datetime.date(2023, 5, 9): 449.0,
                    datetime.date(2023, 5, 10): 368.0,
                    datetime.date(2023, 5, 11): 454.0,
                    datetime.date(2023, 5, 12): 395.0,
                },
        'user_02': {datetime.date(2023, 5, 9): 465.0,
                    datetime.date(2023, 5, 10): 628.0,
                    datetime.date(2023, 5, 11): 525.0,
                    datetime.date(2023, 5, 12): 421.0,
                }
    }

When multiple statistics are returned, such as with the function
:func:`pywearable.sleep.get_sleep_statistics`: then the :class:`dict`
has the following structure::

    >> loader = pywearable.loader.LabfrontLoader(path_to_labfront_data)
    >> pywearable.sleep.get_sleep_statistics(loader, user_id="all", return_df=False)
    {
        "user_01": {
            datetime.date(2023, 6, 20): {
                '%N1': 63.51351351351351,
                '%N2': nan,
                '%N3': 18.01801801801802,
                '%NREM': 81.53153153153153,
                '%REM': 18.46846846846847,
                'AWAKE': 11.0,
                'CPD_duration': 1.1764911071240722,
                'CPD_midpoint': 2.8276045024405767,
                'Lat_N1': 0.0,
                'Lat_N2': nan,
                'Lat_N3': 45.0,
                'Lat_REM': 124.0,
                'N1': 282.0,
                'N2': nan,
                'N3': 80.0,
                'NREM': 362.0,
                'REM': 82.0,
                'SCORE': 86,
                'SE': 97.58241758241758,
                'SME': 97.58241758241758,
                'SOL': 0.0,
                'SPT': 455.0,
                'TIB': 455.0,
                'TST': 444.0,
                'UNMEASURABLE': 0.0,
                'WASO': 11.0,
                'countAwake': 1.0,
                'countN1': 9.0,
                'countN2': nan,
                'countN3': 6.0,
                'countREM': 3.0
            },
            datetime.date(2023, 6, 21): {
                '%N1': 56.116504854368934,
                '%N2': nan,
                '%N3': 24.271844660194176,
                '%NREM': 80.3883495145631,
                '%REM': 19.611650485436893,
                'AWAKE': 14.0,
                'CPD_duration': 1.569871112485467,
                'CPD_midpoint': 0.6795116710632063,
                'Lat_N1': 0.0,
                'Lat_N2': nan,
                'Lat_N3': 33.0,
                'Lat_REM': 142.0,
                'N1': 289.0,
                'N2': nan,
                'N3': 125.0,
                'NREM': 414.0,
                'REM': 101.0,
                'SCORE': 87,
                'SE': 97.35349716446125,
                'SME': 97.35349716446125,
                'SOL': 0.0,
                'SPT': 529.0,
                'TIB': 529.0,
                'TST': 515.0,
                'UNMEASURABLE': 0.0,
                'WASO': 14.0,
                'countAwake': 4.0,
                'countN1': 13.0,
                'countN2': nan,
                'countN3': 4.0,
                'countREM': 6.0}
            }
        }
    }

DataFrame
---------
Statistics can be provided in a standardized |dataframe| if the parameter
``return_df`` of the statistics functions is set to
``True``. It is possible to control the output format of the
returned |dataframe| by setting the parameter ``return_multi_index`` to
``True`` (default behavior) for a |dataframe| with a :class:`pandas.MultiIndex` index
containing both user and days information, and to ``False`` for a |dataframe| 
with a standard :class:`pandas.RangeIndex` index and user and days information
as columns.

MultiIndex DataFrame
~~~~~~~~~~~~~~~~~~~~
If the parameter ``return_multi_index`` is set to ``True``, then the 
returned |dataframe| has a :class:`pandas.MultiIndex` index. The first
level of the index reports the identifiers for the users, while the
second level of the index reports days information. An example
|dataframe| returned with this method is reported below::

    >> loader = pywearable.loader.LabfrontLoader(path_to_labfront_data)
    >> pywearable.respiration.get_respiration_statistics(loader, user_id="all", return_df=True)

                                 meanPulseOx  p10PulseOx  
    user            calendarDate
    user_01         2023-03-22            NaN         NaN
                    2023-03-23      96.730392        90.0
                    2023-03-24      96.936364        94.0
                    2023-03-25            NaN         NaN
    user_02         2023-06-17      91.773026        87.0
                    2023-06-18      91.507692        87.0
                    2023-06-19            NaN         NaN
                    2023-06-20      92.432671        88.0
                    2023-06-21      89.935606        84.0

RangeIndex DataFrame
~~~~~~~~~~~~~~~~~~~~
If the parameter ``return_multi_index`` is set to ``False``, then the 
returned |dataframe| has a :class:`pandas.RangeIndex` index. 
The information about users and calendar days is reported into
columns of the |dataframe|, ``pywearable.constants._USER_COL``
and ``pywearable.constants._CALENDAR_DATE_COL``.
An example
|dataframe| returned with this method is reported below::

    >> loader = pywearable.loader.LabfrontLoader(path_to_labfront_data)
    >> pywearable.respiration.get_respiration_statistics(loader, user_id="all", return_df=True)
                                 
    user        calendarDate    meanPulseOx     p10PulseOx  
    user_01     2023-03-22            NaN              NaN
    user_01     2023-03-23      96.730392             90.0
    user_01     2023-03-24      96.936364             94.0
    user_01     2023-03-25            NaN              NaN
    user_02     2023-06-17      91.773026             87.0
    user_02     2023-06-18      91.507692             87.0
    user_02     2023-06-19            NaN              NaN
    user_02     2023-06-20      92.432671             88.0
    user_02     2023-06-21      89.935606             84.0
