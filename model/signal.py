"""
Description:
this file is a toolkit for producing signals.

The general interface will be adding an extra column to the dataframe

"""
import pandas as pd
import numpy as pd

def create_peaks(price, period):
    """
    args:
        price: a time series in which to find peaks
        period: a list contain two time length. the peak must be higher than
            any values in the period
    output:
        peaks and gaps as time series
    """
    def _peak_apply_func(data, period1, period2):
        assert len(data) == period1 + period2 + 1
        return (
            np.all(data[period1] > data[:period1])
            and np.all(data[period1] > data[-period2:])
            and data[0] < data[period1] and data[-1] < data[period1])

    peaks = pd.rolling_apply(
        price,
        period[0] + period[1] + 1,
        lambda x:_peak_apply_func(x, period[0], period[1])
    ).shift(-period[1])

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


def create_thining_(price, suffix='_sp500'):
    intra_day_vol = (
        price["High{}".format(suffix)] - price["Low{}".format(suffix)]
        + price["High{}".format(suffix)] - price["Open{}".format(suffix)]
        + price["Close{}".format(suffix)] - price["Low{}".format(suffix)]
    )/3/price["Open{}".format(suffix)]
    EOD_day_vol = np.abs(price["Close{}".format(suffix)].diff(1))/price["Close{}".format(suffix)].shift(1)
    price["Thining{}".format(suffix)] = EOD_day_vol.rolling(5).mean()
    return price
