from datetime import datetime
import pandas as pd
import pandas_datareader.data as web

ticker = 'INDEXCBOE:VIX'
data_source = 'google'
start_date = datetime(2000,1,1)
end_date = datetime(2017, 6, 26)
f = web.DataReader(ticker, data_source, start_date, end_date)
print(f)
