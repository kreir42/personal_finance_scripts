#!/bin/sh
yahoo_symbol=$(grep ^"$1" yahoo_symbols.csv | awk -F, '{print $2}')
if [ -z "$yahoo_symbol" ];then
	yahoo_symbol="$1"
fi
./env/bin/python download_price_data.py "$1" "$yahoo_symbol"
currency_conversion=$(grep ^"$1" price_data/currency_conversion.csv | awk -F, '{print $2}')
if [ "$currency_conversion" ];then
	./env/bin/python convert_price_data.py "$1" "$currency_conversion"
fi
