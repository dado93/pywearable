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
import seaborn as sns
import july

from pathlib import Path
from matplotlib.dates import DateFormatter

date_form = DateFormatter("%m-%d")


def get_steps_graph_and_stats(loader,start_dt,end_dt,user,verbose=False):

    timedelta = datetime.timedelta(days=1)
    # get dates,steps,goals,compare steps to goal to get goal completion
    dates, steps = zip(*activity.get_steps_per_day(loader,start_dt,end_dt+timedelta,user)[user].items())
    goals = list(activity.get_steps_goal_per_day(loader,start_dt,end_dt+timedelta,user)[user].values())
    col = np.where(np.array(steps) > np.array(goals),"g","r")
    # get stats from the series
    mean_steps = activity.get_steps_per_day(loader,start_dt,end_dt,user,average=True)[user]
    mean_distance = activity.get_distance_per_day(loader,start_dt,end_dt,user,average=True)[user]
    goal_reached = np.sum(np.array(steps) > np.array(goals))
    number_of_days = len(dates)
    percentage_goal = round(goal_reached/number_of_days*100,1)
    stats_dict = {"Mean daily steps": mean_steps,
                  "Mean daily distance": mean_distance,
                  "Percentage goal completion": percentage_goal}


    with plt.style.context('ggplot'):
        fig,ax = plt.subplots(figsize=(10,6))
        ax.xaxis.set_major_formatter(date_form)
        ax.plot(dates, steps, label="steps", c="k")
        ax.plot(dates, goals, linestyle="--",c="g",label="daily goal")
        ax.scatter(dates, steps, c=col, s=100)
        plt.xticks(rotation=45,fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=14, loc="best")
        plt.grid("on")
        plt.ylim([max(min(steps)-500,0),max(steps)+2000])
        plt.xlim([min(dates)-datetime.timedelta(hours=6),max(dates)+datetime.timedelta(hours=6)])
        plt.ylabel("Steps",fontsize=16)
        #plt.title("Daily steps", fontsize=15)
        plt.show()

    # print out stats
    if verbose:
        print(f"Mean daily steps: {mean_steps}")
        print(f"Mean daily distance travelled: {mean_distance}")
        print(f"Goal reached: {goal_reached}/{number_of_days} ({percentage_goal}%)")
    
    return stats_dict


