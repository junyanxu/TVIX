import pandas as pd
import matplotlib.pyplot as plt

from TVIX.data.data_util import read_data
from TVIX.model.econ import attach_PMI_index

start_date = pd.datetime(2011, 1, 1)
end_date = pd.datetime.today()

tvix = read_data(start_date, end_date, 'tvix')
spy = read_data(start_date, end_date, 'spy')

tvix['return'] = tvix['Close'].diff(1)/tvix['Close'].shift(1)
tvix['date'] = tvix.index
tvix = tvix[tvix['return'] < 2]

spy['return'] = spy['Close'].diff(1)/spy['Close'].shift(1)
spy['date'] = spy.index

comp = pd.merge(tvix[['Close', 'return', 'date']], spy[['Close', 'return', 'date']],
                on='date',
                suffixes=('_tvix', '_sp'))
comp.index= comp.date
comp['ratio'] = -comp['return_sp'] / comp['return_tvix']

comp.loc[((comp['return_sp'] < 0) & (comp['return_tvix'] > 0)) | (comp.ratio < 0.2) , 'ratio'] = 0

comp[['Close_sp', 'ratio']].plot(secondary_y='ratio')
plt.show()

comp.to_csv('~/Desktop/test.csv')
