from datetime import datetime
from pandas_datareader import data as web
import pandas as pd
import re
import quandl

QUANDL_API_KEY = 'AJH1cx5c8ZxqTrtaZXHr'
quandl.ApiConfig.api_key = 'AJH1cx5c8ZxqTrtaZXHr'

def get_first_business_of_month(dates):
    from pandas.tseries.offsets import BDay
    return dates - BDay() + BDay()

def fetch_OHLC_cols(columns):
    OHLCV_map = dict()
    OHLCV = ['Open', 'High', 'Low', 'Close', 'Volume']
    for i in OHLCV:
        regex = re.compile(i+'$', re.IGNORECASE)
        for j in columns:
            if j == 'Last':
                OHLCV_map[j] = 'Close'
            if regex.search(j):
                OHLCV_map[j] = i
    return OHLCV_map


def read_data_from_google(start_date, end_date, ticker):
    data_source = 'google'
    f = web.DataReader(ticker, data_source, start_date, end_date)
    cols_to_keep = ['Open', 'High', 'Low', 'Close']
    if 'Volume' in set(f.columns):
        cols_to_keep += ['Volume']
    return f[cols_to_keep]


def read_data_from_quandl(start_date, end_date, ticker):
    mydata = quandl.get(ticker, start_date=start_date, end_date=end_date)
    OHLCV_map = fetch_OHLC_cols(mydata.columns)
    mydata.rename(columns=OHLCV_map, inplace=True)
    return mydata[OHLCV_map.values()]

def read_econ_data_from_quandl(start_date, end_date, ticker, dates_transform=get_first_business_of_month):
    mydata = quandl.get(ticker, start_date=start_date, end_date=end_date)
    if dates_transform:
        mydata.index = dates_transform(mydata.index)
    return mydata


data_ticker_hash = {
    'sp500':'CHRIS/CME_SP1',
    'SP500':'CHRIS/CME_SP1',
    'sp':'CHRIS/CME_SP1',
    'SP':'CHRIS/CME_SP1',
    'tvix':'TVIX',
    'VIX':'CBOE/VIX',
    'vix':'CBOE/VIX',
    'CL':'CHRIS/CME_CL1',
    'oil':'CHRIS/CME_CL1',
    'pmi':'ISM/MAN_PMI',
    'PMI':'ISM/MAN_PMI',
}

data_process_hash = {
    'TVIX':read_data_from_google,
    'CBOE/VIX':read_data_from_quandl,
    'CHRIS/CME_SP1':read_data_from_quandl,
    'CHRIS/CME_CL1':read_data_from_quandl,
    'ISM/MAN_PMI':read_econ_data_from_quandl,
}


def read_data(start_date, end_date, ticker):
    if data_ticker_hash.has_key(ticker):
        ticker_for_download = data_ticker_hash[ticker]
    else:
        ticker_for_download = ticker
    if data_process_hash.has_key(ticker_for_download):
        return data_process_hash[ticker_for_download](
            start_date, end_date, ticker_for_download)
    else:
        return read_data_from_google(start_date, end_date, ticker_for_download)


if __name__ == '__main__':
    start_date = datetime(2010, 1, 1)
    end_date = datetime.today()
    print(read_data(start_date, end_date, 'tvix'))
