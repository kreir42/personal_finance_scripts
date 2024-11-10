#!/bin/sh
input_files=$(ls IBKR/*.csv)

base_currency=$(echo $input_files | xargs grep -m 1 "^Account Information,Data,Base Currency," | awk -F, '{print $4}' | head -1) #assumes base currency doesnt change

#money going in/out of account
echo date,currency,amount > transfers.csv
for file in $input_files; do
	grep -h "^Deposits & Withdrawals" "$file" | sed -n '/,Code$/q;p' | grep "^Deposits & Withdrawals,Data," | grep -v "^Deposits & Withdrawals,Data,Total," | awk -F, '{OFS=","; print $4,$3,$6}' >> transfers.csv
done
cat transfers.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > transfers.csv; rm tmp

#symbols
echo symbol,name > symbols.csv
grep -h "^Financial Instrument Information,Data," $input_files | awk -F, '{OFS=","; print $4,$5}' | sort | uniq >> symbols.csv

#trades
echo date,symbol,currency,amount,procceeds,commission > trades.csv
grep -h "^Trades,Data,Trade," $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '{OFS=","; print $7,$6,$5,$9,$12,$13}' >> trades.csv
cat trades.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > trades.csv; rm tmp

#realized P/L
echo date,name,realized P/L > realized_PL.csv
grep -h "^Trades,Data,Trade" $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '($15 && $4!="Forex"){OFS=","; print $7,$6,$15}' >> realized_PL.csv
grep -h "^Forex P/L Details,Data,Forex," $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '($11 && $5~"^Forex"){OFS=","; print $6,$5,$11}' >> realized_PL.csv
cat realized_PL.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > realized_PL.csv; rm tmp

#commissions
echo date,name,currency,commission > commissions.csv
grep -h "^Commission Details,Data," $input_files | sed 's/"\([^,]*\),\([^,]*\)"/\1\2/g' | awk -F, '($8 && !($3~"Total")){OFS=","; print $6,$5,$4,$8}' >> commissions.csv
cat commissions.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > commissions.csv; rm tmp

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
