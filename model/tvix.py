from TVIX.data.data_util import read_data
from TVIX.model.econ import attach_PMI_index
from datetime import datetime
from pandas.tseries.offsets import MonthBegin, BDay, Day
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

start_date = datetime(2010, 12, 1)
end_date = datetime(2017, 6, 30)


%matplotlib inline

tvix = read_data(start_date, end_date, 'tvix')
tvix["date"] = tvix.index.copy()
tvix["BM_date"] = tvix["date"] +Day(1) - MonthBegin() - BDay() + BDay()
tvix["day_return"] = (tvix['Close'] - tvix['Open'])/tvix['Open']
tvix["day_return_n1"] = tvix['day_return'].shift(-1)
tvix["Open_n1"] = tvix['Open'].shift(-1)
tvix["night_return"] = (tvix['Open_n1']- tvix['Close'])/tvix['Close']
tvix["night_return_n1"] = tvix["night_return"].shift(-1)
tvix["night_return_indicator"] = tvix["night_return"].apply(lambda x: 1 if x>0.05 else 0)
tvix["day_return_indicator"] = tvix["day_return"].apply(lambda x: 1 if x>0.05 else 0)
tvix["concern_indicator"] = (tvix["night_return_indicator"] | tvix["day_return_indicator"])
tvix = attach_PMI_index(tvix)
tvix = tvix.dropna()
tvix

freq = tvix.groupby("BM_date")["concern_indicator"].sum()
PMI_Health = tvix.groupby("BM_date")["PMI_Health"].first()
PMI_RSI =  tvix.groupby("BM_date")["PMI_RSI"].first()

PMI_Health

plt.scatter(PMI_Health, PMI_RSI, freq*10)
for i in freq.index:
    if freq[i] > 6:
        plt.text(PMI_Health[i], PMI_RSI[i], i.strftime("%Y-%m-%d"))
