import sys
import pandas as pd
from datetime import datetime

root='price_data'

ticker=sys.argv[1]
filename=root+'/'+ticker+'.csv'
currency=sys.argv[2]
currency_filename=root+'/'+currency+'.csv'

currency_data = pd.read_csv(currency_filename, index_col=0, names=['date','price'], parse_dates=True)
ticker_data = pd.read_csv(filename, index_col=0, names=['date','price'], parse_dates=True)
ticker_data['price'] *= currency_data['price']
ticker_data.to_csv(filename, mode='w', header=False, index=True)
