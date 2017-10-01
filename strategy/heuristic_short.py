import pandas as pd
import matplotlib.pyplot as plt

from TVIX.data.data_util import read_data
from TVIX.model.econ import attach_PMI_index

start_date = pd.datetime(2011, 1, 1)
end_date = pd.datetime.today()
holding_period = 10

tvix = read_data(start_date, end_date, 'tvix')
tvix['date'] = tvix.index
tvix['tvix_last_return'] = tvix['Close'].diff(1)/tvix['Close'].shift(1)
tvix['tvix_return'] = tvix['Close'].diff(1).shift(-1)/tvix['Close']
tvix['vix_sell_sig'] = tvix['Close'].rolling(4).apply(
    lambda x: (x[0] < x[1]) and (x[1] > x[2]) and (x[2] > x[3])
    # lambda x: (x[0] < x[1]) and (x[1] > x[2])
)

tvix = attach_PMI_index(tvix)



def current_econ_is_health(background):
    if background.PMI_Health > 0.1 and background.PMI_RSI > -0.7:
        return True
    else:
        return False

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
        if background['vix_sell_sig'] == 1 and position[-1] == 0 and current_econ_is_health(background):
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
            "PMI_Health",
            "PMI_RSI",
        ]
    ].plot(ax=axe[0][0], secondary_y=["PMI_Health", "PMI_RSI"])

    data[
        [
            "cum_pnl_compound",
            "PMI_Health",
            "PMI_RSI",
        ]

    ].plot(ax=axe[1][0], secondary_y=["PMI_Health", "PMI_RSI"])
    # axe[0][1].hist(data['tvix_return'][data['position'] == -1], bins=30)
    monthly_pnl = data['cum_pnl_compound'].resample('M', how='last')
    #(monthly_pnl.diff()/monthly_pnl.shift(1)).plot(ax=axe[1][1])
    # print(data[["position", "tvix_return",
    #            "vix_sell_sig",
    #            "left"]])



if __name__ == '__main__':
    rolling_backtest(tvix)
    #print("max drawndown:", compute_max_drawn_down(tvix.cum_pnl_compound))
    tvix.to_csv('simulation_{}.csv'.format(
        pd.datetime.today().strftime('%Y-%m-%d')
        )
    )
    plt.show()
