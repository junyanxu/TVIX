from os import path
import pandas as pd
import numpy as np

# %matplotlib inline

def fetch_single_date_data(date, ticker):
    path = '~/Downloads/942439_csv/{0}/{1}.csv'.format(
        date.strftime("%Y%m%d"),
        ticker
    )
    res = pd.read_csv(
        path,
        names=['time', 'price',
               'size', 'exchange',
               'sale_condition', 'suspicious']
        )
    res.price = res.price/10000.
    res.time = res.time.apply(lambda x: pd.Timedelta(np.int(x/1000), 's')) + date
    return res


def fetch_data(dates, ticker, transform=False):
    if not hasattr(dates, '__iter__'):
        file_path = '/Users/junyan/Downloads/942439_csv/{0}/{1}.csv'.format(
            dates.strftime("%Y%m%d"),
            ticker
        )
        if path.exists(file_path):
            res = fetch_single_date_data(dates, ticker)
        else:
            res = None
    elif hasattr(dates, '__iter__'):
        res = []
        for i in dates:
            file_path = '/Users/junyan/Downloads/942439_csv/{0}/{1}.csv'.format(
                i.strftime("%Y%m%d"),
                ticker
            )
            if path.isfile(file_path):
                res.append(fetch_single_date_data(i, ticker))
        res = pd.concat(res).sort_values('time')
    if transform == True and res is not None:
        res = res[res.suspicious==0]
        temp = res.groupby('time')
        price = temp['price'].mean()
        volume = temp['size'].sum()
        time = temp['time'].first()
        res = pd.DataFrame(
            {'time': time, 'price':price, 'volume': volume}
        )
        res.index=res.time
        return res
    else:
        return res

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

dates=pd.date_range('2017-5-25', '2017-7-30')

hist = []

import matplotlib.pyplot as plt
for i in range(0, len(dates)):
    data = fetch_data(dates[i], 'tvix', True)
    if data is not None:
        hist.append((dates[i], data))
        if len(hist) == 3:
            plot, axe = plt.subplots(1, 3)
            hist[0][1].price.plot(ax=axe[0])
            axe[0].axvline(hist[0][0] + pd.Timedelta('9 hours 30 min'), color='red')
            axe[0].axvline(hist[0][0] + pd.Timedelta('16 hours 0 min'), color='red')
            axe[0].set_title(hist[0][0].strftime("%Y%m%d"))

            hist[1][1].price.plot(ax=axe[1])
            axe[1].axvline(hist[1][0] + pd.Timedelta('9 hours 30 min'), color='red')
            axe[1].axvline(hist[1][0] + pd.Timedelta('16 hours 0 min'), color='red')
            axe[1].set_title(hist[1][0].strftime("%Y%m%d"))

            data.price.plot(ax=axe[2])
            axe[2].axvline(dates[i] + pd.Timedelta('9 hours 30 min'), color='red')
            axe[2].axvline(dates[i] + pd.Timedelta('16 hours 0 min'), color='red')
            axe[2].set_title(dates[i].strftime("%Y%m%d"))

            y_min = np.min([i.price.min() for j, i in hist])
            y_max = np.max([i.price.max() for j, i in hist])

            for i in axe:
                i.set_ylim([y_min, y_max])
            plt.show()
        if len(hist) == 3:
            hist.pop(0)
