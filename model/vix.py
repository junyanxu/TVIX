"""
Description:
this file is for producing research and signal for vix index, two types of class are available:
1. {}_creater: for appending signals on dataframe
2. {}_researcher: for plotting

"""

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


__author__="junyanxu5513@gmail.com"


def load_data():
    def _append_last_return(x):
        x["Last Return"] = x["Adj Close"].diff(1)/x["Adj Close"].shift(1)

    vix = pd.read_csv(
        "/Users/junyan/Desktop/tvix/data/vix.csv",
        index_col=0, parse_dates=True)
    vix["date"] = vix.index
    _append_last_return(vix)
    sp500 = pd.read_csv(
        "/Users/junyan/Desktop/tvix/data/sp500.csv",
        index_col=0, parse_dates=True
    )
    sp500["date"] = sp500.index
    _append_last_return(sp500)

    price = pd.merge(vix, sp500,
                     left_on='date',
                     right_on='date',
                     how='inner', suffixes=["_vix", "_sp500"])
    price.index=price.date
    return price


def _concav_apply(self, x, num_increase, num_decrease):
    assert len(x) == num_decrease + num_increase + 1
    flag_increase = [x[i+1] - x[i] > 0 for i in range(num_increase)]
    flag_decrease = [
        x[num_increase+i+1] - x[num_increase+i] < 0 for i in range(num_decrease)
    ]
    return all(flag_increase) and all(flag_decrease)


def vix_sell_sig(price_source, ma_length, show=True):   
    price = price_source.copy()
    price = price[price != 'null'].astype('float')
    ma_120 = price.rolling(120).mean()
    ra_120 = price - ma_120
    ma = price.rolling(ma_length).mean()
    data = pd.DataFrame({"Adj Close": price,
                         "ma120": ma_120,
                         "ra120": ra_120,
                         "ma": ma,
                         "mara120": ma-ma_120})
    data = data.dropna()
    data["sell_sig"] = pd.rolling_apply(
        data["Adj Close"], num_increase + num_decrease + 1,
        lambda x: _concav_apply(x, num_increase, num_decrease))
    data["concav"] = data["sell_sig"].shift(-1)
    data = data.dropna()
    if show:
        plot, axe = plt.subplots(2, 2)
        axe[0][0].scatter(data.index,
                          data["mara120"]*data["sell_sig"].apply(
                           lambda x: x if x != 0 else np.nan
                          ), color='g')
        data['mara120'].plot(ax=axe[0])
        axe[1][0].scatter(data.index,
                          data["Adj Close"]*data["sell_sig"].apply(
                              lambda x: x if x != 0 else np.nan),
                          color='g')
        data['Adj Close'].plot(ax=axe[0][1])
        plt.show()
    data.columns = ["vix_" + i for i in data.columns]
    return data