def get_cardiac_graph_and_stats(loader,start_dt,end_dt,user,verbose=False):

    # get stats
    avg_resting_hr = round(cardiac.get_rest_heart_rate(loader,start_dt,end_dt,[user],True)[user]["values"])
    max_hr_recorded = np.nanmax(list(cardiac.get_max_heart_rate(loader,start_dt,end_dt,[user],False)[user].values()))
    stats_dict = {"Mean resting HR": avg_resting_hr,
                  "Maximum HR overall": max_hr_recorded}
    # get time series
    dates, rest_hr = zip(*cardiac.get_rest_heart_rate(loader,start_dt,end_dt,user)[user].items())
    # avg_hr = list(cardiac.get_avg_heart_rate(loader,start_dt,end_dt,user)[user].values())
    max_hr = list(cardiac.get_max_heart_rate(loader,start_dt,end_dt,user)[user].values())

    # plotting
    with plt.style.context('ggplot'):
        fig,ax = plt.subplots(figsize=(10,6))
        ax.xaxis.set_major_formatter(date_form)
        ax.plot(dates, rest_hr, label="resting heart rate", c="k",linewidth=1.5,marker="o",markersize=4)
        #ax.plot(dates, avg_hr, label="average heart rate", c="g",linewidth=1.5,marker="o",markersize=4)
        ax.plot(dates, max_hr, label="maximum heart rate", c="r",linewidth=1.5,marker="o",markersize=4)
        #ax.set_title("Heart rate statistics over time",fontsize=18)
        ax.set_ylabel("Heart rate [beats/min]",fontsize=16)
        plt.xticks(rotation=45,fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(loc="upper right",fontsize=15)
        plt.grid("both")
        plt.ylim([min(30,min(rest_hr)),max(200,max_hr_recorded+30)])
        plt.show()

    if verbose:
        print(f"Resting HR: {avg_resting_hr}")
        print(f"Maximum HR: {max_hr_recorded}")

    return stats_dict


def get_rest_spo2_graph(loader,start_dt,end_dt,user):
    
    timedelta = datetime.timedelta(hours=12) # this assumes that at the last day a person wakes up before midday...
    spo2_df = loader.load_garmin_connect_pulse_ox(user,start_dt,end_dt+timedelta)
    sleep_spo2_df = spo2_df[spo2_df.sleep == 1].loc[:,["isoDate","spo2"]]
    unique_dates = pd.to_datetime(sleep_spo2_df.isoDate.dt.date.unique())
    # in order to avoid plotting lines between nights, we need to plot separately each sleep occurrence
    # unfortunately this takes some time (~6-7s/month), to find appropriate night for every row, maybe try to improve?
    sleep_spo2_df["date"] = sleep_spo2_df.isoDate.apply(lambda x: utils.find_nearest_timestamp(x, unique_dates))

    fig, ax = plt.subplots(figsize=(14,6))
    # nights are plotted individually
    for date in unique_dates:
        relevant_data = sleep_spo2_df[sleep_spo2_df.date == date]
        ax.plot(relevant_data.isoDate, relevant_data.spo2,color="gray")

    # get extremes of x-axis
    min_date = sleep_spo2_df.isoDate.min()-timedelta
    max_date = sleep_spo2_df.isoDate.max()+timedelta
    
    # plot coloring by fill_between different y-ranges
    # normal zone
    ax.fill_between([min_date,max_date],
                    [90 for i in range(2)],
                    [100 for i in range(2)],
                    color="g",
                    alpha=.25,
                    label="Normal")
    # low
    ax.fill_between([min_date,max_date],
                    [80 for i in range(2)],
                    [90 for i in range(2)],
                    color="yellow",
                    alpha=.25,
                    label="Low")
    # concerning
    ax.fill_between([min_date,max_date],
                    [70 for i in range(2)],
                    [80 for i in range(2)],
                    color="orange",
                    alpha=.25,
                    label="Concerning")
    # critical
    ax.fill_between([min_date,max_date],
                    [0 for i in range(2)],
                    [70 for i in range(2)],
                    color="tomato",
                    alpha=.25,
                    label="Critical")

    # graph params
    ax.set_ylabel(r"SpO$_2$",fontsize=18)
    ax.set_title(r"Rest SpO$_2$",fontsize=20)

    ax.xaxis.grid(True, color='#CCCCCC')
    ax.xaxis.set_major_formatter(date_form)
    plt.xticks(rotation=60,fontsize=16)
    plt.yticks(fontsize=16)
    plt.ylim([min(50,min(sleep_spo2_df.spo2)),100])
    plt.legend(loc="best",fontsize=16)
    plt.xlim([min_date, max_date])
    plt.tight_layout()
    plt.show()


def get_stress_graph_and_stats(loader, start_dt, end_dt, user, verbose=False):

    # get stats
    dates, metrics = zip(*stress.get_daily_stress_statistics(loader,start_dt,end_dt+datetime.timedelta(days=1),user)[user].items())
    daily_avg_stress, daily_max_stress = list(zip(*metrics))
    avg_stress = round(np.mean(daily_avg_stress))
    stats_dict = {"Averege stress score": avg_stress}

    # Plot yearly stress
    # We need to create a DataFrame with dates going from one year before to the latest datetime
    # Get start and end days from calendar date
    start_date = dates[-1] - datetime.timedelta(days=364)
    # we want to make it inclusive wrt end_date
    end_date = dates[-1] + datetime.timedelta(days=1)
    intervals = int(divmod((end_date - start_date).total_seconds(), 60*60*24)[0])
    time_delta_intervals = [start_date + i * datetime.timedelta(days=1) for i in range(intervals)]

    stress_reduced_df = pd.DataFrame(
        {
            'date': dates,
            'stress': daily_avg_stress
        }
    )

    stress_df = pd.DataFrame(
        {
            'date': time_delta_intervals,
        }
    )

    stress_df = pd.merge(left=stress_df, right=stress_reduced_df, on='date', how='left')

    stress_df.loc[stress_df.stress.isna(), 'stress'] = 0

    july.heatmap(stress_df.date,
                stress_df.stress, 
                cmap="golden",
                title='Average daily stress',
                colorbar=True,
                month_grid=True)

    plt.show()

    if verbose:
        print(f"Average daily stress: {avg_stress}")

    return stats_dict


def get_respiration_graph_and_stats(loader, start_dt, end_dt, user, verbose=False):
    # get series, note that we're inclusive wrt the whole last day
    rest_dates, rest_resp = zip(*respiration.get_rest_breaths_per_minute(loader,start_dt,end_dt+datetime.timedelta(hours=23,minutes=59),user,remove_zero=True)[user].items())
    waking_dates, waking_resp = zip(*respiration.get_waking_breaths_per_minute(loader,start_dt,end_dt+datetime.timedelta(hours=23,minutes=59),user,remove_zero=True)[user].items())
    combined_dates = sorted(list(set(rest_dates+waking_dates))) # not always we have waking/rest data, but need consistent x labeling
    # get stats
    avg_sleeping_breaths = round(np.mean(rest_resp),2)
    avg_waking_breaths = round(np.mean(waking_resp),2)
    stats_dict = {"Average sleep breaths": avg_sleeping_breaths,
                  "Average waking breaths": avg_waking_breaths}

    # plotting
    dates_format = [date.strftime("%d-%m") for date in combined_dates]
    with plt.style.context('ggplot'):
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(rest_dates, rest_resp,marker="o",label="Sleep Avg")
        ax.plot(waking_dates,waking_resp,marker="o",label="Awake Avg")
        ax.legend(loc="best",fontsize=15)
        #ax.set_title("Mean daily breaths per minute",fontsize=15)
        ax.set_ylabel("Breaths per minute",fontsize=15)
        ax.set_xlabel("Date",fontsize=16)
        plt.ylim([min(8,min(rest_resp+waking_resp)),max(rest_resp+waking_resp)+2.5])
        plt.xticks(combined_dates[::2],dates_format[::2],rotation=45,fontsize=15)
        plt.yticks(fontsize=15)
        plt.show()
    
    if verbose:
        print(f"Avg sleep: {avg_sleeping_breaths}")
        print(f"Avg awake: {avg_waking_breaths}")
    
    return stats_dict


def get_sleep_heatmap_and_stats(loader, start_dt, end_dt, user,verbose=True):
    # We need to create a dataframe with dates going from one year before to the latest datetime
    dates, scores = zip(*sleep.get_sleep_score(loader,start_dt,end_dt,user)[user].items())
    # Get start and end days from calendar date
    start_date = dates[-1]-datetime.timedelta(days=364)
    end_date = dates[-1]+datetime.timedelta(days=1)
    intervals = int(divmod((end_date - start_date).total_seconds(), 60*60*24)[0])
    time_delta_intervals = [start_date + i * datetime.timedelta(days=1) for i in range(intervals)]

    sleep_reduced_df = pd.DataFrame(
        {
            'date': dates,
            'sleep': scores
        }
    )

    sleep_df = pd.DataFrame(
        {
            'date': time_delta_intervals
        }
    )

    sleep_df = pd.merge(left=sleep_df, right=sleep_reduced_df, on='date', how='left')
    sleep_df.loc[sleep_df.sleep.isna(), 'sleep'] = 0

    july.heatmap(sleep_df.date, 
                sleep_df.sleep, 
                cmap="BuGn", 
                title='Sleep performance', 
                colorbar=True, 
                month_grid=True)

    plt.show()

    # stats
    avg_deep = sleep.get_deep_sleep_duration(loader,start_dt,end_dt,user,average=True)[user]["values"]
    avg_light = sleep.get_light_sleep_duration(loader,start_dt,end_dt,user,average=True)[user]["values"]
    avg_rem = sleep.get_rem_sleep_duration(loader,start_dt,end_dt,user,average=True)[user]["values"]
    avg_awake = sleep.get_awake_sleep_duration(loader,start_dt,end_dt,user,average=True)[user]["values"]
    avg_awakenings = sleep.get_awakenings(loader,start_dt,end_dt,user,average=True)[user]["value"]
    avg_score = sleep.get_sleep_score(loader,start_dt,end_dt,user,average=True)[user]["values"]

    # average are reported in minutes
    stats_dict = {"Average light sleep": int(avg_light / (1000*60)),
                  "Average deep sleep": int(avg_deep / (1000*60)),
                  "Average REM sleep": int(avg_rem / (1000*60)),
                  "Average awake time": int(avg_awake / (1000*60)),
                  "Average sleep disruptions": round(avg_awakenings,1),
                  "Average sleep score": round(avg_score)}

    if verbose:
        for k,v in stats_dict.items():
            print(f"{k} : {v}")

    return stats_dict


def get_sleep_summary_graph(loader, start_dt, end_dt, user):
    
    # define params for graph
    ALPHA = 0.25
    POSITION = 1.3

    fig, ax = plt.subplots(figsize=(12,21))

    time_period = pd.date_range(start_dt+datetime.timedelta(days=1), 
                        periods=(end_dt-start_dt).days,
                        freq="D")

    # define color-coding based on garmin connect visuals
    color_dict = {1: "royalblue", 3:"darkblue", 4:"darkmagenta", 0:"hotpink"}

    # get relevant scores
    scores_series = sleep.get_sleep_score(loader,start_dt,end_dt,user)[user]
    # get maximum amount of time spent in bed to know x-axis limit
    max_bed_time = np.max([tst for tst in sleep.get_time_in_bed(loader,start_dt,end_dt,user)[user].values() if tst is not None])/60

    # setup an internal fn to get appropriate sleep score colors:
    def get_color(score):
        if score == "":
            return "black"
        else:
            if score >= 90:
                return "forestgreen"
            elif score >= 80:
                return "limegreen"
            elif score >= 60:
                return "darkorange"
            else:
                return "firebrick"

    # for every day in the period of interest, we plot the hypnogram
    for j, night in enumerate(time_period):
        try: # this takes care of days where data is missing, skipping days through the plot y-axis
            # get the hypnogram
            hypnogram = loader.load_hypnogram(user,night)
            # determine when there're stage variations
            hypnogram["stages_diff"] = np.concatenate([[0],hypnogram.iloc[1:,:].stage.values - hypnogram.iloc[:-1,:].stage.values]) != 0
            # get rows relative to initial/final timestamp of sleep or to variations in stage
            relevant_rows = hypnogram.loc[np.logical_or(hypnogram.index.isin([0,len(hypnogram)-1]),hypnogram.stages_diff),["isoDate","stage"]]
            # create a row that indicate the duration of permanence in the stages 
            # (in hours, they will be the height of the sections of the stacked barplot)
            stages_duration = []
            for i in range(len(relevant_rows)-1):
                stages_duration.append((pd.to_datetime(relevant_rows.iloc[i+1].isoDate) - pd.to_datetime(relevant_rows.iloc[i].isoDate)).seconds / (60*60)) 
            stages_duration.append(0) # the last row is not starting a new stage
            relevant_rows["stage duration"] = stages_duration
            # get array of the heights for the sections of the stacked barplot
            array = relevant_rows["stage duration"].values
            colors = [color_dict[stage] for stage in relevant_rows.stage.values]
            # keep track on the position where to begin the bar section
            bottom = 0
            # look through the stages
            for i in range(len(array)):
                # only Deep and REM sleep get full alpha, light and awake are in transparence
                appropriate_alpha = ALPHA if (colors[i]=="royalblue" or colors[i] == "hotpink") else 1
                ax.barh(j*POSITION, array[i], left=bottom, color=colors[i], alpha=appropriate_alpha)
                # Update the bottom coordinates for the next section
                bottom += array[i]
            # annotate on top of the daily bar with the daily sleep score, color-coded appropriately
            score = scores_series.get(night)
            appropriate_color = get_color(score)
            # not sure why but with horizontal bars the annotation has to be manually adjusted in position
            plt.annotate(str(score), xy=(bottom+0.05, j*POSITION+0.2), color=appropriate_color,fontsize=15)
        except: # skip missing dates
            continue

    ax.set_xlim([0,max(10,max_bed_time+.5)])

    # graph and legend params
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#DDDDDD')
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(bottom=False, left=False)
    # this is a tall graph, show also x-axis above?
    # ax_t = ax.secondary_xaxis('top')
    # ax_t.spines["top"].set_visible(False)
    # ax_t.tick_params(top=False)

    # graph params
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color='#EEEEEE')
    ax.yaxis.grid(False)

    ax.set_ylabel('Date', labelpad=15, color='#333333',fontsize=16)
    ax.set_xlabel('Sleep time [hours]', labelpad=15, color='#333333',fontsize=16)

    ax.set_yticks([i*POSITION for i in range(len(time_period))], 
                time_period.strftime("%d/%m").values,
                rotation=0,fontsize=14)

    ax.set_title('Sleep stages and score',
                pad=25,
                color='#333333',
                weight='bold',
                fontsize=20)

    # ordinarly the yaxis starts from below, but it's better to visualize earlier dates on top instead
    plt.gca().invert_yaxis()

    # legend
    labels = ["Deep","Light","REM","Awake"]
    alphas = [1,ALPHA,1,ALPHA]
    colors = ["darkblue","royalblue","darkmagenta","hotpink"]
    lgd = ax.legend(labels=labels, loc='upper center', bbox_to_anchor=(1.1,0.45),fontsize=14)
    # take care of opacity of of the colors selected
    for i,lh in enumerate(lgd.legendHandles):
        lh.set_color(colors[i]) 
        lh.set_alpha(alphas[i])
    lgd.get_frame().set_alpha(0.0)
    lgd.set_title("Sleep stages", prop={"size": 15})

    # code for the colorbar

    bins = [40, 60, 80, 90, 100]
    labels = ["poor", "fair", "good", "excellent"]
    midpoints = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins)-1)]
    colors = ["firebrick","darkorange","limegreen","forestgreen","forestgreen"]

    cmap = mpl.colors.ListedColormap(colors)
    norm = mpl.colors.BoundaryNorm(bins, cmap.N)

    # Create an additional axis for the colorbar
    cax = fig.add_axes([0.935, 0.55, 0.03, 0.2])
    cbar = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap),
                        cax=cax,
                        ticks=midpoints,
                        pad=0.10)
    cbar.ax.set_yticklabels(labels,fontsize=14)

    plt.annotate("Sleep Score", xy=(1.2, 1.1),
                xycoords='axes fraction', ha='center',
                fontsize=14)

    plt.show()


