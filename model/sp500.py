from TVIX.data.data_util import read_data

from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np



start_date = pd.datetime(2010, 1, 1)
end_date = datetime.today()

sp500 = read_data(start_date, end_date, 'sp500')

def create_day_down_reverse(price_row):
    mid = (price_row['Open'] + price_row['Close'])/2
    ret = price_row['Close'] - price_row['Open']
    down = mid - price_row['Low']
    up = price_row['High'] - mid
    return down/up


sp500['down_reverse'] = sp500.apply(create_day_down_reverse, axis=1)
sp500['down_reverse_10'] = pd.rolling_mean(sp500['down_reverse'], 10)
sp500[['Close', 'down_reverse_10']].plot(secondary_y='down_reverse_10')
plt.show()

sp500[sp500['down_reverse'] < 0]
