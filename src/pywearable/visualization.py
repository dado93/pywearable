"""
This module contains all the functions related to the visualization of data
"""


import datetime
from pathlib import Path
from typing import Union

import hrvanalysis
import july
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter, MultipleLocator, PercentFormatter

import pywearable.activity as activity
import pywearable.cardiac as cardiac
import pywearable.constants
from .loader.base import BaseLoader
import pywearable.respiration as respiration
import pywearable.sleep as sleep
import pywearable.stress as stress
import pywearable.utils as utils

from .loader.base import BaseLoader

date_form = DateFormatter("%m-%d")


def get_steps_line_graph_and_stats(
    loader: BaseLoader,
    user_id: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    verbose: bool = False,
    save_to: Union[str, None] = None,
    show: bool = True,
    steps_line_label: str = "steps",
    goal_line_label: str = "daily goal",
    ylabel: str = "Steps",
    plot_title: Union[str, None] = "Daily steps",
    figsize: tuple = (10, 6),
    fontsize: int = 15,
) -> dict:
    """Generate line-plot of daily steps and goals.

    The function creates (and possibly saves) a graph of the activity of a selected ``user_id``
    for a time period between ``start_date`` and ``end_date``, showing his/her number of steps
    every day, his/her goal for that day and whether the goal was reached.
    Furthermore activity statistics are computed and returned.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader
    user_id : :class:`str`
        The id of the user of interest
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None.
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None.
    verbose : :class:`bool`, optional
        Whether to print out activity statistics, by default False
    save_to : :class:`str` or None, optional
        Path where to save the plot, by default None
    show : :class:`bool`, optional
        Whether to show the plot, by default True
    steps_line_label : :class:`str`, optional
        Label of the steps line plot, by default "steps"
    goal_line_label : :class:`str`, optional
        Label of the dashed goals line plot, by default "daily goal"
    ylabel : :class:`str`, optional
        Label of the y-axis, by default "Steps"
    plot_title : :class:`str` or None, optional
        Title of the plot, by default "Daily steps"
    figsize : :class:`tuple`, optional
        Size of the figure, by default (10,6)
    fontsize : :class:`int`, optional
        Font size of the graph, by default 15

    Returns
    -------
    :class:`dict`
        dictionary of daily activity statistics
        (Mean daily steps, Mean daily distance, Percentage goal completion)
    """
    user_id = loader.get_full_id(user_id)
    # get dates,steps,goals,compare steps to goal to get goal completion
    dates, steps = zip(
        *activity.get_daily_steps(loader, user_id, start_date, end_date)[
            user_id
        ].items()
    )
    goals = list(
        activity.get_daily_steps_goal(loader, user_id, start_date, end_date)[
            user_id
        ].values()
    )
    col = np.where(np.array(steps) > np.array(goals), "g", "r")
    # get stats from the series
    mean_steps = activity.get_daily_steps(
        loader, user_id, start_date, end_date, average=True
    )[user_id]
    mean_distance = activity.get_daily_distance(
        loader, user_id, start_date, end_date, average=True
    )[user_id]
    goal_reached = np.sum(np.array(steps) > np.array(goals))
    number_of_days = len(dates)
    percentage_goal = round(goal_reached / number_of_days * 100, 1)
    stats_dict = {
        "Mean daily steps": mean_steps,
        "Mean daily distance": mean_distance,
        "Percentage goal completion": f"{goal_reached}/{number_of_days} {percentage_goal}%",
    }

    with plt.style.context("ggplot"):
        fig, ax = plt.subplots(figsize=figsize)
        ax.xaxis.set_major_formatter(date_form)
        ax.plot(dates, steps, label=steps_line_label, c="k")
        ax.plot(dates, goals, linestyle="--", c="g", label=goal_line_label)
        ax.scatter(dates, steps, c=col, s=100)
        plt.xticks(rotation=45, fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.legend(fontsize=fontsize - 1, loc="best")
        plt.grid("on")
        plt.ylim([max(min(steps) - 500, 0), max(steps) + 2000])
        plt.xlim(
            [
                min(dates) - datetime.timedelta(hours=6),
                max(dates) + datetime.timedelta(hours=6),
            ]
        )
        plt.ylabel(ylabel, fontsize=fontsize)
        if plot_title:
            plt.title(plot_title, fontsize=fontsize + 2)
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


def get_cardiac_line_graph_and_stats(
    loader: BaseLoader,
    user_id: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    verbose: bool = False,
    save_to: Union[str, None] = None,
    show: bool = True,
    resting_hr_label: str = "resting heart rate",
    maximum_hr_label: str = "maximum heart rate",
    ylabel: str = "Heart rate [beats/min]",
    title: Union[str, None] = None,
    figsize: tuple = (10, 6),
    fontsize: int = 15,
) -> dict:
    """Generate graph of cardiac activity

    This function generate (and possibly save) a graph of cardiac data of `user_id`
    for a period of interest between `start_date` and `end_date`.
    Cardiac statistics are computed and returned.

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str`
        The id of the user of interest
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    verbose : :class:`bool`, optional
        Whether to print out information about cardiac statistics, by default False
    save_to : :class:`str` or None, optional
        Path where to save the plot, by default None
    show : :class:`bool`, optional
        Whether to show the plot, by default True
    resting_hr_label : :class:`str`, optional
        Label for the resting HR line plot, by default "resting heart rate"
    maximum_hr_label : :class:`str`, optional
        Label for the maximum HR line plot, by default "maximum heart rate"
    ylabel : :class:`str`, optional
        Label for the y-axis, by default "Heart rate [beats/min]"
    title : :class:`str` or None, optional
        Title of the plot, by default None
    figsize : :class:`tuple`, optional
        Size of the figure, by default (10,6)
    fontsize : :class:`int`, optional
        Font size of the plot, by default 15

    Returns
    -------
    :class:`dict`
        dictionary of cardiac statistics for the period of interest
        (Average resting heart rate, Maximum heart rate overall)
    """
    user_id = loader.get_full_id(user_id)
    # get stats
    avg_resting_hr = round(
        cardiac.get_rest_heart_rate(
            loader, user_id, start_date, end_date, average=True
        )[user_id]["values"]
    )
    max_hr_recorded = np.nanmax(
        list(
            cardiac.get_max_heart_rate(
                loader, user_id, start_date, end_date, average=False
            )[user_id].values()
        )
    )
    stats_dict = {
        "Mean resting HR": avg_resting_hr,
        "Maximum HR overall": max_hr_recorded,
    }
    # get time series
    dates, rest_hr = zip(
        *cardiac.get_rest_heart_rate(loader, user_id, start_date, end_date)[
            user_id
        ].items()
    )
    # avg_hr = list(cardiac.get_avg_heart_rate(loader,start_date,end_date,user)[user].values())
    max_hr = list(
        cardiac.get_max_heart_rate(loader, user_id, start_date, end_date)[
            user_id
        ].values()
    )

    # plotting
    with plt.style.context("ggplot"):
        fig, ax = plt.subplots(figsize=figsize)
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
        ax.set_ylabel(ylabel, fontsize=fontsize + 1)
        plt.xticks(rotation=45, fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.legend(loc="upper right", fontsize=fontsize - 1)
        plt.grid("both")
        plt.ylim([min(30, min(rest_hr)), max(200, max_hr_recorded + 30)])
        if title:
            plt.title(title, fontsize=fontsize + 2)
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
    loader: BaseLoader,
    user_id: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    save_to: Union[str, None] = None,
    show: bool = True,
    zones_labels: list = ["Normal", "Low", "Concerning", "Critical"],
    zones_colors: list = ["g", "yellow", "orange", "tomato"],
    zones_alpha: float = 0.25,
    title: str = r"Rest SpO$_2$",
    ylabel: str = r"SpO$_2$",
    figsize: tuple = (14, 6),
    fontsize: int = 18,
):
    """Generate spO2 night graph

    This function creates (and possibly save if `save_to` = True),
    a graph showing all night data of SpO2 for `user_id`,
    in the period of interest starting from `start_date` and ending at `end_date`

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader.
    user_id : :class:`str`
        _The id of the user
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None], optional
        End date for data retrieval, by default None
    save_to : :class:`str` or None, optional
        Path where to save the plot, by default None
    show : :class:`bool`, optional
        Whether to show the plot, by default True
    zones_labels : :class:`list`, optional
        labels of the risk ranges, by default ["Normal", "Low", "Concerning", "Critical"]
    zones_colors : :class:`list`, optional
        Colors of the risk ranges, by default ["g", "yellow", "orange", "tomato"]
    zones_alpha : :class:`float`, optional
        Alphas for the risk ranges, by default 0.25
    title : :class:`str`, optional
        Title of the plot, by default r"Rest SpO$"
    ylabel : :class:`str`, optional
        Label of the y-axis, by default r"SpO$"
    figsize : :class:`tuple`, optional
        Size of the figure, by default (14, 6)
    fontsize : :class:`int`, optional
        Font size for the plot, by default 18
    """
    user_id = loader.get_full_id(user_id)

    timedelta = datetime.timedelta(
        hours=12
    )  # this assumes that at the last day a person wakes up before midday...
    spo2_df = loader.load_garmin_connect_pulse_ox(
        user_id, start_date, end_date + timedelta
    )
    sleep_spo2_df = spo2_df[spo2_df.sleep == 1].loc[:, ["isoDate", "spo2"]]
    unique_dates = pd.to_datetime(sleep_spo2_df.isoDate.dt.date.unique())
    # in order to avoid plotting lines between nights, we need to plot separately each sleep occurrence
    # unfortunately this takes some time (~6-7s/month), to find appropriate night for every row, maybe try to improve?
    sleep_spo2_df["date"] = sleep_spo2_df.isoDate.apply(
        lambda x: utils.find_nearest_timestamp(x, unique_dates)
    )

    fig, ax = plt.subplots(figsize=figsize)
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
    ax.set_ylabel(ylabel, fontsize=fontsize)
    ax.set_title(title, fontsize=fontsize + 2)

    ax.xaxis.grid(True, color="#CCCCCC")
    ax.xaxis.set_major_formatter(date_form)
    plt.xticks(rotation=60, fontsize=fontsize - 2)
    plt.yticks(fontsize=fontsize - 2)
    plt.ylim([min(50, min(sleep_spo2_df.spo2)), 100])
    plt.legend(loc="best", fontsize=fontsize - 2)
    plt.xlim([min_date, max_date])
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close()


def get_stress_grid_and_stats(
    loader: BaseLoader,
    user_id: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    verbose: bool = False,
    save_to: Union[str, None] = None,
    show: bool = True,
    title: str = "Average daily stress",
) -> dict:
    """Generate a github-like plot of daily stress scores

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader
    user_id : :class:`str`
        The id of the user
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    verbose : :class:`bool`, optional
        Whether to print out average daily stress score, by default False
    save_to : :class:`str` or None, optional
        Path where to save the plot, by default None
    show : :class:`bool`, optional
        Whether to show the plot, by default True
    title : :class:`str`, optional
        Title of the plot, by default "Average daily stress"

    Returns
    -------
    :class:`int`
        Average stress score for the period of interest
    """
    user_id = loader.get_full_id(user_id)

    # get stats
    dates, metrics = zip(
        *stress.get_daily_stress_statistics(loader, user_id, start_date, end_date)[
            user_id
        ].items()
    )
    daily_avg_stress, daily_max_stress = list(zip(*metrics))
    avg_stress = round(np.mean(daily_avg_stress))

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

    return avg_stress


def get_respiration_line_graph_and_stats(
    loader: BaseLoader,
    user_id: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    verbose: bool = False,
    save_to: Union[str, None] = None,
    show: bool = True,
    figsize: tuple = (10, 6),
    rest_line_label: str = "Sleep Avg",
    awake_line_label: str = "Awake Avg",
    title: Union[str, None] = None,
    xlabel: str = "Date",
    ylabel: str = "Breaths per minute",
    fontsize: int = 15,
) -> dict:
    """Generate a line-plot of daily and night average daily respiration rates

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader
    user_id : :class:`str`
        The id of the user
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    verbose : :class:`bool`, optional
        Whether to print out respiration stats, by default False
    save_to : class`str` or None, optional
        Path where to save the plot, by default None
    show : :class:`bool`, optional
        Whether to show the plot, by default True
    figsize: :class:`tuple`, optional
        Size of the figure, by default (10,6)
    rest_line_label : :class:`str`, optional
        Label of the line relative to night respiration data, by default "Sleep Avg"
    awake_line_label : :class:`str`, optional
        Label of the line relative to daily respiration data, by default "Awake Avg"
    title : :class:`str` or None, optional
        Title of the plot, by default None
    xlabel : :class:`str`, optional
        Label of the x-axis, by default "Date"
    ylabel : :class:`str`, optional
        Label of the y-axis, by default "Breaths per minute"
    fontsize : :class:`int`, optional
        Fontsize for the plot, by default 15

    Returns
    -------
    :class:`dict`
        Dictionary reporting average breaths per minute during the day and the night
    """
    user_id = loader.get_full_id(user_id)
    # get series, note that we're inclusive wrt the whole last day
    rest_dates, rest_resp = zip(
        *respiration.get_rest_breaths_per_minute(
            loader,
            user_id,
            start_date,
            end_date + datetime.timedelta(hours=23, minutes=59),
            remove_zero=True,
        )[user_id].items()
    )
    waking_dates, waking_resp = zip(
        *respiration.get_waking_breaths_per_minute(
            loader,
            user_id,
            start_date,
            end_date + datetime.timedelta(hours=23, minutes=59),
            remove_zero=True,
        )[user_id].items()
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
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(rest_dates, rest_resp, marker="o", label=rest_line_label)
        ax.plot(waking_dates, waking_resp, marker="o", label=awake_line_label)
        ax.legend(loc="best", fontsize=fontsize - 1)
        # ax.set_title(title,fontsize=15)
        ax.set_ylabel(ylabel, fontsize=fontsize)
        ax.set_xlabel(xlabel, fontsize=fontsize)
        plt.ylim(
            [min(8, min(rest_resp + waking_resp)), max(rest_resp + waking_resp) + 2.5]
        )
        plt.xticks(
            combined_dates[::2], dates_format[::2], rotation=45, fontsize=fontsize
        )
        plt.yticks(fontsize=fontsize)
        if save_to:
            plt.savefig(save_to, bbox_inches="tight")
        if title:
            plt.title(fontsize=fontsize + 2)
    if show:
        plt.show()
    else:
        plt.close()

    if verbose:
        print(f"Avg sleep: {avg_sleeping_breaths}")
        print(f"Avg awake: {avg_waking_breaths}")

    return stats_dict


def get_sleep_grid_and_stats(
    loader: BaseLoader,
    user_id: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    verbose: bool = False,
    save_to: Union[str, None] = None,
    show: bool = True,
    title: str = "Sleep performance",
) -> dict:
    """
    Generate a github-like grid plot of the sleep scores over that years for `user_id`

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader
    user_id : :class:`str`
        The id of the user
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    verbose : :class:`bool`, optional
        Whether to print out sleep stats, by default False
    save_to : :class:`str` or None, optional
        Path where to save the grid plot, by default None
    show : :class:`str`, optional
        _Whether to show the plot, by default True
    title : :class:`str`, optional
        Title of the plot, by default "Sleep performance"

    Returns
    -------
    :class:`dict`
        Dictionary of sleep stats (averages of sleep stages durations, awakenings, and sleep score)
    """
    user_id = loader.get_full_id(user_id)

    # We need to create a dataframe with dates going from one year before to the latest datetime
    dates, scores = zip(
        *sleep.get_sleep_score(loader, user_id, start_date, end_date)[user_id].items()
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
    avg_deep = sleep.get_n3_duration(
        loader, user_id, start_date, end_date, average=True
    )[user_id]["N3"]
    avg_light = sleep.get_n1_duration(
        loader, user_id, start_date, end_date, average=True
    )[user_id]["N1"]
    avg_rem = sleep.get_rem_duration(
        loader, user_id, start_date, end_date, average=True
    )[user_id]["REM"]
    avg_awake = sleep.get_awake_duration(
        loader, user_id, start_date, end_date, average=True
    )[user_id]["AWAKE"]
    avg_awakenings = sleep.get_awakenings(
        loader, user_id, start_date, end_date, average=True
    )[user_id]["AWAKENINGS"]
    avg_score = sleep.get_sleep_score(
        loader, user_id, start_date, end_date, average=True
    )[user_id]["SCORE"]

    stats_dict = {
        "Average light sleep": f"{avg_light}",
        "Average deep sleep": f"{avg_deep}",
        "Average REM sleep": f"{avg_rem}",
        "Average awake time": f"{avg_awake}",
        "Average awakenings": round(avg_awakenings, 1),
        "Average sleep score": round(avg_score),
    }

    if verbose:
        for k, v in stats_dict.items():
            print(f"{k} : {v}")

    return stats_dict


def get_sleep_summary_graph(
    loader: BaseLoader,
    user_id: str,
    start_date: Union[datetime.datetime, datetime.date, str, None] = None,
    end_date: Union[datetime.datetime, datetime.date, str, None] = None,
    save_to: str = None,
    show: bool = True,
    alpha: float = 0.25,
    title: str = "Sleep stages and score",
    xlabel: str = "Sleep time [hours]",
    ylabel: str = "Date",
    legend_title: str = "Sleep stages",
    legend_labels: str = ["Deep", "Light", "REM", "Awake"],
    colorbar_title: str = "Sleep Score",
    colorbar_labels: str = ["poor", "fair", "good", "excellent"],
    figsize: tuple = (15, 30),
    bottom_offset: int = 500,
    vertical_offset: float = -0.0,
    sleep_metric: Union[str, None] = None,
    chronotype_sleep_start: Union[str, None] = None,
    chronotype_sleep_end: Union[str, None] = None,
    show_chronotype: bool = False,
):
    """
    Generates a graph of all hypnograms of main sleeps of `user_id` for the period of interest

    Parameters
    ----------
    loader : :class:`pylabfront.loader.LabfrontLoader`
        An instance of a data loader
    user_id : :class:`str`
        The id of the user
    start_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        Start date for data retrieval, by default None
    end_date : :class:`datetime.datetime` or :class:`datetime.date` or :class:`str` or None, optional
        End date for data retrieval, by default None
    save_to : :class:`str`, optional
        Path where to save the plot, by default None
    show : class:`bool`, optional
        Whether to show the plot, by default True
    alpha : :class`float`, optional
        Alpha for elements in transparency in the plot, by default 0.25
    title : :class:`str`, optional
        Title of the plot, by default "Sleep stages and score"
    xlabel : :class:`str`, optional
        label of the x-axis, by default "Sleep time [hours]"
    ylabel : :class:`str`, optional
        label of the y-axis, by default "Date"
    legend_title : :class:`str`, optional
        title of the sleep stages legend, by default "Sleep stages"
    legend_labels : :class:`str`, optional
        labels for the sleep stages legend, by default ["Deep", "Light", "REM", "Awake"]
    colorbar_title : :class:`str`, optional
        title of the colorbar, by default "Sleep Score"
    colorbar_labels : :class:`str`, optional
        labels of the colorbar, by default ["poor", "fair", "good", "excellent"]
    figsize : :class:`tuple`, optional
        size of the figure, by default (15,30)
    bottom_offset : :class:`int`, optional
        distance of the scores from the bottom of the hypnograms, by default 500
    vertical_offset : :class:`float`, optional
        vertical offset of the scores at the bottom of the hypnograms, by default -0.
    sleep_metric : :class:`str` or None, optional
        metric used for circadian variability ("midpoint" or "duration"), by default None
    chronotype_sleep_start : :class:`str` or None, optional
        usual sleeping time for `user_id` in format HH:MM, by default None
    chronotype_sleep_end : :class:`str` or None, optional
        usual waking time for `user_id` in format HH:MM, by default None
    show_chronotype : :class:`bool`, optional
        whether to show chronotype dashed vertical lines over the hypnograms, by default False
    """

    if sleep_metric is not None:
        assertion_msg = "Must specify chronotype when plotting circadian measures"
        assert (
            chronotype_sleep_start is not None and chronotype_sleep_end is not None
        ), assertion_msg

    user_id = loader.get_full_id(user_id)

    # Define parameters for plotting
    ALPHA = alpha
    POSITION = 1.3

    # Get sleep summaries so that it is easier to get info
    sleep_summaries = loader.load_garmin_connect_sleep_summary(
        user_id, start_date, end_date
    )
    if len(sleep_summaries) == 0:
        return
    sleep_min_time = datetime.time(15, 0)
    # Check for start and end dates and convert them appropriately
    start_date = utils.check_date(start_date)
    end_date = utils.check_date(end_date)

    sleep_summaries["isoDate-Min"] = pd.to_datetime(
        sleep_summaries["calendarDate"].apply(
            lambda x: datetime.datetime.combine(
                x - datetime.timedelta(days=1), sleep_min_time
            )
        )
    )

    sleep_summaries["endIsoDate"] = pd.to_datetime(
        (
            sleep_summaries[pywearable.constants._UNIXTIMESTAMP_IN_MS_COL]
            + sleep_summaries[
                pywearable.constants._GARMIN_CONNECT_TIMEZONEOFFSET_IN_MS_COL
            ]
            + sleep_summaries[pywearable.constants._SLEEP_SUMMARY_DURATION_IN_MS_COL]
            + sleep_summaries[
                pywearable.constants._SLEEP_SUMMARY_AWAKE_DURATION_IN_MS_COL
            ]
        ),
        unit="ms",
        utc=True,
    ).dt.tz_localize(None)

    sleep_summaries["secondsDiff"] = (
        sleep_summaries["isoDate"] - sleep_summaries["isoDate-Min"]
    ).dt.total_seconds()

    sleep_summaries["endSecondsDiff"] = (
        sleep_summaries["endIsoDate"] - sleep_summaries["isoDate-Min"]
    ).dt.total_seconds()

    time_period = pd.date_range(
        start_date + datetime.timedelta(days=1),
        periods=(end_date - start_date).days,
        freq="D",
    )

    time_period = pd.Series(time_period).dt.date

    # define color-coding based on garmin connect visuals
    color_dict = {
        1: "royalblue",
        3: "darkblue",
        4: "darkmagenta",
        0: "hotpink",
        -1: "gray",
    }

    # get relevant scores
    scores_series = sleep.get_sleep_score(
        loader=loader, start_date=start_date, end_date=end_date, user_id=user_id
    )[user_id]
    # get maximum amount of time spent in bed to know x-axis limit
    max_bed_time = np.max(
        list(
            sleep.get_time_in_bed(
                loader=loader, start_date=start_date, end_date=end_date, user_id=user_id
            )[user_id].values()
        )
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

    hypnograms = loader.load_hypnogram(user_id, start_date, end_date, resolution=1)
    if sleep_metric is None:
        fig, ax = plt.subplots(figsize=figsize)
    elif sleep_metric == "midpoint" or sleep_metric == "duration":
        fig, (ax, ax2) = plt.subplots(
            1, 2, gridspec_kw={"width_ratios": [8, 2]}, figsize=figsize
        )
    elif sleep_metric == "both":
        fig, (ax, ax2, ax3) = plt.subplots(
            1, 3, gridspec_kw={"width_ratios": [8, 1, 1]}, figsize=figsize
        )
    else:
        raise KeyError("sleep metric specified for variability isn't valid.")

    # for every day in the period of interest, we plot the hypnogram
    for j, night in enumerate(time_period):
        try:  # this takes care of days where data is missing, skipping days through the plot y-axis
            # get the hypnogram
            hypnogram = hypnograms[night]
            # create dataframe for hypnogram
            hypnogram = pd.DataFrame(
                {
                    "stage": hypnogram["values"],
                    "isoDate": [
                        hypnogram["start_time"] + i * datetime.timedelta(minutes=1)
                        for i in range(
                            int(
                                (
                                    hypnogram["end_time"] - hypnogram["start_time"]
                                ).total_seconds()
                                / 60
                            )
                        )
                    ],
                }
            )
            # determine when there're stage variations
            hypnogram["stages_diff"] = (
                np.concatenate(
                    [
                        [0],
                        hypnogram.iloc[1:, :]["stage"].values
                        - hypnogram.iloc[:-1, :]["stage"].values,
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
                )
            stages_duration.append(0)  # the last row is not starting a new stage
            relevant_rows["stage duration"] = stages_duration
            # get array of the heights for the sections of the stacked barplot
            stage_duration_array = relevant_rows["stage duration"].values
            colors = [color_dict[stage] for stage in relevant_rows.stage.values]

            # keep track on the position where to begin the bar section
            sleep_summary_row = sleep_summaries[
                (sleep_summaries["calendarDate"] == night)
            ]
            seconds_diff = sleep_summary_row["secondsDiff"]

            bottom = seconds_diff

            # look through the stages
            for i in range(len(stage_duration_array)):
                # only Deep and REM sleep get full alpha, light, awake, and unmeasurable are in transparence
                appropriate_alpha = (
                    ALPHA
                    if (
                        colors[i] == "royalblue"
                        or colors[i] == "hotpink"
                        or colors[i] == "gray"
                    )
                    else 1
                )
                ax.barh(
                    j * POSITION,
                    stage_duration_array[i],
                    left=bottom,
                    color=colors[i],
                    alpha=appropriate_alpha,
                )
                # Update the bottom coordinates for the next section
                bottom += stage_duration_array[i]

            # annotate on top of the daily bar with the daily sleep score, color-coded appropriately
            score = scores_series.get(night)
            appropriate_color = get_color(score)
            # not sure why but with horizontal bars the annotation has to be manually adjusted in position
            ax.annotate(
                str(score),
                xy=(bottom + bottom_offset, j * POSITION + vertical_offset),
                color=appropriate_color,
                fontsize=15,
            )
        except Exception as e:  # skip missing dates
            continue

    # Set limits to be an hour lower than lowest difference
    # and one hour more than longest and latest sleep
    ax.set_xlim(
        [
            sleep_summaries["secondsDiff"].min() - 3600,
            sleep_summaries["endSecondsDiff"].max() + 3600,
        ]
    )

    # graph and legend params
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#DDDDDD")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(bottom=False, left=False)

    def format_func(x, pos):
        hours = sleep_min_time.hour + int(x // 3600)
        if hours >= 24:
            hours -= 24
        minutes = int((x % 3600) // 60)

        return "{:02d}".format(hours)

    formatter = FuncFormatter(format_func)

    ax.xaxis.set_major_formatter(formatter)
    # this locates y-ticks at the hours
    ax.xaxis.set_major_locator(MultipleLocator(base=3600))

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
    ax.set_ylim([-POSITION, (len(time_period)) * POSITION])
    ax.invert_yaxis()

    ## Legend
    alphas = [1, ALPHA, 1, ALPHA]
    colors = ["darkblue", "royalblue", "darkmagenta", "hotpink"]
    lgd = fig.legend(
        labels=legend_labels,
        loc="upper center",
        bbox_to_anchor=(0.97, 0.45),
        fontsize=14,
    )
    # take care of opacity of of the colors selected
    for i, lh in enumerate(lgd.legendHandles):
        lh.set_color(colors[i])
        lh.set_alpha(alphas[i])
    lgd.get_frame().set_alpha(0.0)
    lgd.set_title(legend_title, prop={"size": 15})

    # habitual sleep times lines
    if show_chronotype:
        sleep_time_hour = int(chronotype_sleep_start.split(":")[0])
        sleep_time_mins = int(chronotype_sleep_start.split(":")[1])
        wake_time_hour = int(chronotype_sleep_end.split(":")[0])
        wake_time_mins = int(chronotype_sleep_end.split(":")[1])
        # this conversion takes into consideration the min_sleep_time = 15
        # and the change of day (assuming wake is before 12)
        converted_sleep_time = (
            sleep_time_hour + 24 * (0 <= sleep_time_hour <= 12) - 15
        ) * 60 * 60 + sleep_time_mins * 60
        converted_wake_time = (
            wake_time_hour + 24 * (0 <= wake_time_hour <= 12) - 15
        ) * 60 * 60 + wake_time_mins * 60
        ax.axvline(converted_sleep_time, linestyle="--", zorder=10)
        ax.axvline(converted_wake_time, linestyle="--", zorder=11)

    # CONSISTENCY SUBPLOTS
    if sleep_metric is not None:
        # determine which metrics are needed in the subplot(s)
        metrics = [sleep_metric] if sleep_metric != "both" else ["duration", "midpoint"]
        axes = [ax2] if sleep_metric != "both" else [ax2, ax3]

        # and populate a subplot which each one
        for k in range(len(metrics)):
            current_ax = axes[k]
            sleep_metric = metrics[k]
            # we get data for cpd antecedent to the period of interest so that we may have a NR already set in some cases
            cpd_dict = sleep.get_cpd(
                loader,
                user_id,
                start_date - datetime.timedelta(days=30),
                end_date,
                days_to_consider=1000,
                average=False,
                sleep_metric=sleep_metric,
                chronotype_sleep_start=chronotype_sleep_start,
                chronotype_sleep_end=chronotype_sleep_end,
            )
            cpd_trend = utils.trend_analysis(
                cpd_dict, start_date - datetime.timedelta(days=30), end_date
            )
            # filter out to keep appropriate period
            cpd_trend = cpd_trend[cpd_trend.index.isin(time_period)]

            dates = cpd_trend.index
            # need to fillna to avoid skipping plotting some days at the start and end of the period
            metric = cpd_trend.metric.fillna(0)
            baseline = cpd_trend.BASELINE
            LB = cpd_trend.NR_LOWER_BOUND
            LB[LB < 0] = 0  # can't have a negative lower bound
            UB = cpd_trend.NR_UPPER_BOUND

            current_ax.barh(dates, metric, color="gray", alpha=0.7)
            current_ax.plot(baseline, dates, linestyle="-", linewidth=1, color="red")
            current_ax.fill_betweenx(dates, LB, UB, alpha=0.25, color="green")
            current_ax.grid("on")
            current_ax.set_title(f"CPD ({sleep_metric})", fontsize=10)
            current_ax.set_yticks([])

            # subplot params
            current_ax.set_axisbelow(True)
            current_ax.xaxis.grid(True, color="#EEEEEE")
            current_ax.yaxis.grid(False)
            current_ax.spines["top"].set_visible(False)
            current_ax.spines["right"].set_visible(False)
            current_ax.spines["left"].set_color("#DDDDDD")
            # as before invert to keep earlier dates in the upper part of the plot
            current_ax.set_ylim(
                [
                    time_period.iloc[0] - datetime.timedelta(days=1),
                    time_period.iloc[-1] + datetime.timedelta(days=1),
                ]
            )
            current_ax.invert_yaxis()

    # COLORBAR
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
    quest_df: pd.DataFrame,
    questionnaire_dict: dict,
    variable_of_interest: str,
    answer_of_interest: str,
    title: str = "",
    ylabel: str = "",
    answer_categories: Union[list, None] = None,
    save_to: Union[str, None] = None,
    show: bool = True,
):
    """Plots an errorbar graph with respect to the ``variable_of_interest`` for a specific question in a questionnaire

    For every category of answer given

    Parameters
    ----------
    quest_df : :class:`pandas.DataFrame`
        DataFrame obtained from the pylabfront.questionnaire.process_questionnaire function for the questionnaire of interest,
        filtered by user of interest, and possibly processed in some other way to obtain additional column(s) of interest,
        used as ``variable_of_interest``.
    questionnaire_dict : :class:`dict`
        Dictionary obtained from the pylabfront.loader.LabfrontLoader.get_questionnare_questions method for the questionnaire of interest
    variable_of_interest : :class:`str`
        name of the column of ``quest_df`` against which to calculate stats
    answer_of_interest : :class:`str`
        number of the answer in the questionaire in the format reported by Labfront
    title : :class:`str`, optional
        title of the plot. Defaults to empty string.
    ylabel : :class:`str`, optional
        label for the y-axis in the plot. Defaults to empty string.
    answer_categories : :class:`list`, optional
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


def plot_bbi_distribution(bbi: np.array, bin_length: int = 20):
    """
    Plots distribution of BBI data

    Parameters
    ----------
    bbi : :class:`numpy.ndarray`
        Array of Beat-to-beat intraval (BBI) data
    bin_length : :class:`int`, optional
        length of bins in the histogram, by default 20
    """

    hrvanalysis.plot.plot_distrib(np.array(bbi, dtype=np.int16), bin_length=bin_length)


def plot_comparison_radar_chart():
    pass  # TODO


def compare_against_group(
    user_data: Union[int, float],
    comparison_data: list,
    show: bool = True,
    save_to: Union[str, None] = None,
    bins: int = 10,
    title: str = "",
    ylabel: str = "% users",
    xlabel: str = "",
    fontsize: int = 16,
    shaded_regions: bool = False,
    regions_cutoffs: Union[list, None] = None,
    regions_colors: Union[list, None] = None,
    alpha: float = 0.25,
    xlim: Union[list, None] = None,
):
    """Plots a histogram of the distribution of a desired metric, specifying where an user stands within the distribution

    This functions compare an user against a chosen population with respect to a specific metric.
    The metric should be evaluated for both the user and the comparison group prior to the calling of the function.

    Parameters
    ----------
    user_data : :class:`float` or :class:`int`
        The value of the user of interest for the metric of interest
    comparison_data : :class:`list`
        List of values for the metric of interest for the comparison group (including the user of interest)
    show : :class:`bool`, optional
        Whether to show the plot, by default True
    save_to : :class:`str` or None, optional
        Path where to save the plot, by default None
    bins : :class:`int`, optional
        Number of bins for the comparison histogram, by default 10
    title : :class:`str`, optional
        Title of the plot, by default ""
    ylabel : :class:`str`, optional
        Label of the y-axis, by default "% users"
    xlabel : :class:`str`, optional
        Label of the x-axis, by default ""
    fontsize : :class:`int`, optional
        Font size for the plot, by default 16
    shaded_regions : :class:`bool`, optional
        Whether to enable in the plot the use of colored regions, by default False
    regions_cutoffs : :class:`list`, optional
        Values of the cuttoff points for the shaded regions, by default None
    regions_colors : :class:`list`, optional
        Colors of the shaded regions, len(regions_colors) is expected to be len(regions_cutoffs)-1, by default None
    alpha : :class:`float`, optional
        Alpha of the shaded regions, by default 0.25
    xlim : :class:`list`, optional
        List of the leftmost and rightmost x-values for the plot, by dafault None

    Returns
    -------
    :class:`float`
        Percentile standing of the user among the comparison group considered
    """

    # note that the following is not strict percentile
    # this is good to say you were above x% of the others..
    # should we instead show the strict percentile??
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
    df: pd.DataFrame,
    ax: Union[plt.axes, None] = None,
    save_to: Union[str, None] = None,
    show: bool = True,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    fontsize: int = 16,
    alpha: float = 0.3,
    xticks_frequency: int = 3,
    xticks_rotation: int = 45,
    figsize: tuple = (10, 6),
    show_legend: bool = False,
    normal_range: tuple = None,
):
    """Plots a trend analysis graph including short-term, mid-term, and long-term metrics

    Parameters
    ----------
    df : :class:`pandas.DataFrame`
        DataFrame of the processed metric data returned by the `pylabfront.utils.trend_analysis` function
    ax : None or class:`matplotlib.axes`, optional
        Axes where to build the figure, by default None
    save_to : :class:`str`, optional
        path where to save the plot, by default None
    show : :class:`bool`, optional
        whether to show the plot
    xlabel : :class:`str`, optional
        label of the x-axis, by default ""
    ylabel : :class:`str`, optional
        label of the y-axis, by default ""
    title : :class:`str`, optional
        title of the plot, by default ""
    fontsize : :class:`int`, optional
        fonti size for the plot, by default 16
    alpha : :class:`float`, optional
        Alpha of the shaded regions, by default 0.3
    xticks_frequency : :class:`int`, optional
        frequency of visualization of x-axis ticks, by default 3
    xticksrotaton : :class:`int`, optional
        rotation of ticks on the x-axis, by default 45
    figsize : :class:`tuple`, optional
        size of the figure, by default (10,6)
    show_legend : :class:`bool`, optional
        whether to show the legend of the plot, by default False
    normal_range : :class:`tuple`, optional
        start and end of a fixed range (based on norm values) instead of a trend NR, by default None
    """
    df = df.dropna(how="all")  # restrict viz to period with available data
    dates = df.index
    metric = df.metric
    baseline = df.BASELINE
    LB = df.NR_LOWER_BOUND
    UB = df.NR_UPPER_BOUND
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)
    ax.bar(dates, metric, label="Daily metric")
    ax.plot(baseline, linestyle="-", linewidth=3, color="red", label="Baseline")
    if normal_range is not None:
        assert type(normal_range) == tuple and len(normal_range) == 2
        ax.fill_between(
            dates,
            normal_range[0],
            normal_range[1],
            alpha=alpha,
            color="green",
            label="Normal range",
        )
    else:
        ax.fill_between(dates, LB, UB, alpha=alpha, color="green")
    ax.grid("on")
    ax.set_xticks(dates[::xticks_frequency])
    ax.tick_params(axis="x", labelrotation=xticks_rotation)
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)
    ax.set_title(title, fontsize=fontsize + 2)
    if show_legend:
        plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    if save_to:
        plt.savefig(save_to, bbox_inches="tight")
    if show:
        plt.show()
    return ax
