import pandas as pd
import numpy as np
import sys
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import dates
import re
import math
import pickle


class Market_regime_plot:
    def __init__(self, data, data_freq="d"):
        pd.plotting.register_matplotlib_converters()
        self.data_freq = data_freq
        self.data = data
        frequency = None
        if not pd.infer_freq(self.data.index):
            if self.data_freq == "d":
                frequency = "B"
            elif self.data_freq == "h":
                frequency = "BH"
            elif self.data_freq == "m":
                frequency = "T"

    # 	self.data = self.data.asfreq(frequency, method="ffill")
    def plot_market_regime(self, figsize=(30, 15), day_interval=10, save_pic=""):
        data_numberOfYears = np.unique(self.data.index.year)
        try:
            for (index, year) in enumerate(data_numberOfYears):
                data = self.data.loc[str(year)]
                plot = plt.figure(index)
                self.plot(data, figsize, day_interval, save_pic)
        except:
            print("There was an error during enumerating over number of years in data")
            print(sys.exc_info()[0])
        plt.show()

    def plot(self, data, figsize, day_interval, save_pic):
        data_to_draw = data
        # drawing boilderplate
        nrows = 2
        fig, ax = plt.subplots(
            nrows=nrows,
            sharex=True,
            figsize=figsize,
            gridspec_kw={"height_ratios": [8, 2]},
        )
        [ax[i].cla() for i in range(nrows)]
        [ax[i].set_facecolor("k") for i in range(nrows)]
        [
            ax[i].xaxis.set_major_locator(dates.DayLocator(interval=day_interval))
            for i in range(nrows)
        ]
        [
            ax[i].xaxis.set_major_formatter(dates.DateFormatter("%y-%m-%d"))
            for i in range(nrows)
        ]
        [
            ax[i].grid(color="r", linestyle="-", linewidth=1, alpha=0.3)
            for i in range(nrows)
        ]
        plt.xticks(rotation=90)

        # drawing price graph
        ax[0].plot(data_to_draw["Price"], label="Price", color="dimgray")

        # annotate plot with DC info
        self.annotate_plot(data_to_draw, ax[0])

        ax[1].plot(
            data_to_draw["pct_change"], color="y", linewidth=1.5, label="Price return"
        )
        [ax[i].legend(loc="lower right", prop={"size": 6}) for i in range(2)]
        [ax[i].legend(loc="upper left", prop={"size": 5}) for i in range(2, nrows)]
        if save_pic:
            pickle.dump(fig, open(f"{save_pic}.pickle", "wb"))

    def annotate_plot(self, data_to_draw, plot_to_annotate):
        data_event_columns = self.data.filter(regex=("Event.*"))
        # figuring out how much to space arrows in annotations out:
        first_round = True
        fontsize = 10
        if self.data_freq == "d":
            freq = "days"
            duration = min(
                math.floor(
                    (data_to_draw.index[-1].date() - data_to_draw.index[0].date()).days
                    / 90
                ),
                6,
            )
        elif self.data_freq == "h":
            freq = "hours"
            duration = min(
                math.floor(
                    (data_to_draw.index[-1].date() - data_to_draw.index[0].date()).days
                    / 90
                ),
                6,
            )
        elif self.data_freq == "m":
            one_day = 60 * 24
            freq = "minutes"
            length = len(data_to_draw)
            duration = min(math.ceil(one_day / length), 0.1)
            offset_value_reduction = max((1 / duration), 10)

        for column in data_event_columns:
            annotate_result = data_to_draw[data_to_draw[column].notnull()]
            match = re.search(r"(Event_)([\w\.-]+)", column)
            superscript = match.group(2)
            if first_round:
                color = "#e60ed7"
                offset_value = 1
            else:
                color = "#0c7ea8"
                offset_value = 5
            if self.data_freq == "m":
                offset_value /= offset_value_reduction
            for index, row in annotate_result.iterrows():
                text = "%s%s" % (row[column], superscript)
                if (
                    row[column] == "Down"
                    or row[column] == "Down+DXP"
                    or row[column] == "DXP"
                ):
                    if row[column] == "Down":
                        plot_to_annotate.annotate(
                            text,
                            xy=(index, row["Price"]),
                            xytext=(
                                index - datetime.timedelta(**{freq: (duration * 4)}),
                                (row["Price"] + (duration * 2) - offset_value),
                            ),
                            horizontalalignment="center",
                            color=color,
                            arrowprops=dict(
                                arrowstyle="->",
                                connectionstyle="angle3,angleA=0,angleB=90",
                                color=color,
                            ),
                            fontsize=fontsize,
                        )
                    if row[column] == "Down+DXP" or row[column] == "DXP":
                        plot_to_annotate.annotate(
                            text,
                            xy=(index, row["Price"]),
                            xytext=(
                                index - datetime.timedelta(**{freq: (duration * 4)}),
                                (row["Price"] - (duration * 2) - offset_value),
                            ),
                            horizontalalignment="center",
                            color=color,
                            arrowprops=dict(
                                arrowstyle="->",
                                connectionstyle="angle3,angleA=0,angleB=90",
                                color=color,
                            ),
                            fontsize=fontsize,
                        )
                    if not first_round:
                        downText = ""
                        if (
                            not math.isnan(data_to_draw.loc[index]["BBTheta"])
                            and data_to_draw.loc[index][column] == "Down"
                        ):
                            downText = str(data_to_draw.loc[index]["BBTheta"])
                        if not pd.isnull(data_to_draw.loc[index]["OSV"]):
                            string = str(
                                data_to_draw.loc[index]["OSV"].round(decimals=2)
                            )
                            if downText:
                                string += "--" + downText
                            downText = string
                        if downText:
                            plot_to_annotate.annotate(
                                downText,
                                xy=(index, row["Price"]),
                                xytext=(
                                    index
                                    - datetime.timedelta(**{freq: (duration * 10)}),
                                    (row["Price"] - (duration)),
                                ),
                                horizontalalignment="center",
                                color="#bac90a",
                                arrowprops=dict(
                                    arrowstyle="->",
                                    connectionstyle="angle3,angleA=0,angleB=90",
                                    color="#bac90a",
                                ),
                                fontsize=fontsize,
                            )
                elif (
                    row[column] == "Up"
                    or row[column] == "Up+UXP"
                    or row[column] == "UXP"
                ):
                    if row[column] == "Up":
                        plot_to_annotate.annotate(
                            text,
                            xy=(index, row["Price"]),
                            xytext=(
                                index + datetime.timedelta(**{freq: (duration * 1)}),
                                (row["Price"] - (duration * 2)),
                            ),
                            horizontalalignment="center",
                            color=color,
                            arrowprops=dict(
                                arrowstyle="->",
                                connectionstyle="angle3,angleA=0,angleB=-60",
                                color=color,
                            ),
                            fontsize=fontsize,
                        )
                    elif row[column] == "Up+UXP" or row[column] == "UXP":
                        plot_to_annotate.annotate(
                            text,
                            xy=(index, row["Price"]),
                            xytext=(
                                index - datetime.timedelta(**{freq: (duration * 4)}),
                                (row["Price"] + (duration * 2) + offset_value),
                            ),
                            horizontalalignment="center",
                            color=color,
                            arrowprops=dict(
                                arrowstyle="->",
                                connectionstyle="angle3,angleA=0,angleB=90",
                                color=color,
                            ),
                            fontsize=fontsize,
                        )
                    if not first_round:
                        upText = ""
                        if (
                            not math.isnan(data_to_draw.loc[index]["BBTheta"])
                            and data_to_draw.loc[index][column] == "Up"
                        ):
                            upText = str(data_to_draw.loc[index]["BBTheta"])
                        if not pd.isnull(data_to_draw.loc[index]["OSV"]):
                            string = str(
                                data_to_draw.loc[index]["OSV"].round(decimals=2)
                            )
                            if upText:
                                string += "--" + upText
                            upText = string
                        if upText:
                            plot_to_annotate.annotate(
                                upText,
                                xy=(index, row["Price"]),
                                xytext=(
                                    index
                                    - datetime.timedelta(**{freq: (duration * 10)}),
                                    (row["Price"] + (duration)),
                                ),
                                horizontalalignment="center",
                                color="#bac90a",
                                arrowprops=dict(
                                    arrowstyle="->",
                                    connectionstyle="angle3,angleA=0,angleB=120",
                                    color="#bac90a",
                                ),
                                fontsize=fontsize,
                            )
            first_round = False
        return None
