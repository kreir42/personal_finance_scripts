monthly = 1000
years_investing = 25
years_holding = 5
portfolio = [("SP500TR",         0.90, 0.08),
             ("gold",            0.10, 0),
             ]
rebalance_threshold = 0.5
rebalance_months = 4


if sum([x for _,x,_ in portfolio])!=1:
    print("ERROR: Portfolio percentages don't add up to 1")
    import sys
    sys.exit()

capital_gains_tax_brackets = [(0, 0.19), (6000, 0.21), (50000, 0.23), (200000, 0.27), (300000, 0.28)]; capital_gains_tax_brackets.reverse()

from datetime import datetime, timezone, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np
import numpy_financial as npf

def capital_gains_taxes(capital_gains):
    if capital_gains<=0:
        return 0
    taxes = 0
    for bracket in capital_gains_tax_brackets:
        if capital_gains > bracket[0]:
            taxes += bracket[1] * (capital_gains-bracket[0])
            capital_gains = bracket[0]
    return taxes

total_years = years_investing + years_holding
months_investing = years_investing*12
months_holding = years_holding*12
total_months = months_investing+months_holding
total_invested = months_investing*monthly
invest_series = [-monthly]*months_investing + [0]*months_holding

def calculate_IRR(final_value):
    try:
        return npf.irr(invest_series+[final_value])
    except:
        return np.nan

#inflation
data = pd.read_csv("price_data/US_cpi.csv", index_col=0, names=['Date','CPI'])
data.index = pd.to_datetime(data.index)
data = data.resample('ME').agg({'CPI': 'last',}).dropna()
final_cpi = data['CPI'].iloc[-1]
data['Inflation'] = (pow(data['CPI'].pct_change()+1,12)-1)*100
data['Inflation adjustment'] = final_cpi/data['CPI']

data['LS yearly return'] = 0
for name,weight,expense_ratio in portfolio:
    if weight==0:
        continue
    data_tmp = pd.read_csv(f"price_data/{name}.csv", index_col=0,
                names=['Date',name], usecols = ['Date',name])
    data_tmp.index = pd.to_datetime(data_tmp.index, format='ISO8601')
    data_tmp = data_tmp.resample('ME').agg({name: 'mean',})
    data_tmp = data_tmp.dropna()
    data_tmp[name] = data_tmp[name]*data['Inflation adjustment']
    data['LS yearly return'] += weight*data_tmp[name]/data_tmp[name].shift(total_months)
    data = pd.merge(data, data_tmp, on='Date', how='inner')
    data[f"{name}_shares"] = 0
    data[f"{name}_value"] = 0
data['LS yearly return'] = (pow(data['LS yearly return'], 1/total_years)-1)*100

remaining_monthly = pd.DataFrame(0,index=data.index,columns=[''])
data['Rebalancing times'] = 0
data['Rebalancing taxes'] = 0

def rebalance_function(row):
    to_rebalance=False
    portfolio_weights = {}
    for name,weight,expense_ratio in portfolio:
        if weight==0:
            continue
        portfolio_weights[name] = row[f"{name}_value"] / row['total_value']
        if abs(portfolio_weights[name]/weight-1) >= rebalance_threshold:
            to_rebalance=True
    if to_rebalance:
        row['Rebalancing times'] += 1
        taxes_today = 0
        for name,weight,expense_ratio in portfolio:
            if weight==0:
                continue
            change = row[f"{name}_value"]-row['total_value']*weight
            row[f"{name}_value"] -= change
            row[f"{name}_shares"] = row[f"{name}_value"]/row[name]
            taxes_today += capital_gains_taxes((row[f"{name}_value"]-weight*monthly*(i+1))*(portfolio_weights[name]-weight))
        row['Rebalancing taxes'] += taxes_today
        row['total_value'] -= taxes_today
        for name,weight,expense_ratio in portfolio:
            if weight==0:
                continue
            row[f"{name}_value"] = row['total_value']*weight
            row[f"{name}_shares"] = row[f"{name}_value"]/row[name]
    return row