def process_morning_questionnaire(loader,start_dt,end_dt,user):
    # TODO check that questionnaires are filled in the right time range (?)
    # QUITE LIKELY SHOULD BE MOVED TO LOADER OR QUESTIONNAIRES


    # create questionnaire dataframe
    quest_df = loader.process_questionnaire("morning questionnaire")
    # restrict it to the user of interest
    quest_df = quest_df.loc[quest_df.userId == user,:]
    # restrict it to the period of interest
    quest_df = quest_df.loc[np.logical_and(quest_df.isoDate>start_dt, quest_df.isoDate < end_dt),:]
    # get the dictionary with relevant infos for all questions
    questionnaire_dict = loader.get_questionnaire_questions("morning questionnaire")
    # add to the DataFrame relevant information (morning body battery and sleep score)
    timedelta = datetime.timedelta(hours=2) # select a time window to look for maximal body battery wrt time of questionnaire
    quest_df["morning_bb"] = quest_df.isoDate.apply(lambda x: list(stress.get_max_body_battery(loader,x-timedelta,x+timedelta,user)[user].values())[0] 
                                                        if stress.get_max_body_battery(loader,x-timedelta,x+timedelta,user)[user] is not None else None)
    sleeping_scores_dict = sleep.get_sleep_score(loader,start_dt,end_dt,user)[user]
    quest_df["sleep_score"] = quest_df.isoDate.apply(lambda x: sleeping_scores_dict.get(pd.Timestamp(x.date()),None))

    return quest_df, questionnaire_dict                                       


