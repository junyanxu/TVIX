from TVIX.data.data_util import read_data
from datetime import datetime
from pandas.tseries.offsets import MonthBegin, BDay, Day
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def create_PMI_RSI(pmi):
    pmi["PMI_Return"] = pmi["Index"].diff(1)/pmi["Index"].shift(1)
    pmi["PMI_RSI"] = pmi["PMI_Return"].rolling(window=6).apply(
        lambda x: np.sum(x[x > 0])/np.sum(np.abs(x))
    )


def create_PMI_health(pmi):
    up_scale = np.max(pmi["Index"][pmi["Index"] > 50] - 50)
    down_scale = np.max(50 - pmi["Index"][pmi["Index"] < 50])
    pmi["PMI_Health"] = pmi["Index"].apply(
        lambda x: (x-50)/up_scale if x > 50 else (x - 50)/down_scale
    )


def create_PMI_index():
    start_date = datetime(2003, 11, 1)
    end_date = datetime.today()
    pmi = read_data(start_date, end_date, 'PMI')
    pmi["date"] = pmi.index.copy()
    create_PMI_RSI(pmi)
    create_PMI_health(pmi)
    return pmi.rename(columns={"Index": "PMI"})


def attach_PMI_index(df):
    df["month_start"] = df["date"] + Day(1) - MonthBegin()
    df["first_B_day_of_month"] = df["month_start"] - BDay() + BDay()
    res = pd.merge(
        df, create_PMI_index(),
        left_on='first_B_day_of_month',
        right_on='date',
        how='left'
    )
    res = res.drop(["month_start", "first_B_day_of_month", "date_y"], axis=1)
    res = res.rename(columns = {"date_x": "date"})
    res.index = res["date"]
    return res
