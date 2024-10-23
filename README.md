# Personal finance scripts
Collection of small scripts for personal finance.
Configure them by modifying their source code.

## budget.py
Plots pie charts and breaks down the monthly spending percentages for a budget.

## rent_or_buy.py
Compares buying a home with a mortgage vs renting.
The first plot shows the monthly cost of each option over time.
The second plot shows the extra value of an investment portfolio, where every year the option with the lower cost is investing the difference (the highest cost minus its own).
This assumes all options are always affordable.

## DCA_backtesting.py
Backtests Dollar Costs Averaging a constant inflation-adjusted amount over time (plus a 'hold' time with no contributions) into a portfolio given historical data.
Price and inflation data are located in the price_data folder in csv format. Price data must not be inflation adjusted.

## investment_needs.py
Shows the required monthly investment to achieve a certain portfolio value depending on the time and the annual returns.
