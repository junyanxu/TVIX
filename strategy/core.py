from TVIX.data.tick import fetch_data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""
    env is a dictionary contain subjective information:
    1. time
    2. price

    port is a dictionary contain portfolio information:
    1. size
    2. market_value
    3. cash

    hist is a dictionary contain informatio:
    1. trades:
        list_of_trade

    2. perfomance:
        1. PNL

    command is a dictionary contain information:
        1. time
        2. size

    trade is a dictionary contain information:
        1. time
        2. size
        3. price
"""

def create_env(price, time, volume, idx):
    return {
        'price': price[idx],
        'time': time[idx],
        'volume': volume[idx]
    }


def create_trade(env, command):
    if command is not None:
        command['price'] = env['price']
    return command


def create_port(env, port, trade):
    if trade is not None:
        port['size'] += trade['size']
        port['cash'] -= trade['size']*trade['price']

    port['market_value'] = port['size']*env['price']
    return port


def create_hist(env, trade, port, hist):
    if trade is not None:
        hist['trades'].append(trade)
    PNL = port['size']*env['price'] - port['market_value']
    hist['PNL'].append(PNL)
    return hist


def run(algo, algo_strats, data):
    price = data['price'].values
    time = data['time'].values
    volume = data['volume'].values
    idx = range(data.shape[0])

    port = {
        'size': 0,
        'market_value': 0,
        'cash': 100000
    }

    hist = {
        'trades':[],
        'PNL':[]
    }

    trade = None
    strats = algo_strats()
    for i in idx:
        env = create_env(price, time, volume, i)
        hist = create_hist(env, trade, port, hist)
        command, strats = algo(env, port, hist, strats)
        trade = create_trade(env, command)
        port = create_port(env, port, trade)

    return hist


if __name__ == '__main__':

    from TVIX.strategy.dynamic_option import algo, strats

    dates = pd.date_range('2015-08-25', '2015-08-30')
    res = fetch_data(dates, 'tvix', transform=True)

    hist = run(algo, strats, res)
    plt.plot(
        range(hist['PNL'].__len__()),
        np.cumsum(hist['PNL']),
        label='PNL',
        color='r'
    )

    ax2 = plt.twinx()
    ax2.plot(
        range(hist['PNL'].__len__()),
        res['price'],
        label='price'
    )
    plt.show()