def process_evening_questionnaire(loader,start_dt,end_dt,user):
    # TODO check that questionnaires are filled in the right time range (?)
    # QUITE LIKELY SHOULD BE MOVED TO LOADER OR QUESTIONNAIRES

    # create questionnaire dataframe
    quest_df = loader.process_questionnaire("evening questionnaire")
    # restrict it to the user of interest
    quest_df = quest_df.loc[quest_df.userId == user,:]
    # restrict it to the period of interest
    quest_df = quest_df.loc[np.logical_and(quest_df.isoDate>start_dt, quest_df.isoDate < end_dt),:]
    # get the dictionary with relevant infos for all questions
    questionnaire_dict = loader.get_questionnaire_questions("evening questionnaire")
    # sometimes people answer to the questionnaire later than midnight, we need to get to which day the questionnaire is referring
    quest_df["calendar_day"] = quest_df.isoDate.apply(lambda x: x.date() if not 0 <= x.hour < 12 else x.date()-datetime.timedelta(days=1))
    # get sleeping, stress scores, and sleep stages durations in the period of interest
    sleeping_scores_dict = sleep.get_sleep_score(loader,start_dt,end_dt,user)[user]
    stress_scores_dict = stress.get_daily_stress_statistics(loader,start_dt,end_dt,user)[user].to_dict()
    rem_durations = sleep.get_rem_sleep_duration(loader,start_dt,end_dt,user)[user]
    deep_sleep_durations = sleep.get_deep_sleep_duration(loader,start_dt,end_dt,user)[user]
    # for every day when an evening questionnaire is filled, get the corresponding sleep score (which refers to the night just spent)
    quest_df["prev_sleep_score"] = quest_df.calendar_day.apply(lambda x: sleeping_scores_dict.get(pd.Timestamp(x),None))
    # for every day when an evening questionnaire is filled, get the sleep score for the following day (which refers to the subsequent night of sleep)
    quest_df["next_sleep_score"] = quest_df.calendar_day.apply(lambda x: sleeping_scores_dict.get(pd.Timestamp(x+datetime.timedelta(days=1)),None))
    # for every day when an evening questionnaire is filled, get the stress score (avg, max)
    quest_df["stress_score_metrics"] = quest_df.calendar_day.apply(lambda x: stress_scores_dict.get(pd.Timestamp(x),None))
    quest_df["stress_score"] = quest_df.stress_score_metrics.apply(lambda x: x[0])
    # for every day when an evening questionnaire is filled, get the rem duration for the following night of sleep (can be useful to check with alcohol)
    quest_df["next_rem_duration"] = quest_df.calendar_day.apply(lambda x: rem_durations.get(pd.Timestamp(x)+datetime.timedelta(days=1),None))
    # same with deep sleep
    quest_df["next_deep_sleep_duration"] = quest_df.calendar_day.apply(lambda x: deep_sleep_durations.get(pd.Timestamp(x)+datetime.timedelta(days=1),None))

    return quest_df, questionnaire_dict



