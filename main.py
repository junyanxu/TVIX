import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from model.vix import build_vix_sig

__author__ = 'junyan'
holding_period = 1000
locking_period = 40
stoploss = 0.6

tvix_data = pd.read_csv(
    "/Users/junyan/Desktop/tvix/data/tvix.csv",
    parse_dates=True).sort_values(['Date']).set_index('Date')
sp500_data = pd.read_csv(
    "/Users/junyan/Desktop/tvix/data/sp500.csv",
    parse_dates=True).sort_values(['Date']).set_index('Date')

tvix_data.columns = ["tvix_" + i for i in tvix_data.columns]
sp500_data.columns = ["sp500_" + i for i in sp500_data.columns]

sp500_data["sp500_60 return"] = (sp500_data["sp500_Adj Close"].diff(60) /
                                 sp500_data["sp500_Adj Close"])
sp500_data["sp500_120 return"] = (sp500_data["sp500_Adj Close"].diff(120) /
                                  sp500_data["sp500_Adj Close"])
data = pd.concat(
    [tvix_data, sp500_data],
    axis=1, join='outer')


data["tvix_40_return"] = (
    data["tvix_Adj Close"].diff(40).shift(-40) /
    data["tvix_Adj Close"]
)

data["tvix_last_return"] = (
    data["tvix_Adj Close"].diff(1)/data["tvix_Adj Close"]
)
data["tvix_return"] = data["tvix_last_return"].shift(-1)

data = data.dropna()
data = pd.merge(data, build_vix_sig(2, show=False),
                how='inner', left_index=True, right_index=True)

def compute_max_drawn_down(PNL):
    current_max = PNL[0]
    current_max_drawn_down = 0
    for i in list(PNL)[1:]:
        current_max = max(i, current_max)
        current_max_drawn_down = max(
            current_max_drawn_down,
            (current_max-i) / current_max
        )
    return current_max_drawn_down

def rolling_backtest(data):
    dates = data.index
    position = [0]
    holding_count = [0]
    lock_count = [0]
    current_max = [1]
    max_drowndown = [0]
    enter = [0]
    left = [0]
    for i in dates[1:]:
        background = data.loc[i, :]
        if background['vix_sell_sig'] == 1 and position[-1] == 0:
            position.append(-1)
            holding_count.append(1)
            enter.append(1)
            left.append(0)
            
        elif background["tvix_last_return"] > 0 and position[-1] == -1:
            position.append(0)
            holding_count.append(0)
            enter.append(0)
            left.append(1)
        
        elif holding_count[-1] == holding_period and position[-1] == -1:
            position.append(0)
            holding_count.append(0)
            enter.append(0)
            left.append(1)
        else:
            position.append(position[-1])
            holding_count.append(holding_count[-1]+1)
            enter.append(0)
            left.append(0)
        
    data["position"] = position
    data["enter"] = enter
    data["left"] = left
    data["cum_pnl_single"] = (data['position'] * data["tvix_return"]).cumsum()
    data["cum_pnl_compound"] = (
        1 + data['position'] * data["tvix_return"]).cumprod()
    
    plot, axe = plt.subplots(2, 2)
    data[
        [
            "cum_pnl_single",
            "sp500_Adj Close"
        ]
    ].plot(ax=axe[0][0], secondary_y="sp500_Adj Close")

    data[
        [
            "cum_pnl_compound",
            "sp500_Adj Close"
        ]
    ].plot(ax=axe[1][0], secondary_y="sp500_Adj Close")
    axe[0][1].hist(data['tvix_return'][data['position'] == -1], bins=30)
    monthly_pnl = data['cum_pnl_compound'].resample('M', how='last')
    (monthly_pnl.diff()/monthly_pnl.shift(1)).plot(ax=axe[1][1])
    print(data[["position", "tvix_return",
                "vix_Adj Close",
                "vix_sell_sig",
                "left"]])
    data.to_excel("result.xlsx")
    plt.show()


if __name__ == '__main__':
    rolling_backtest(data)
    print("max drawndown:", compute_max_drawn_down(data.cum_pnl_compound))
    plt.show()
