#!/bin/sh

base_currency=$(ls U*.csv | head -1 | xargs grep -m 1 "^Account Information,Data,Base Currency," | awk -F, '{print $4}' ) #assumes base currency doesnt change

#money going in/out of account
echo date,currency,amount > transfers.csv
for file in U*.csv; do
	grep -h "^Deposits & Withdrawals" "$file" | sed -n '/,Code$/q;p' | grep "^Deposits & Withdrawals,Data," | grep -v "^Deposits & Withdrawals,Data,Total," | awk -F, '{OFS=","; print $4,$3,$6}' >> transfers.csv
done
cat transfers.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > transfers.csv; rm tmp

#trades
echo date,name,amount,balance change > trades.csv
grep -h "^Statement of Funds,Data,Base Currency Summary," U*.csv | awk -F, 'match($6, /(Buy|Sell) ([0-9.-]+) (.*)/, arr){OFS=","; print $5,arr[3],arr[2],$7$8}' | sed 's/ *,/,/g' >> trades.csv
cat trades.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > trades.csv; rm tmp

#realized P/L
echo date,name,realized P/L > realized_PL.csv
grep -h "^Trades,Data,Trade" U*.csv | sed 's/"\(.*\),\(.*\)"/\1\2/g' | awk -F, '($15 && $4!="Forex"){OFS=","; print $7,$6,$15}' >> realized_PL.csv
grep -h "^Forex P/L Details,Data,Forex," U*.csv | sed 's/"\(.*\),\(.*\)"/\1\2/g' | awk -F, '($11 && $5~"^Forex"){OFS=","; print $6,$5,$11}' >> realized_PL.csv
cat realized_PL.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > realized_PL.csv; rm tmp

#commissions
echo date,name,currency,commission > commissions.csv
grep -h "^Commission Details,Data," U*.csv | sed 's/"\(.*\),\(.*\)"/\1\2/g' | awk -F, '($8 && !($3~"Total")){OFS=","; print $6,$5,$4,$8}' >> commissions.csv
cat commissions.csv | (sed -u 1q; sort -t, -k1,1 -s) > tmp; cat tmp > commissions.csv; rm tmp

for file in U*.csv; do
	echo $(echo $file | sed 's/U.*_.*_\(.*\).csv/\1/') $(grep -h "^Net Asset Value,Data,Total" $file | awk -F, '{print $7}') >> tmp
done
sort tmp -o tmp
start_date=$(head -1 tmp | awk '{print $1}')
final_date=$(tail -1 tmp | awk '{print $1}')
final_value=$(tail -1 tmp | awk '{print $2}')
rm tmp

#report
echo Date range: $start_date to $final_date > report
echo Final value: $final_value $base_currency >> report