def get_errorbar_graph(quest_df, questionnaire_dict, variable_of_interest, answer_of_interest, title, ylabel,answer_categories=None):
    # if a specific order isn't explicitely given, get the order of the answers in the questionnaire
    if answer_categories is None:
        answer_categories = questionnaire_dict[answer_of_interest]["options"]
    # get the description and the string of the full answer id, useful to get the appropriate columns in the dataframe
    answer_descr = questionnaire_dict[answer_of_interest]["description"]
    answer_string = answer_of_interest + "-" + answer_descr

    # get only the relevant columns, drop the rows where there's incomplete data
    tmp_df = quest_df.loc[:,[answer_string,variable_of_interest]].copy().dropna()
    # Get mean and std wrt the variable of interest for every answer level (if std is None (single obs), put it to 0)
    bar_df = tmp_df.loc[:,[answer_string,variable_of_interest]].dropna().groupby(answer_string).agg(Mean=(variable_of_interest,np.mean),Std=(variable_of_interest,np.std)).fillna(0)
    # a bit of a hack, but we need the indexes in the right order for appropriate plotting
    bar_df = bar_df.reindex(answer_categories).dropna()
    # plot bars with height equal to the mean and error reference of std
    ax = bar_df.plot(kind="bar",
                    y="Mean",
                    legend=False,
                    alpha=0.25,
                    figsize=(12,6))
    ax.errorbar(bar_df.index, bar_df["Mean"], yerr = bar_df["Std"], 
                linewidth = 1.5, color = "black", alpha = 0.75, capsize = 10,marker="o")
    # graph params
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE')
    ax.xaxis.grid(False)
    ax.set_ylabel(ylabel,labelpad=15, color="#333333",fontsize=15)
    ax.set_xlabel("")
    ax.set_title(title,
                pad=25,
                color='#333333',
                weight='bold',
                fontsize=20)
    # to avoid overlapping of xlabels, we add newlines every 3 words
    labels = bar_df.index.unique().values
    new_labels = []
    for label in labels:
        label = label.split()
        new_label = []
        for i in range(len(label)):
            new_label.append(label[i])
            if (i+1) % 3 == 0:
                new_label.append("\n")
        new_labels.append(" ".join(new_label))
    plt.xticks(labels,new_labels,rotation=0,fontsize=15)
    plt.yticks(fontsize=15)
    plt.show()


