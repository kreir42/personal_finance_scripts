base_currency = 'EUR'
cpi_filename = 'EU_cpi.csv'

from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np
import numpy_financial as npf
import re

def calculate_IRR(final_value, invest_series):
    try:
        copy = np.array(invest_series)
        copy *= -1
        copy[-1] += final_value
        return npf.irr(copy)
    except:
        return np.nan

transfers = pd.read_csv("portfolio/transfers.csv", index_col=0, header=0, parse_dates=True)
trades = pd.read_csv("portfolio/trades.csv", index_col=0, header=0, parse_dates=True)

start_date = transfers.index[0]
now = datetime.now()
date_range = pd.date_range(start=start_date, end=now, freq='D')
df = pd.DataFrame(index=date_range)

#inflation
cpi = pd.read_csv("price_data/"+cpi_filename, index_col=0, names=['Date','CPI'], parse_dates=True)
cpi = cpi.loc[start_date-timedelta(days=30):]
cpi = cpi.resample('D').agg({'CPI': 'last',})
cpi = cpi.interpolate(method='linear')
final_cpi = cpi['CPI'].iloc[-1]

df['CPI'] = cpi['CPI']
df['CPI'] = df['CPI'].ffill()
df['Inflation adjustment'] = final_cpi/df['CPI']

df[base_currency] = 0.0

#make one column per symbol and get prices in base_currency
currencies = trades['currency'].unique()
for symbol in currencies:
    if symbol==base_currency:
        continue
    df[symbol] = 0.0
    tmp = pd.read_csv('price_data/'+symbol+'.csv', index_col=0, names=['date','price'], parse_dates=True)
    df[symbol+'_price'] = tmp['price']
    df[symbol+'_price'] = df[symbol+'_price'].ffill().fillna(0)
symbols = []
for symbol in trades['symbol'].unique():
    match = re.match(r"^(\w+)\.(\w+)$", symbol)
    if match and (match.group(1) and match.group(2) in currencies):
        continue
    symbols.append(symbol)
    df[symbol] = 0.0
    tmp = pd.read_csv('price_data/'+symbol+'.csv', index_col=0, names=['date','price'], parse_dates=True)
    df[symbol+'_price'] = tmp['price']
    df[symbol+'_price'] = df[symbol+'_price'].ffill().fillna(0)
#transfers
for date, row in transfers.iterrows():
    df.loc[date:, row['currency']] += row['amount']
#get number of shares over time
for date, row in trades.iterrows():
    symbol = row['symbol']
    match = re.match(r"^(\w+)\.(\w+)$", symbol)
    if match and (match.group(1) and match.group(2) in currencies):
        if match.group(1)==row['currency']:
            symbol = match.group(2)
        elif match.group(2)==row['currency']:
            symbol = match.group(1)
    df.loc[date:, symbol] += row['amount']
    df.loc[date:, row['currency']] += row['procceeds']+row['commission']
#calculate value
df['value'] = df[base_currency]
for symbol in currencies:
    if symbol==base_currency:
        continue
    df['value'] += df[symbol]*df[symbol+'_price']
for symbol in symbols:
    df['value'] += df[symbol]*df[symbol+'_price']
#adjust value for inflation
df['value'] *= df['Inflation adjustment']

#calculate IRR
df['IRR'] = 0.0
transfers_array = []
for date, row in df.iterrows():
    try:
        transfers_array.append(transfers.loc[date, 'amount']*df.loc[date, 'Inflation adjustment'])
    except:
        transfers_array.append(0)
    df.loc[date, 'IRR'] = calculate_IRR(df.loc[date, 'value'], transfers_array)
df['IRR'] = (pow(df['IRR']+1,365.24)-1)*100 #go from daily to yearly percentage

print(df)
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(df.index, df['IRR'], label='IRR', color='blue')
ax1.plot(df.index, df['IRR'].rolling(window=30).mean(), label='30-day average', linestyle='--', linewidth=0.8, color='blue')
ax2.plot(df.index, df['value'], label='Value', color='black', linestyle='--', linewidth=0.85)
plt.tight_layout()
ax1.set_xlabel('Date')
ax1.set_ylabel('IRR (%)')
ax2.set_ylabel(f"Value ({base_currency})")
ax1.grid(True)
fig.legend()
plt.show()

#Report IRR per symbol
print()
print('IRR per symbol:')
for symbol in symbols:
    money_flow = pd.DataFrame(index=date_range)
    money_flow['value'] = 0.0
    for index, row in trades.iterrows():
        date = pd.to_datetime(index).floor('D')
        if row['symbol']!=symbol:
            continue
        money_flow.loc[date, 'value'] -= row['procceeds']+row['commission']*df.loc[date, 'Inflation adjustment']
        if row['currency']!=base_currency:
            money_flow.loc[date, 'value'] *= df.loc[date, row['currency']+'_price']
    IRR = calculate_IRR(df[symbol].iat[-1]*df[symbol+'_price'].iat[-1], money_flow['value'])
    IRR = (pow(IRR+1,365.24)-1)*100 #go from daily to yearly percentage
    print(f"    {symbol}: {IRR:.2f}%")
