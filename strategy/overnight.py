import pandas as pd
import matplotlib.pyplot as plt

from TVIX.data.data_util import read_data
from TVIX.model.econ import attach_PMI_index

start_date = pd.datetime(2011, 1, 1)
end_date = pd.datetime.today()
holding_period = 10

tvix = read_data(start_date, end_date, 'tvix')
vix = read_data(start_date, end_date, 'vix')
tvix['date'] = tvix.index
vix['date'] = vix.index
tvix['tvix_last_return'] = tvix['Close'].diff(1)/tvix['Close'].shift(1)
tvix['tvix_return'] = tvix['Close'].diff(1).shift(-1)/tvix['Close']
tvix['tvix_return_next'] = ((tvix.Close - tvix.Open)/tvix.Open).shift(-1)

tvix['overnight_return'] = (tvix['Open'].shift(-1) - tvix.Close)/tvix.Close
tvix = tvix[tvix.overnight_return.abs() < 2]

comp = pd.merge(tvix, vix, left_on='date', right_on='date')

comp.columns


comp['overnight_cumsum'] = comp['overnight_return'].cumsum()
comp['overnight_return_next'] = comp['overnight_return'].shift(-1)
comp.index=comp.date
# comp.overnight_cumsum.plot()

plt.scatter(comp['overnight_return'], comp['over'])
plt.show()