for i in range(total_months):
    data['total_value'] = 0
    for name,weight,expense_ratio in portfolio:
        if weight==0:
            continue
        data[f"{name}_shares"] *= pow(1 - expense_ratio/100, 1/12)
        data[f"{name}_value"] = data[f"{name}_shares"] * data[name]
        data['total_value'] += data[f"{name}_value"]
    #investment
    if i<months_investing:
        remaining_monthly = monthly
        data['total_value'] += monthly
        for name,weight,expense_ratio in portfolio:
            if weight==0:
                continue
            difference = data['total_value']*weight - data[f"{name}_value"]
            difference = np.where(difference > 0,
                      np.where(difference > remaining_monthly, remaining_monthly, difference),
                      0)
            remaining_monthly -= difference
            data[f"{name}_shares"] += difference/data[name]
            data[f"{name}_value"] = data[f"{name}_shares"] * data[name]
        data['total_value'] = 0
        for name,weight,expense_ratio in portfolio:
            if weight==0:
                continue
            data['total_value'] += data[f"{name}_value"]
    #rebalancing
    if rebalance_months>0 and i%rebalance_months==0:
        data = data.apply(rebalance_function, axis=1)
    for name,weight,expense_ratio in portfolio:
        if weight==0:
            continue
        data[f"{name}_shares"] = data[f"{name}_shares"].shift(1)
        data[f"{name}_value"] = data[f"{name}_value"].shift(1)
    data['Rebalancing taxes'] = data['Rebalancing taxes'].shift(1)
    data['Rebalancing times'] = data['Rebalancing times'].shift(1)
data['IRR'] = data['total_value'].apply(calculate_IRR)
data['IRR'] = (pow(data['IRR']+1,12)-1)*100
IRR_mean = data['IRR'].mean()
IRR_stddev = data['IRR'].std()
rebalancing_times_mean = data['Rebalancing times'].mean()
rebalancing_times_stddev = data['Rebalancing times'].std()



##############################
#           PLOTS
##############################


plt.plot(data.index, data['Inflation'], label='Raw', linewidth=0.5)
plt.plot(data.index, data['Inflation'].rolling(center=True, window=12).mean(), label='Smoothed 1 year')
plt.plot(data.index, data['Inflation'].rolling(center=True, window=36).mean(), label='Smoothed 3 years')
plt.axhline(data['Inflation'].mean(), linestyle='-.', label='Mean')
plt.title('Inflation over time')
plt.xlabel('Date')
plt.ylabel('Yearly inflation (%)')
plt.legend()
plt.grid(True)
plt.show()

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(data.index, data['IRR'].shift(-total_months), label='IRR')
ax1.axhline(IRR_mean, linestyle=':', label='IRR mean')
ax1.plot(data.index, data['LS yearly return'].shift(-total_months), label='LS', linewidth=0.85)
for name,weight,expense_ratio in portfolio:
    if weight==0:
        continue
    ax2.plot(data.index, data[name], linestyle='--', linewidth=0.5, label=f"{name} price")
ax1.plot(data.index, data['Rebalancing taxes'].shift(-total_months)/total_invested*100, label='Rebalancing taxes percentage', linewidth=0.85)
fig.tight_layout()
ax1.set_xlabel('Date started')
ax1.set_ylabel('Annual return (%)')
ax2.set_ylabel('Price ($)')
plt.title('Annual returns over year started')
fig.legend()
ax1.grid(True)
plt.show()

plt.hist(data['IRR'], bins=50, density=True)
plt.axvline(IRR_mean)
plt.axvline(IRR_mean+IRR_stddev, linestyle=':')
plt.axvline(IRR_mean-IRR_stddev, linestyle=':')
plt.title('Frequency Distribution of IRR')
plt.xlabel('IRR (%)')
plt.ylabel('Density')
plt.show()

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.plot(data.index, data['total_value'].shift(-total_months), label='Final value')
ax1.plot(data.index, data['Rebalancing taxes'].shift(-total_months), label='Rebalancing taxes')
ax1.axhline(total_invested, linestyle='-', color='red', label='Total invested')
for name,weight,expense_ratio in portfolio:
    if weight==0:
        continue
    ax2.plot(data.index, data[name], linestyle='--', linewidth=0.5, label=f"{name} price")
fig.tight_layout()
ax1.set_xlabel('Date started')
ax1.set_ylabel('Value ($)')
ax2.set_ylabel('Price ($)')
plt.title('Final investment value over year started')
fig.legend()
ax1.grid(True)
plt.show()

plt.plot(data.index, data['Rebalancing times'].shift(-total_months), label='Rebalancing times')
plt.axhline(rebalancing_times_mean, linestyle='-.', label='Mean')
plt.title('Rebalancing times')
plt.xlabel('Date')
plt.ylabel('Times')
plt.legend()
plt.grid(True)
plt.show()

######################

print(f"Mean rebalancing times:   {round(rebalancing_times_mean,2)} +- {round(rebalancing_times_stddev,2)}")
print(f"Mean LS annual return:   ({round(data['LS yearly return'].mean(),2)} +- {round(data['LS yearly return'].std(),2)})%")
print(f"Mean IRR:                ({round(IRR_mean,2)} +- {round(IRR_stddev,2)})%")
print(f"Total invested over {years_investing}+{years_holding} = {total_years} years: {total_invested}")
