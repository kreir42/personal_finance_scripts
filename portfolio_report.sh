#!/bin/sh
mkdir -p portfolio
#download price data
tail +2 portfolio/symbols.csv | awk -F, '{print $1}' | while read ticker; do
	./download_price_data.sh $ticker
done
./env/bin/python portfolio_report.py
