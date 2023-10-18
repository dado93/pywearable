import pandas as pd

from . import constants
from .loader.base import BaseLoader


def process_questionnaire(
    loader: BaseLoader, questionnaire: str, verbose: bool = False
) -> pd.DataFrame:
    """Process questionnaire to extract answers.

    This function process all the questionnaire answers
    from all users and report them in a structured format
    through a :class:`pd.DataFrame`.

    Example :class:`pd.DataFrame`::

        timezone,unixTimestampInMs,isoDate,userId,How are you?
        Europe/Rome,1683599224781,2023-05-09 04:27:04.781,User1_4a520aea-12d9-4513-8a0c-3055d399b097,Come al solito,Peggio del solito
        Europe/Budapest,1683698097137,2023-05-10 07:54:57.137,User1_4a520aea-12d9-4513-8a0c-3055d399b097,Peggio del solito,Come al solito
        Europe/Budapest,1683784544642,2023-05-11 07:55:44.642,User1_4a520aea-12d9-4513-8a0c-3055d399b097,Come al solito,Peggio del solito
        Europe/Berlin,1683870934322,2023-05-12 07:55:34.322,User1_a520aea-12d9-4513-8a0c-3055d399b097,Peggio del solito,

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a :class:`pylabfront.loader.LabfrontLoader`.
    questionnaire : str
        Unique identifier for the questionnaire to be analyzed.
    verbose : bool, optional
        If `True`, print out information on the terminal, by default False

    Returns
    -------
    pd.DataFrame
        A :class:`pd.DataFrame` with questions as columns, together with
        a `userId` column and standard columns for date and time
        information.
    """
    questionnaire_df = pd.DataFrame()
    questionnaire_questions = loader.get_questionnaire_questions(questionnaire)

    for participant in loader.get_full_ids():
        try:
            questionnaire_data = loader.load_questionnaire(
                participant, questionnaire_name=questionnaire
            )
        except KeyError:
            if verbose:
                print(
                    f"Could not load {questionnaire} from {participant} as the questionnaire is not available."
                )
            continue
        if len(questionnaire_data) > 0:
            questionnaire_data.loc[:, "userId"] = participant
            for question_key in questionnaire_questions.keys():
                if (
                    questionnaire_questions[question_key]["type"]
                    == constants._QUESTIONNAIRE_QUESTION_TYPE_RADIO_VALUE
                ):
                    options_dict = {
                        (k + 1): v
                        for k, v in enumerate(
                            questionnaire_questions[question_key]["options"]
                        )
                    }
                    questionnaire_data[question_key] = questionnaire_data[
                        question_key
                    ].map(options_dict)
                    questionnaire_data.loc[
                        :,
                        f'{question_key}-{questionnaire_questions[question_key]["description"]}',
                    ] = questionnaire_data[question_key]
                elif (
                    questionnaire_questions[question_key]["type"]
                    == constants._QUESTIONNAIRE_QUESTION_TYPE_TEXT_VALUE
                ):
                    questionnaire_data.loc[
                        :,
                        f'{question_key}-{questionnaire_questions[question_key]["description"]}',
                    ] = questionnaire_data[question_key]

                elif (
                    questionnaire_questions[question_key]["type"]
                    == constants._QUESTIONNAIRE_QUESTION_TYPE_MULTI_SELECT_VALUE
                ):
                    # We may have multiple options here, separated by a comma
                    # We create new columns based on question name - option name and set the values to default False
                    options_list = questionnaire_questions[question_key]["options"]
                    for option in range(len(options_list)):
                        questionnaire_data.loc[
                            :,
                            f'{question_key}-{questionnaire_questions[question_key]["description"]}-{options_list[int(option)]}',
                        ] = False
                    # If we have the option, then set the corresponding column value to True
                    for idx, row in questionnaire_data.iterrows():
                        for option in range(len(options_list)):
                            if isinstance(row[question_key], str):
                                if str(option + 1) in row[question_key]:
                                    questionnaire_data.loc[
                                        idx,
                                        f'{question_key}-{questionnaire_questions[question_key]["description"]}-{options_list[int(option)]}',
                                    ] = True
                            elif row[question_key] == option + 1:
                                questionnaire_data.loc[
                                    idx,
                                    f'{question_key}-{questionnaire_questions[question_key]["description"]}-{options_list[int(option)]}',
                                ] = True
                questionnaire_data = questionnaire_data.drop([question_key], axis=1)
            questionnaire_df = pd.concat(
                [questionnaire_df, questionnaire_data], ignore_index=True
            )
    return questionnaire_df
