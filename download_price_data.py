import sys
import yfinance as yf
import pandas as pd
from datetime import datetime

root='price_data'

ticker=sys.argv[1]
filename=root+'/'+ticker+'.csv'
yahoo_ticker=sys.argv[2]

stock = yf.Ticker(yahoo_ticker)
data = stock.history(period='max', interval="1d", repair=True)
if not data.empty:
    data.index=data.index.strftime('%Y-%m-%d')
    data[['Close']].to_csv(filename, mode='w', header=False, index=True)