def vix_gap_research(price, period=[3, 5]):

    def _peak_apply_func(data, period1, period2):
        assert len(data) == period1 + period2 + 1
        return np.all(data[period1] > data[:period1]) and np.all(data[period1] > data[-period2:]) and data[0] < data[period1] and data[-1] < data[period1]
    
    def _create_peaks(price, period):
        peaks = pd.rolling_apply(price, period[0] + period[1] + 1, lambda x:_peak_apply_func(x, period[0], period[1])).shift(-period[1])
        last_peak_date = peaks.index[0]
        gaps = [np.nan]
        for i in range(1, len(peaks)):
            if peaks.values[i] == True:
                gaps.append(np.busday_count(last_peak_date, peaks.index[i]))
                last_peak_date = peaks.index[i]
            else:
                gaps.append(np.nan)
        gaps = pd.Series(gaps, index=peaks.index)
        return peaks, gaps

    def _create_gap_stats_distribution(gaps_days):
        max_gap = np.max(gaps_days)
        f = np.zeros(max_gap)
        for i in gaps_days:
            f[i-1] += 1

        f = f/np.sum(f)
        F = np.cumsum(f)
        F_bar = np.roll(np.cumsum(f[::-1])[::-1]/np.sum(f), -1)
        F_bar[-1] = 0

        x = range(max_gap)
        y = range(max_gap)
        x, y = np.meshgrid(x, y)
        @np.vectorize
        def _condition_prob(x, y):
            if x+y >= max_gap:
                return 1
            else:
                return (F[x+y] - F[x])/F_bar[x]
        table = _condition_prob(x, y)
        
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_wireframe(x, y, table)
        ax.set_xlabel('conditional on n days past')
        ax.set_ylabel('at next n days')
        ax.set_zlabel('probablity of up jump')
        plt.show()

    def _create_thining_variable(price, suffix='_sp500'):
        intra_day_vol = (
            price["High{}".format(suffix)] - price["Low{}".format(suffix)]
            + price["High{}".format(suffix)] - price["Open{}".format(suffix)]
            + price["Close{}".format(suffix)] - price["Low{}".format(suffix)]
        )/3/price["Open{}".format(suffix)]
        EOD_day_vol = np.abs(price["Adj Close{}".format(suffix)].diff(1))/price["Adj Close{}".format(suffix)].shift(1)
        price["Thining{}".format(suffix)] = EOD_day_vol.rolling(5).mean()
    
    def _append_past_n_gaps(vix, n):
        assert "gaps" in vix.columns
        first_gap = vix["gaps"][vix["gaps"] != 0].iloc[0]
        last_n_gaps = [first_gap for i in range(n)]
        res = []
        for i in vix["gaps"].index:
            if vix["gaps"][i] != 0:
                last_n_gaps.append(vix["gaps"][i])
                last_n_gaps.pop(0)
            res.append(last_n_gaps)
        res = np.array(res)
        for i in range(n):
            vix["Last Gap{}".format(i+1)] = res[:, i]
        vix["Avg Last {} Gaps".format(n)] = vix[["Last Gap{}".format(i+1) for i in range(n)]].apply(np.mean, axis=1)
        return vix

    def _append_peak_start(vix, effective_thresh=0.85):
        assert "peaks_vix" in vix.columns
        assert "Adj Close_vix" in vix.columns
        start_index = 0
        vix["peaks_start_vix"] = 0
        for i in range(len(vix["peaks_vix"])):
            if vix["peaks_vix"].values[i] == True:
                peaks_start_index = start_index + np.argmin(vix["Adj Close_vix"].values[start_index: i])
                
                peak_magnitude = vix["Adj Close_vix"].values[i] - vix["Adj Close_vix"].values[peaks_start_index]
                for j in list(range(peaks_start_index, i))[::-1]:
                    if vix["Adj Close_vix"].values[i] - vix["Adj Close_vix"].values[j] > effective_thresh*peak_magnitude:
                        vix["peaks_start_vix"].values[j] = 1
                        break
                start_index = i + 1
    
    peaks_buff = _create_peaks(price['Adj Close_vix'], period)
    price["peaks_vix"] = peaks_buff[0].fillna(0)
    price["gaps_vix"] = peaks_buff[1].fillna(0)
    _append_peak_start(price)
    _create_thining_variable(price, suffix="_vix")
    # price["vix_norm"] = price["Adj Close_vix"]/np.max(price["Adj Close_vix"])
    #price["Thining_norm"] = price["Thining_vix"]/np.max(price["Thining_vix"])

    price["Thining_norm"] = 2*((1 + np.exp(-5*price["Thining_vix"]))**-1)-1
    #price[["Relative Thining_sp500", "vix_norm", "peaks_vix"]].plot(secondary_y="Relative Thining_sp500")
    # buff = price["Adj Close_vix"][price["peaks_vix"] == True]
    # days_gap_stats = price["gaps_vix"][price["gaps_vix"] != 0].astype('int')
    # plt.plot(list(days_gap_stats))
    # price["peaks_vix"][peaks] = 1
    price[["peaks_vix", "peaks_start_vix", "Adj Close_vix", "Thining_norm"]].plot(secondary_y=["peaks_vix", "peaks_start_vix", "Thining_norm"])
    plt.show()
    #_create_gap_stats_distribution(days_gap_stats)

if __name__ == '__main__':
    #    vix_gap_research(price)
    num_increase=1
    num_decrease=1
    price = load_data()
    vix_gap_research(price, [10, 7])

    
