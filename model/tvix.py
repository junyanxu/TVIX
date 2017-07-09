from TVIX.data.data_util import read_data
from TVIX.model.econ import attach_PMI_index
from datetime import datetime
from pandas.tseries.offsets import MonthBegin, BDay, Day
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
%matplotlib inline

start_date = datetime(2010, 12, 1)
end_date = datetime(2017, 6, 30)

tvix = read_data(start_date, end_date, 'tvix')
tvix["date"] = tvix.index.copy()
tvix["BM_date"] = tvix["date"] +Day(1) - MonthBegin() - BDay() + BDay()
tvix["day_return"] = (tvix['Close'] - tvix['Open'])/tvix['Open']
tvix["day_return_n1"] = tvix['day_return'].shift(-1)
tvix["Open_n1"] = tvix['Open'].shift(-1)
tvix["night_return"] = (tvix['Open_n1']- tvix['Close'])/tvix['Close']
tvix["night_return_n1"] = tvix["night_return"].shift(-1)
tvix["night_return_indicator"] = tvix["night_return"].apply(lambda x: 1 if x>0.04 else 0)
tvix = attach_PMI_index(tvix)
tvix = tvix.dropna()
tvix

freq = tvix.groupby("BM_date")["night_return_indicator"].sum()
freq
PMI_Health = tvix.groupby("BM_date")["PMI_Health"].first()

plt.scatter(PMI_Health, freq)
