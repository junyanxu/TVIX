import numpy as np
import pandas as pd

class strats:
    def __init__(self):
        self.price_window = list()
        self.pnl_window = list()
        self.strike = None
        self.begin_time = None
        self.pnl_window = list()

    def update(self, env, hist):
        if len(self.price_window) > 2000:
            self.price_window.pop(0)
        self.price_window.append(env["price"])
        if len(self.pnl_window) > 2000:
            self.pnl_window.pop(0)
        self.pnl_window.append(hist['PNL'][-1])


def algo(
    env,
    port,
    hist,
    strats,
):
    """
        env is a dictionary contain subjective information:
        1. time
        2. price

        port is a dictionary contain portfolio information:
        1.size
        2.maturity_time
        3.strike
        4.enter_time

        hist is a dictionary contain informatio:
        1. history trades
        2. PNL

        command is a dictionary contain information:
        1. size
        2. bs

        trade is a dictionary contain information:
        1. size
        2. bs

        strat is a variable representing the perception of the robot:
        1. price_window:
        2. PNL_window:

    """
    current_time = env['time']
    price = env['price']
    size = port['size']

    strats.update(env, hist)
    command = None

    if (strats.begin_time is None) or ((current_time - strats.begin_time) > np.timedelta64(60, 's')):
        if port['size'] != 0:
            command = {
                'size':-port['size'],
                'time':current_time
            }
        else:
            strats.strike = price
            strats.begin_time = current_time

    else:
        if price > strats.strike:
            if port['size'] < 0:
                command = {
                    'size':-2*port['size'],
                    'time':current_time
                    }
            elif port['size'] == 0:
                command = {
                    'size':1,
                    'time':current_time
                    }
            else:
                pass

        elif price < strats.strike:
            if port['size'] > 0:
                command = {
                    'size':-2*port['size'],
                    'time':current_time
                    }
            elif port['size'] == 0:
                command = {
                    'size': -1,
                    'time':current_time
                    }

    print strats.strike, price, port['size'], (current_time - strats.begin_time)/np.timedelta64(1, 's'), hist['PNL'][-1], port['market_value']

    return command, strats
