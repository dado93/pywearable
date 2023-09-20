import re

import pandas as pd

from . import constants, loader


def process_questionnaire(
    labfront_loader: loader.LabfrontLoader, questionnaire: str, verbose: bool = False
):
    questionnaire_df = pd.DataFrame()
    questionnaire_questions = labfront_loader.get_questionnaire_questions(
        labfront_loader, questionnaire
    )
    questions = [
        questionnaire_questions[k]["description"]
        for k in questionnaire_questions.keys()
    ]

    for participant in labfront_loader.get_full_ids():
        try:
            questionnaire_data = labfront_loader.load_questionnaire(
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
