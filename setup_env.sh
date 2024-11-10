#!/bin/sh
rm -rf env/
python -m venv env/
./env/bin/pip install matplotlib pandas numpy numpy-financial yfinance scipy
