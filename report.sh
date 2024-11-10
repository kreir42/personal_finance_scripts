#!/bin/sh
#download price data
tail +2 symbols.csv | awk -F, '{print $1}' | while read ticker; do
	./download_price_data.sh $ticker
done
./env/bin/python report.py