def get_alcohol_influence_on_sleep(quest_df,questionnaire_dict,rem=True,deep=False):
    # THIS SHOULD PROBABLY BE INCLUDED IN THE STANDARD WAY TO BUILD ERRORBAR GRAPHS
    # ADDING THE POSSIBILITY TO ADJUST THE GRAPH GENERATED BY IT.

    variable_of_interest = "next_sleep_score"

    answer_of_interest = "1_13"
    answer_categories = ['No',
                    'Yes, small quantities (eg. a beer)',
                    'Yes, moderate quantities (eg. couple of beers, a single whiskey shot)',
                    'Yes, more than moderate quantities']
    answer_descr = questionnaire_dict[answer_of_interest]["description"]
    answer_string = answer_of_interest + "-" + answer_descr

    tmp_df = quest_df.loc[:,[answer_string,variable_of_interest]].copy().dropna()

    bar_df = tmp_df.loc[:,[answer_string,variable_of_interest]].dropna().groupby(answer_string).agg(Mean=(variable_of_interest,np.mean),Std=(variable_of_interest,np.std)).fillna(0)

    bar_df = bar_df.reindex(answer_categories).dropna()
    ax = bar_df.plot(kind="bar",
                    y="Mean",
                    legend=False,
                    alpha=0.25,
                    figsize=(16,6))


    ax.errorbar(bar_df.index, bar_df["Mean"], yerr = bar_df["Std"], 
                linewidth = 1.5, color = "black", alpha = 0.75, capsize = 10,marker="o")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.tick_params(bottom=False, left=False)

    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE')
    ax.xaxis.grid(False)

    ax.set_ylabel("Sleep score",labelpad=15, color="black",fontsize=16)
    ax.set_xlabel("")
    ax.set_title('Alcohol consumption VS sleep score',
                pad=25,
                color='#333333',
                weight='bold',
                fontsize=18)

    labels = bar_df.index.unique().values
    new_labels = []
    for label in labels:
        label = label.split()
        new_label = []
        for i in range(len(label)):
            new_label.append(label[i])
            if (i+1) % 3 == 0:
                new_label.append("\n")
        new_labels.append(" ".join(new_label))


    plt.xticks(labels,new_labels,rotation=0,fontsize=14)
    plt.yticks(fontsize=15)
    
    if rem:
        # Alchol consumption vs rem sleep duration
        variable_of_interest = "next_rem_duration"

        # get data relative to rem sleep duration for every questionnaire answer given
        tmp_df2 = quest_df.loc[:,[answer_string,variable_of_interest]].copy().dropna()
        tmp_df2.loc[:,variable_of_interest] /= (1000*60*60)
        bar_df2 = tmp_df2.loc[:,[answer_string,variable_of_interest]].dropna().groupby(answer_string).agg(Mean=(variable_of_interest,np.mean),Std=(variable_of_interest,np.std)).fillna(0)
        bar_df2 = bar_df2.reindex(answer_categories).dropna()

        ax2 = ax.twinx()
        ax2.plot(bar_df2["Mean"],marker="o",color="darkmagenta",linewidth=1,alpha=0.75)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(True)
        ax2.spines['left'].set_visible(False)
        ax2.spines['bottom'].set_color('#DDDDDD')
        ax2.tick_params(bottom=False, left=False)
        ax2.set_ylim([0,max(2.5,max(bar_df2["Mean"]))])
        if not deep:
            # the y-axis is designed for only rem sleep in this case
            ax2.spines['right'].set_color('darkmagenta')
            ax2.yaxis.label.set_color('darkmagenta')
            ax2.tick_params(axis='y', colors='darkmagenta')
            ax2.set_ylabel("Average Rem duration [hours]",fontsize=16)
            plt.yticks(fontsize=15)

    if deep:
        # Alchol consumption vs deep sleep duration

        variable_of_interest = "next_deep_sleep_duration"

        # get data relative to deep sleep duration for every questionnaire answer given
        tmp_df3 = quest_df.loc[:,[answer_string,variable_of_interest]].copy().dropna()
        tmp_df3.loc[:,variable_of_interest] /= (1000*60*60)
        bar_df3 = tmp_df3.loc[:,[answer_string,variable_of_interest]].dropna().groupby(answer_string).agg(Mean=(variable_of_interest,np.mean),Std=(variable_of_interest,np.std)).fillna(0)
        bar_df3 = bar_df3.reindex(answer_categories).dropna()

        ax3 = ax.twinx()
        ax3.plot(bar_df3["Mean"],marker="o",color="darkblue",linewidth=1,alpha=0.75,label="Deep Sleep")
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(True)
        ax3.spines['left'].set_visible(False)
        ax3.spines['bottom'].set_color('#DDDDDD')
        ax3.tick_params(bottom=False, left=False)
        ax3.set_ylim([0,max(2.5,max(bar_df3["Mean"]))])
        if not rem:
            # the y-axis is designed for only deep sleep in this case
            ax3.spines['right'].set_color('darkblue')
            ax3.yaxis.label.set_color('darkblue')
            ax3.tick_params(axis='y', colors='darkblue')
            ax3.set_ylabel("Average deep sleep duration [hours]",fontsize=16)
            plt.yticks(fontsize=15)

    if rem and deep:
        ax2.set_ylabel("Average sleep stage duration [hours]",fontsize=12)
        # fake axis to better manage legend
        legend_ax = ax.twinx()
        legend_ax.plot([],[],color="black",marker="o",label="Sleep score")
        legend_ax.plot([],[],color="darkmagenta",marker="o",label="REM sleep")
        legend_ax.plot([],[],color="darkblue",marker="o",label="Deep sleep")
        legend_ax.axis("off")

        legend_ax.legend(loc=0)

    plt.show()