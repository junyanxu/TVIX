from os import path
import pandas as pd

%matplotlib inline

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
    res.time = res.time.apply(lambda x: pd.Timedelta(x, 'ms')) + date
    return res

def fetch_data(dates, ticker):
    if dates.__class__.__name__ == 'datetime':
        file_path = '~/Downloads/942439_csv/{0}/{1}.csv'.format(
            dates.strftime("%Y%m%d"),
            ticker
        )
        if path.exists(file_path):
            return fetch_single_date_data(dates, ticker)
    elif hasattr(dates, '__iter__'):
        res = []
        for i in dates:
            file_path = '/Users/junyan/Downloads/942439_csv/{0}/{1}.csv'.format(
                i.strftime("%Y%m%d"),
                ticker
            )
            if path.isfile(file_path):
                res.append(fetch_single_date_data(i, ticker))
        return pd.concat(res).sort_values('time')

dates = pd.date_range('2017-05-16', '2017-05-20')
res = fetch_data(dates, 'tvix')
res.set_index('time', inplace=True)
res.price.plot()
