#!/bin/sh
input_files=$(ls IBKR/*.csv)

base_currency=$(echo $input_files | xargs grep -m 1 "^Account Information,Data,Base Currency," | awk -F, '{print $4}' | head -1) #assumes base currency doesnt change

#setup files
echo date,currency,amount > portfolio/transfers.csv
if [ -e portfolio/manual_transfers.csv ]; then
	tail +2 portfolio/manual_transfers.csv >> portfolio/transfers.csv
else
	echo date,currency,amount > portfolio/manual_transfers.csv
fi
echo symbol,name > portfolio/symbols.csv
if [ -e portfolio/manual_symbols.csv ]; then
	tail +2 portfolio/manual_symbols.csv >> portfolio/symbols.csv
else
	echo symbol,name > portfolio/manual_symbols.csv
fi
echo date,symbol,currency,amount,procceeds,commission > portfolio/trades.csv
if [ -e portfolio/manual_trades.csv ]; then
	tail +2 portfolio/manual_trades.csv >> portfolio/trades.csv
else
	echo date,symbol,currency,amount,procceeds,commission > portfolio/manual_trades.csv
fi
echo date,name,realized P/L > portfolio/realized_PL.csv
if [ -e portfolio/manual_realized_PL.csv ]; then
	tail +2 portfolio/manual_realized_PL.csv >> portfolio/realized_PL.csv
else
	echo date,name,realized P/L > portfolio/manual_realized_PL.csv
fi
echo date,name,currency,commission > portfolio/commissions.csv
if [ -e portfolio/manual_commissions.csv ]; then
	tail +2 portfolio/manual_commissions.csv >> portfolio/commissions.csv
else
	echo date,name,currency,commission > portfolio/manual_commissions.csv
fi

#money going in/out of account
for file in $input_files; do
	grep -h "^Deposits & Withdrawals" "$file" | sed -n '/,Code$/q;p' | grep "^Deposits & Withdrawals,Data," | grep -v "^Deposits & Withdrawals,Data,Total," | awk -F, '{OFS=","; print $4,$3,$6}' >> portfolio/transfers.csv
done
cat portfolio/transfers.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > portfolio/transfers.csv; rm tmp

#symbols
grep -h "^Financial Instrument Information,Data," $input_files | awk -F, '{OFS=","; print $4,$5}' | sort | uniq >> portfolio/symbols.csv

#trades
grep -h "^Trades,Data,Trade," $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '{OFS=","; print $7,$6,$5,$9,$12,$13}' >> portfolio/trades.csv
cat portfolio/trades.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > portfolio/trades.csv; rm tmp

#realized P/L
grep -h "^Trades,Data,Trade" $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '($15 && $4!="Forex"){OFS=","; print $7,$6,$15}' >> portfolio/realized_PL.csv
grep -h "^Forex P/L Details,Data,Forex," $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '($11 && $5~"^Forex"){OFS=","; print $6,$5,$11}' >> portfolio/realized_PL.csv
cat portfolio/realized_PL.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > portfolio/realized_PL.csv; rm tmp

#commissions
grep -h "^Commission Details,Data," $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '($8 && !($3~"Total")){OFS=","; print $6,$5,$4,$8}' >> portfolio/commissions.csv
cat portfolio/commissions.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > portfolio/commissions.csv; rm tmp

for file in $input_files; do
	echo $(echo $file | sed 's/U.*_.*_\(.*\).csv/\1/') $(grep -h "^Net Asset Value,Data,Total" $file | awk -F, '{print $7}') >> tmp
done
sort tmp -o tmp
start_date=$(head -1 tmp | awk '{print $1}' | sed 's/IBKR\///')
final_date=$(tail -1 tmp | awk '{print $1}' | sed 's/IBKR\///')
final_value=$(tail -1 tmp | awk '{print $2}')
rm tmp

#report
echo Date range: $start_date to $final_date > ibkr_report
echo Final value: $final_value $base_currency >> ibkr_report
