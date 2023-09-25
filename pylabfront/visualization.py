import pylabfront.activity as activity
import pylabfront.utils as utils
import pylabfront.adherence as adherence
import pylabfront.sleep as sleep
import pylabfront.loader
import pylabfront.stress as stress
import pylabfront.respiration as respiration
import pylabfront.cardiac as cardiac

import datetime
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import july
import hrvanalysis

from pathlib import Path
from matplotlib.dates import DateFormatter
from matplotlib.ticker import PercentFormatter

date_form = DateFormatter("%m-%d")


def get_steps_graph_and_stats(
    loader,
    start_date,
    end_date,
    user,
    verbose=False,
    save_to=None,
    show=True,
    steps_line_label="steps",
    goal_line_label="daily goal",
    ylabel="Steps",
    plot_title="Daily steps",
):
    # get dates,steps,goals,compare steps to goal to get goal completion
    dates, steps = zip(
        *activity.get_steps_per_day(loader, start_date, end_date, user)[user].items()
    )
    goals = list(
        activity.get_steps_goal_per_day(loader, start_date, end_date, user)[
            user
        ].values()
    )
    col = np.where(np.array(steps) > np.array(goals), "g", "r")
    # get stats from the series
    mean_steps = activity.get_steps_per_day(
        loader, start_date, end_date, user, average=True
    )[user]
    mean_distance = activity.get_distance_per_day(
        loader, start_date, end_date, user, average=True
    )[user]
    goal_reached = np.sum(np.array(steps) > np.array(goals))
    number_of_days = len(dates)
    percentage_goal = round(goal_reached / number_of_days * 100, 1)
    stats_dict = {
        "Mean daily steps": mean_steps,
        "Mean daily distance": mean_distance,
        "Percentage goal completion": f"{goal_reached}/{number_of_days} {percentage_goal}%",
    }

    with plt.style.context("ggplot"):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.xaxis.set_major_formatter(date_form)
        ax.plot(dates, steps, label=steps_line_label, c="k")
        ax.plot(dates, goals, linestyle="--", c="g", label=goal_line_label)
        ax.scatter(dates, steps, c=col, s=100)
        plt.xticks(rotation=45, fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=14, loc="best")
        plt.grid("on")
        plt.ylim([max(min(steps) - 500, 0), max(steps) + 2000])
        plt.xlim(
            [
                min(dates) - datetime.timedelta(hours=6),
                max(dates) + datetime.timedelta(hours=6),
            ]
        )
        plt.ylabel(ylabel, fontsize=16)
        # plt.title(plot_title, fontsize=15)
        if save_to:
            plt.savefig(save_to, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()

    # print out stats
    if verbose:
        print(f"Mean daily steps: {mean_steps}")
        print(f"Mean daily distance travelled: {mean_distance}")
        print(f"Goal reached: {goal_reached}/{number_of_days} ({percentage_goal}%)")

    return stats_dict


def get_cardiac_graph_and_stats(
    loader,
    start_date,
    end_date,
    user,
    verbose=False,
    save_to=None,
    show=True,
    resting_hr_label="resting heart rate",
    maximum_hr_label="maximum heart rate",
    ylabel="Heart rate [beats/min]",
    title="Heart rate statistics over time",
):
    # get stats
    avg_resting_hr = round(
        cardiac.get_rest_heart_rate(loader, start_date, end_date, [user], True)[user][
            "values"
        ]
    )
    max_hr_recorded = np.nanmax(
        list(
            cardiac.get_max_heart_rate(loader, start_date, end_date, [user], False)[
                user
            ].values()
        )
    )
    stats_dict = {
        "Mean resting HR": avg_resting_hr,
        "Maximum HR overall": max_hr_recorded,
    }
    # get time series
    dates, rest_hr = zip(
        *cardiac.get_rest_heart_rate(loader, start_date, end_date, user)[user].items()
    )
    # avg_hr = list(cardiac.get_avg_heart_rate(loader,start_date,end_date,user)[user].values())
    max_hr = list(
        cardiac.get_max_heart_rate(loader, start_date, end_date, user)[user].values()
    )

    # plotting
    with plt.style.context("ggplot"):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.xaxis.set_major_formatter(date_form)
        ax.plot(
            dates,
            rest_hr,
            label=resting_hr_label,
            c="k",
            linewidth=1.5,
            marker="o",
            markersize=4,
        )
        # ax.plot(dates, avg_hr, label="average heart rate", c="g",linewidth=1.5,marker="o",markersize=4)
        ax.plot(
            dates,
            max_hr,
            label=maximum_hr_label,
            c="r",
            linewidth=1.5,
            marker="o",
            markersize=4,
        )
        # ax.set_title(title,fontsize=18)
        ax.set_ylabel(ylabel, fontsize=16)
        plt.xticks(rotation=45, fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(loc="upper right", fontsize=15)
        plt.grid("both")
        plt.ylim([min(30, min(rest_hr)), max(200, max_hr_recorded + 30)])
        if save_to:
            plt.savefig(save_to, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()

    if verbose:
        print(f"Resting HR: {avg_resting_hr}")
        print(f"Maximum HR: {max_hr_recorded}")

    return stats_dict


def get_rest_spo2_graph(
    loader,
    start_date,
    end_date,
    user,
    save_to=None,
    show=True,
    zones_labels=["Normal", "Low", "Concerning", "Critical"],
    zones_colors=["g", "yellow", "orange", "tomato"],
    zones_alpha=0.25,
    title=r"Rest SpO$_2$",
    ylabel=r"SpO$_2$",
):
    timedelta = datetime.timedelta(
        hours=12
    )  # this assumes that at the last day a person wakes up before midday...
    spo2_df = loader.load_garmin_connect_pulse_ox(
        user, start_date, end_date + timedelta
    )
    sleep_spo2_df = spo2_df[spo2_df.sleep == 1].loc[:, ["isoDate", "spo2"]]
    unique_dates = pd.to_datetime(sleep_spo2_df.isoDate.dt.date.unique())
    # in order to avoid plotting lines between nights, we need to plot separately each sleep occurrence
    # unfortunately this takes some time (~6-7s/month), to find appropriate night for every row, maybe try to improve?
    sleep_spo2_df["date"] = sleep_spo2_df.isoDate.apply(
        lambda x: utils.find_nearest_timestamp(x, unique_dates)
    )

    fig, ax = plt.subplots(figsize=(14, 6))
    # nights are plotted individually
    for date in unique_dates:
        relevant_data = sleep_spo2_df[sleep_spo2_df.date == date]
        ax.plot(relevant_data.isoDate, relevant_data.spo2, color="gray")

    # get extremes of x-axis
    min_date = sleep_spo2_df.isoDate.min() - timedelta
    max_date = sleep_spo2_df.isoDate.max() + timedelta

    # plot coloring by fill_between different y-ranges
    # normal zone
    ax.fill_between(
        [min_date, max_date],
        [90 for i in range(2)],
        [100 for i in range(2)],
        color=zones_colors[0],
        alpha=zones_alpha,
        label=zones_labels[0],
    )
    # low
    ax.fill_between(
        [min_date, max_date],
        [80 for i in range(2)],
        [90 for i in range(2)],
        color=zones_colors[1],
        alpha=zones_alpha,
        label=zones_labels[1],
    )
    # concerning
    ax.fill_between(
        [min_date, max_date],
        [70 for i in range(2)],
        [80 for i in range(2)],
        color=zones_colors[2],
        alpha=zones_alpha,
        label=zones_labels[2],
    )
    # critical
    ax.fill_between(
        [min_date, max_date],
        [0 for i in range(2)],
        [70 for i in range(2)],
        color=zones_colors[3],
        alpha=zones_alpha,
        label=zones_labels[3],
    )

    # graph params
    ax.set_ylabel(ylabel, fontsize=18)
    ax.set_title(title, fontsize=20)

    ax.xaxis.grid(True, color="#CCCCCC")
    ax.xaxis.set_major_formatter(date_form)
    plt.xticks(rotation=60, fontsize=16)
    plt.yticks(fontsize=16)
    plt.ylim([min(50, min(sleep_spo2_df.spo2)), 100])
    plt.legend(loc="best", fontsize=16)
    plt.xlim([min_date, max_date])
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def get_stress_graph_and_stats(
    loader,
    start_date,
    end_date,
    user,
    verbose=False,
    save_to=None,
    show=True,
    title="Average daily stress",
):
    # get stats
    dates, metrics = zip(
        *stress.get_daily_stress_statistics(loader, start_date, end_date, user)[
            user
        ].items()
    )
    daily_avg_stress, daily_max_stress = list(zip(*metrics))
    avg_stress = round(np.mean(daily_avg_stress))
    stats_dict = {"Average stress score": avg_stress}

    # Plot yearly stress
    # We need to create a DataFrame with dates going from one year before to the latest datetime
    # Get start and end days from calendar date
    start_date = dates[-1] - datetime.timedelta(days=364)
    # we want to make it inclusive wrt end_date
    end_date = dates[-1] + datetime.timedelta(days=1)
    intervals = int(divmod((end_date - start_date).total_seconds(), 60 * 60 * 24)[0])
    time_delta_intervals = [
        start_date + i * datetime.timedelta(days=1) for i in range(intervals)
    ]

    stress_reduced_df = pd.DataFrame({"date": dates, "stress": daily_avg_stress})

    stress_df = pd.DataFrame(
        {
            "date": time_delta_intervals,
        }
    )

    stress_df = pd.merge(left=stress_df, right=stress_reduced_df, on="date", how="left")

    stress_df.loc[stress_df.stress.isna(), "stress"] = 0

    july.heatmap(
        stress_df.date,
        stress_df.stress,
        cmap="golden",
        title=title,
        colorbar=True,
        month_grid=True,
    )

    if save_to:
        plt.savefig(save_to, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()

    if verbose:
        print(f"Average daily stress: {avg_stress}")

    return stats_dict


def get_respiration_graph_and_stats(
    loader,
    start_date,
    end_date,
    user,
    verbose=False,
    save_to=None,
    show=True,
    rest_line_label="Sleep Avg",
    awake_line_label="Awake Avg",
    title="Mean daily breaths per minute",
    xlabel="Date",
    ylabel="Breaths per minute",
):
    # get series, note that we're inclusive wrt the whole last day
    rest_dates, rest_resp = zip(
        *respiration.get_rest_breaths_per_minute(
            loader,
            start_date,
            end_date + datetime.timedelta(hours=23, minutes=59),
            user,
            remove_zero=True,
        )[user].items()
    )
    waking_dates, waking_resp = zip(
        *respiration.get_waking_breaths_per_minute(
            loader,
            start_date,
            end_date + datetime.timedelta(hours=23, minutes=59),
            user,
            remove_zero=True,
        )[user].items()
    )
    combined_dates = sorted(
        list(set(rest_dates + waking_dates))
    )  # not always we have waking/rest data, but need consistent x labeling
    # get stats
    avg_sleeping_breaths = round(np.mean(rest_resp), 2)
    avg_waking_breaths = round(np.mean(waking_resp), 2)
    stats_dict = {
        "Average sleep breaths": avg_sleeping_breaths,
        "Average waking breaths": avg_waking_breaths,
    }

    # plotting
    dates_format = [date.strftime("%d-%m") for date in combined_dates]
    with plt.style.context("ggplot"):
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(rest_dates, rest_resp, marker="o", label=rest_line_label)
        ax.plot(waking_dates, waking_resp, marker="o", label=awake_line_label)
        ax.legend(loc="best", fontsize=15)
        # ax.set_title(title,fontsize=15)
        ax.set_ylabel(ylabel, fontsize=15)
        ax.set_xlabel(xlabel, fontsize=16)
        plt.ylim(
            [min(8, min(rest_resp + waking_resp)), max(rest_resp + waking_resp) + 2.5]
        )
        plt.xticks(combined_dates[::2], dates_format[::2], rotation=45, fontsize=15)
        plt.yticks(fontsize=15)
        if save_to:
            plt.savefig(save_to, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()

    if verbose:
        print(f"Avg sleep: {avg_sleeping_breaths}")
        print(f"Avg awake: {avg_waking_breaths}")

    return stats_dict


def get_sleep_heatmap_and_stats(
    loader,
    start_date,
    end_date,
    user,
    verbose=False,
    save_to=None,
    show=True,
    title="Sleep performance",
):
    # We need to create a dataframe with dates going from one year before to the latest datetime
    dates, scores = zip(
        *sleep.get_sleep_score(loader, start_date, end_date, user)[user].items()
    )
    # Get start and end days from calendar date
    start_date = dates[-1] - datetime.timedelta(days=364)
    end_date = dates[-1] + datetime.timedelta(days=1)
    intervals = int(divmod((end_date - start_date).total_seconds(), 60 * 60 * 24)[0])
    time_delta_intervals = [
        start_date + i * datetime.timedelta(days=1) for i in range(intervals)
    ]

    sleep_reduced_df = pd.DataFrame({"date": dates, "sleep": scores})

    sleep_df = pd.DataFrame({"date": time_delta_intervals})

    sleep_df = pd.merge(left=sleep_df, right=sleep_reduced_df, on="date", how="left")
    sleep_df.loc[sleep_df.sleep.isna(), "sleep"] = 0

    july.heatmap(
        sleep_df.date,
        sleep_df.sleep,
        cmap="BuGn",
        title=title,
        colorbar=True,
        month_grid=True,
    )

    if save_to:
        plt.savefig(save_to, bbox_inches="tight")

    if show:
        plt.show()

    # stats
    avg_deep = sleep.get_deep_sleep_duration(
        loader, start_date, end_date, user, average=True
    )[user]["values"]
    avg_light = sleep.get_light_sleep_duration(
        loader, start_date, end_date, user, average=True
    )[user]["values"]
    avg_rem = sleep.get_rem_sleep_duration(
        loader, start_date, end_date, user, average=True
    )[user]["values"]
    avg_awake = sleep.get_awake_sleep_duration(
        loader, start_date, end_date, user, average=True
    )[user]["values"]
    avg_awakenings = sleep.get_awakenings(
        loader, start_date, end_date, user, average=True
    )[user]["value"]
    avg_score = sleep.get_sleep_score(loader, start_date, end_date, user, average=True)[
        user
    ]["values"]

    stats_dict = {
        "Average light sleep": f"{int((avg_light / (1000*60*60))% 24)} hr {int((avg_light / (1000*60))%60)}",
        "Average deep sleep": f"{int((avg_deep / (1000*60*60))% 24)} hr {int((avg_deep / (1000*60))% 60)}",
        "Average REM sleep": f"{int((avg_rem / (1000*60*60))% 24)} hr {int((avg_rem / (1000*60))% 60)}",
        "Average awake time": f"{int((avg_awake / (1000*60*60))% 24)} hr {int((avg_awake / (1000*60))% 60)}",
        "Average sleep disruptions": round(avg_awakenings, 1),
        "Average sleep score": round(avg_score),
    }

    if verbose:
        for k, v in stats_dict.items():
            print(f"{k} : {v}")

    return stats_dict


def get_sleep_summary_graph(
    loader,
    start_date,
    end_date,
    user,
    save_to=None,
    show=True,
    alpha=0.25,
    title="Sleep stages and score",
    xlabel="Sleep time [hours]",
    ylabel="Date",
    legend_title="Sleep stages",
    legend_labels=["Deep", "Light", "REM", "Awake"],
    colorbar_title="Sleep Score",
    colorbar_labels=["poor", "fair", "good", "excellent"],
    figsize=(15,30)
):
    # define params for graph
    ALPHA = alpha
    POSITION = 1.3

    time_period = pd.date_range(
        start_date + datetime.timedelta(days=1),
        periods=(end_date - start_date).days,
        freq="D",
    )

    time_period = pd.Series(time_period).dt.date

    # define color-coding based on garmin connect visuals
    color_dict = {1: "royalblue", 3: "darkblue", 4: "darkmagenta", 0: "hotpink"}

    # get relevant scores
    scores_series = sleep.get_sleep_score(loader, start_date, end_date, user)[user]
    # get maximum amount of time spent in bed to know x-axis limit
    max_bed_time = (
        np.max(
            [
                tst
                for tst in sleep.get_time_in_bed(loader, start_date, end_date, user)[
                    user
                ].values()
                if tst is not None
            ]
        )
        / 60
    )

    # setup an internal fn to get appropriate sleep score colors:
    def get_color(score):
        # if it's null/nan hide it out, this happens for manual input by the user
        if score == "" or np.isnan(score):
            return "white"
        else:
            if score >= 90:
                return "forestgreen"
            elif score >= 80:
                return "limegreen"
            elif score >= 60:
                return "darkorange"
            else:
                return "firebrick"

    fig, ax = plt.subplots(figsize=figsize)

    # for every day in the period of interest, we plot the hypnogram
    for j, night in enumerate(time_period):
        try:  # this takes care of days where data is missing, skipping days through the plot y-axis
            # get the hypnogram
            hypnogram = loader.load_hypnogram(user, night)
            # determine when there're stage variations
            hypnogram["stages_diff"] = (
                np.concatenate(
                    [
                        [0],
                        hypnogram.iloc[1:, :].stage.values
                        - hypnogram.iloc[:-1, :].stage.values,
                    ]
                )
                != 0
            )
            # get rows relative to initial/final timestamp of sleep or to variations in stage
            relevant_rows = hypnogram.loc[
                np.logical_or(
                    hypnogram.index.isin([0, len(hypnogram) - 1]), hypnogram.stages_diff
                ),
                ["isoDate", "stage"],
            ]
            # create a row that indicate the duration of permanence in the stages
            # (in hours, they will be the height of the sections of the stacked barplot)
            stages_duration = []
            for i in range(len(relevant_rows) - 1):
                stages_duration.append(
                    (
                        pd.to_datetime(relevant_rows.iloc[i + 1].isoDate)
                        - pd.to_datetime(relevant_rows.iloc[i].isoDate)
                    ).seconds
                    / (60 * 60)
                )
            stages_duration.append(0)  # the last row is not starting a new stage
            relevant_rows["stage duration"] = stages_duration
            # get array of the heights for the sections of the stacked barplot
            array = relevant_rows["stage duration"].values
            colors = [color_dict[stage] for stage in relevant_rows.stage.values]
            # keep track on the position where to begin the bar section
            bottom = 0
            # look through the stages
            for i in range(len(array)):
                # only Deep and REM sleep get full alpha, light and awake are in transparence
                appropriate_alpha = (
                    ALPHA if (colors[i] == "royalblue" or colors[i] == "hotpink") else 1
                )
                ax.barh(
                    j * POSITION,
                    array[i],
                    left=bottom,
                    color=colors[i],
                    alpha=appropriate_alpha,
                )
                # Update the bottom coordinates for the next section
                bottom += array[i]
            # annotate on top of the daily bar with the daily sleep score, color-coded appropriately
            score = scores_series.get(night)
            appropriate_color = get_color(score)
            # not sure why but with horizontal bars the annotation has to be manually adjusted in position
            plt.annotate(
                str(score),
                xy=(bottom + 0.05, j * POSITION + 0.2),
                color=appropriate_color,
                fontsize=15,
            )
        except:  # skip missing dates
            continue

    ax.set_xlim([0, max(10, max_bed_time + 0.5)])

    # graph and legend params
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#DDDDDD")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(bottom=False, left=False)
    # this is a tall graph, show also x-axis above?
    # ax_t = ax.secondary_xaxis('top')
    # ax_t.spines["top"].set_visible(False)
    # ax_t.tick_params(top=False)

    # graph params
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color="#EEEEEE")
    ax.yaxis.grid(False)

    ax.set_ylabel(ylabel, labelpad=15, color="#333333", fontsize=16)
    ax.set_xlabel(xlabel, labelpad=15, color="#333333", fontsize=16)

    ax.set_yticks(
        [i * POSITION for i in range(len(time_period))],
        [date.strftime("%d/%m") for date in time_period],
        rotation=0,
        fontsize=14,
    )

    ax.set_title(title, pad=25, color="#333333", weight="bold", fontsize=20)

    # ordinarly the yaxis starts from below, but it's better to visualize earlier dates on top instead
    plt.gca().invert_yaxis()

    # legend
    alphas = [1, ALPHA, 1, ALPHA]
    colors = ["darkblue", "royalblue", "darkmagenta", "hotpink"]
    lgd = ax.legend(
        labels=legend_labels,
        loc="upper center",
        bbox_to_anchor=(1.1, 0.45),
        fontsize=14,
    )
    # take care of opacity of of the colors selected
    for i, lh in enumerate(lgd.legendHandles):
        lh.set_color(colors[i])
        lh.set_alpha(alphas[i])
    lgd.get_frame().set_alpha(0.0)
    lgd.set_title(legend_title, prop={"size": 15})

    # code for the colorbar

    bins = [40, 60, 80, 90, 100]
    midpoints = [(bins[i] + bins[i + 1]) / 2 for i in range(len(bins) - 1)]
    colors = ["firebrick", "darkorange", "limegreen", "forestgreen", "forestgreen"]

    cmap = mpl.colors.ListedColormap(colors)
    norm = mpl.colors.BoundaryNorm(bins, cmap.N)

    # Create an additional axis for the colorbar
    cax = fig.add_axes([0.935, 0.55, 0.03, 0.2])
    cbar = plt.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, ticks=midpoints, pad=0.10
    )
    cbar.ax.set_yticklabels(colorbar_labels, fontsize=14)

    plt.annotate(
        colorbar_title,
        xy=(1.2, 1.1),
        xycoords="axes fraction",
        ha="center",
        fontsize=14,
    )

    if save_to:
        plt.savefig(save_to, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def get_errorbar_graph(
    quest_df,
    questionnaire_dict,
    variable_of_interest,
    answer_of_interest,
    title="",
    ylabel="",
    answer_categories=None,
    save_to=None,
    show=True,
):
    """Plots an errorbar graph with respect to the ``variable_of_interest`` for a specific question in a questionnaire

    For every category of answer given
    Parameters
    ----------
    quest_df : pd.DataFrame
        DataFrame obtained from the pylabfront.loader.LabfrontLoader.process_questionnaire method for the questionnaire of interest,
        filtered by user of interest, and possibly processed in some other way to obtain additional column(s) of interest,
        used as ``variable_of_interest``.
    questionnaire_dict : dict
        Dictionary obtained from the pylabfront.loader.LabfrontLoader.get_questionnare_questions method for the questionnaire of interest
    variable_of_interest : string
        name of the column of ``quest_df`` against which to calculate stats
    answer_of_interest : string
        number of the answer in the questionaire in the format reported by Labfront
    title : string, optional
        title of the plot. Defaults to empty string.
    ylabel : string, optional
        label for the y-axis in the plot. Defaults to empty string.
    answer_categories : list, optional
        list of the answers, in the order desired for visaulization, by default None
        if this is left as default, the order is defined by the order proposed in the Labfront questionnaire
    """
    # if a specific order isn't explicitely given, get the order of the answers in the questionnaire
    if answer_categories is None:
        answer_categories = questionnaire_dict[answer_of_interest]["options"]
    # get the description and the string of the full answer id, useful to get the appropriate columns in the dataframe
    answer_descr = questionnaire_dict[answer_of_interest]["description"]
    answer_string = answer_of_interest + "-" + answer_descr

    # get only the relevant columns, drop the rows where there's incomplete data
    tmp_df = quest_df.loc[:, [answer_string, variable_of_interest]].copy().dropna()
    # Get mean and std wrt the variable of interest for every answer level (if std is None (single obs), put it to 0)
    bar_df = (
        tmp_df.loc[:, [answer_string, variable_of_interest]]
        .dropna()
        .groupby(answer_string)
        .agg(Mean=(variable_of_interest, np.mean), Std=(variable_of_interest, np.std))
        .fillna(0)
    )
    # a bit of a hack, but we need the indexes in the right order for appropriate plotting
    bar_df = bar_df.reindex(answer_categories).dropna()
    # plot bars with height equal to the mean and error reference of std
    ax = bar_df.plot(kind="bar", y="Mean", legend=False, alpha=0.25, figsize=(12, 6))
    ax.errorbar(
        bar_df.index,
        bar_df["Mean"],
        yerr=bar_df["Std"],
        linewidth=1.5,
        color="black",
        alpha=0.75,
        capsize=10,
        marker="o",
    )
    # graph params
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#EEEEEE")
    ax.xaxis.grid(False)
    ax.set_ylabel(ylabel, labelpad=15, color="#333333", fontsize=15)
    ax.set_xlabel("")
    ax.set_title(title, pad=25, color="#333333", weight="bold", fontsize=20)
    # to avoid overlapping of xlabels, we add newlines every jumprow words
    # decide how often to insert a newline depending on the number of bars
    jumprow = 3 if len(bar_df) < 5 else 2
    labels = bar_df.index.unique().values
    new_labels = []
    for label in labels:
        label = label.split()
        new_label = []
        for i in range(len(label)):
            new_label.append(label[i])
            if (i + 1) % jumprow == 0:
                new_label.append("\n")
        new_labels.append(" ".join(new_label))
    plt.xticks(labels, new_labels, rotation=0, fontsize=15)
    plt.yticks(fontsize=15)

    if save_to:
        plt.savefig(save_to, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()


def plot_bbi_distribution(bbi, bin_length=20):
    """Plots distribution of bbi data

    Parameters
    ----------
    bbi : numpy.ndarray
        array of bbi data
    bin_length : int, optional
        length of bins in the histogram, by default 20
    """

    hrvanalysis.plot.plot_distrib(np.array(bbi, dtype=np.int16), bin_length=bin_length)


def plot_comparison_radar_chart():
    pass  # TODO


def compare_against_group(
    user_data,
    comparison_data,
    show=True,
    save_to=None,
    bins=10,
    title="",
    ylabel="% users",
    xlabel="",
    fontsize=16,
    shaded_regions=False,
    regions_cutoffs=None,
    regions_colors=None,
    alpha=0.25,
    xlim=None,
):
    """Plots a histogram of the distribution of a desired metric, specifying where an user stands within the distribution

    This functions compare an user against a chosen population with respect to a specific metric.
    The metric should be evaluated for both the user and the comparison group prior to the calling of the function.
    Parameters
    ----------
    user_data : float
        The value of the user of interest for the metric of interest
    comparison_data : list
        List of values for the metric of interest for the comparison group (including the user of interest)
    show : bool, optional
        Whether to show the plot
    save_to : str, optional
        the path where to save the plot, by default None
    bins : int, optional
        Number of bins for the comparison histogram, by default 10
    title : str, optional
        Title of the plot, by default ""
    ylabel : str, optional
        Y-label of the plot, by default "% users"
    xlabel : str, optional
        X-label of the plot, by default ""
    fontsize : int, optional
        Fontsize for the plot, by default 16
    shaded_regions : bool, optional
        Whether to enable in the plot the use of colored regions, by default False
    regions_cutoffs : list, optional
        Values of the cuttoff points for the shaded regions, by default None
    regions_colors : list, optional
        Colors of the shaded regions, len(regions_colors) is expected to be len(regions_cutoffs)-1, by default None
    alpha : float, optional
        Alpha of the shaded regions, by default 0.25
    xlim : list, optional
        List of two extreme x-values for the plot, by dafault None

    Returns
    -------
    float
        Percentile standing of the user among the comparison group considered
    """

    # note that the following is not strict percentile (this is good to say you were above x% of the others..)
    # should we instead show that??
    percentile_standing = np.round(
        np.sum(np.array(comparison_data) <= user_data) / len(comparison_data) * 100, 0
    )

    fig, ax = plt.subplots(figsize=(8, 4), facecolor="w")
    cnts, values, bars = ax.hist(
        comparison_data,
        bins=bins,
        rwidth=0.95,
        weights=np.ones(len(comparison_data)) / len(comparison_data),
        zorder=2,
    )

    plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

    if shaded_regions:
        for i in range(len(regions_colors)):
            start_point = regions_cutoffs[i]
            end_point = regions_cutoffs[i + 1]
            ax.axvspan(start_point, end_point, alpha=alpha, color=regions_colors[i])

    for i, (cnt, value, bar) in enumerate(zip(cnts, values, bars)):
        if i == len(cnts) or values[i] <= user_data <= values[i + 1]:
            bar.set_facecolor("darkorange")
            break
    ax.set_title(title, fontsize=fontsize + 2)
    ax.set_ylabel(ylabel, fontsize=fontsize)
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True)
    if xlim:
        ax.set_xlim(xlim)
    if save_to:
        plt.savefig(save_to, bbox_inches="tight")
    if show:
        plt.show()

    return percentile_standing


def plot_trend_analysis(
    df,
    save_to=None,
    xlabel="",
    ylabel="",
    title="",
    fontsize=16,
    alpha=0.3,
    xticks_frequency=3,
):
    """Plots a trend analysis graph, given data processed using `utils.trend_analysis`

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of the processed metric data returned by `utils.trend_analysis` function
    save_to : str, optional
        the path where to save the plot, by default None
    xlabel : str, optional
        X-label of the plot, by default ""
    ylabel : str, optional
        Y-label of the plot, by default ""
    title : str, optional
        title of the plot, by default ""
    fontsize : int, optional
        fontisize to be used for the labels and the title, by default 16
    alpha : float, optional
        Alpha of the shaded regions, by default 0.3
    xticks_frequency : int, optional
        frequency of visualization of x-axis ticks, by default 3
    """

    dates = df.index
    metric = df.metric
    baseline = df.BASELINE
    LB = df.NR_LOWER_BOUND
    UB = df.NR_UPPER_BOUND
    plt.figure(figsize=(10, 6))
    plt.bar(dates, metric)
    plt.plot(baseline, linestyle="-", linewidth=3, color="red")
    plt.fill_between(dates, LB, UB, alpha=alpha, color="green")
    plt.grid("on")
    plt.xticks(dates[::xticks_frequency], rotation=45)
    plt.xlabel(xlabel, fontsize=fontsize)
    plt.ylabel(ylabel, fontsize=fontsize)
    plt.title(title, fontsize=fontsize + 2)
    if save_to:
        plt.savefig(save_to, bbox_inches="tight")
    plt.show()
