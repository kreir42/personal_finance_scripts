base_currency = 'EUR'
base_currency_symbol = '€'
cpi_filename = 'EU_cpi.csv'
benchmark_symbol = 'IMID'
IRR_plot_skip_days = 60

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
df['Raw net flow'] = 0.0
df['Net flow'] = 0.0
df['Benchmark amount'] = 0.0
df['Benchmark value'] = 0.0

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
#process transfers and calculate net flow of money (money in minus out)
for date, row in transfers.iterrows():
    currency = row['currency']
    if currency==base_currency:
        money = row['amount']
    else:
        money = row['amount'] * df[currency+'_price']
    df.loc[date:, currency] += row['amount']
    df.loc[date:, 'Raw net flow'] += money
    df.loc[date:, 'Net flow'] += money * df.loc[date, 'Inflation adjustment']
    df.loc[date:, 'Benchmark amount'] += money / df.loc[date, benchmark_symbol+'_price']
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
df['Benchmark value'] = df['Benchmark amount'] * df[benchmark_symbol+'_price'] * df['Inflation adjustment']
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
df['Benchmark IRR'] = 0.0
df['IRR'] = 0.0
daily_transfers = transfers.groupby(transfers.index)['amount'].sum()
#join the sums to the main df and calculate the inflation-adjusted value
df['adjusted_transfer'] = df.join(daily_transfers, how='left').fillna(0)['amount'] * df['Inflation adjustment']
transfers_array = []
for date, row in df.iterrows():
    transfers_array.append(row['adjusted_transfer'])
    df.loc[date, 'Benchmark IRR'] = calculate_IRR(df.loc[date, 'Benchmark value'], transfers_array)
    df.loc[date, 'IRR'] = calculate_IRR(df.loc[date, 'value'], transfers_array)
df['Benchmark IRR'] = (pow(df['Benchmark IRR']+1,365.24)-1)*100 #go from daily to yearly percentage
df['IRR'] = (pow(df['IRR']+1,365.24)-1)*100 #go from daily to yearly percentage

print(df)
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
df_subset = df.iloc[IRR_plot_skip_days:]
ax1.plot(df_subset.index, df_subset['IRR'], label='IRR', color='blue')
#ax1.plot(df_subset.index, df_subset['IRR'].rolling(window=30).mean(), label='30-day average', linestyle='--', linewidth=0.8, color='blue')
ax1.plot(df_subset.index, df_subset['Benchmark IRR'], label='Benchmark ('+benchmark_symbol+') IRR', linewidth=0.8, color='green')
ax2.plot(df.index, df['value'], label='Value', color='black', linestyle='--', linewidth=0.85)
ax2.plot(df.index, df['Benchmark value'], label='Benchmark ('+benchmark_symbol+') value', linestyle='--', linewidth=0.85, color='green')
plt.tight_layout()
ax1.set_xlabel('Date')
ax1.set_ylabel('IRR (%)')
ax2.set_ylabel(f"Value ({base_currency})")
ax1.grid(True)
fig.legend()
plt.show()

total_commissions = 0
total_commissions_raw = 0
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
            currency_equivalence = df.loc[date, row['currency']+'_price']
            money_flow.loc[date, 'value'] *= currency_equivalence
            total_commissions_raw += row['commission'] * currency_equivalence
            total_commissions += row['commission']*df.loc[date, 'Inflation adjustment'] * currency_equivalence
        else:
            total_commissions_raw += row['commission']
            total_commissions += row['commission']*df.loc[date, 'Inflation adjustment']
    IRR = calculate_IRR(df[symbol].iat[-1]*df[symbol+'_price'].iat[-1], money_flow['value'])
    IRR = (pow(IRR+1,365.24)-1)*100 #go from daily to yearly percentage
    print(f"    {symbol}: {IRR:.2f}%")
print()
print()
current_value = df['value'].iat[-1]
print(f"Current value:   {current_value:.2f}"+base_currency_symbol)
print(f"Net flow:        {-df['Raw net flow'].iat[-1]:.2f}"+base_currency_symbol+f"     -->     Inflation adjusted: {-df['Net flow'].iat[-1]:.2f}"+base_currency_symbol)
print(f"Current P&L:     {current_value-df['Raw net flow'].iat[-1]:.2f}"+base_currency_symbol+f"     -->     Inflation adjusted: {current_value-df['Net flow'].iat[-1]:.2f}"+base_currency_symbol)
print(f"Total fees paid: {-total_commissions_raw:.2f}"+base_currency_symbol+f"     -->     Inflation adjusted: {-total_commissions:.2f}"+base_currency_symbol)
