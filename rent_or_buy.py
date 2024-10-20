investment_returns = 6 #yearly percentage, after inflation
sim_time = 50 #years

#RENT
rent = 2000 #monthly
rent_increase = 3 #yearly percentage, after inflation

#BUY
home_value = 0.5E6
buying_fees = 10000 #one-time payment
mortgage_fees = 10000 # one-time payment
down_payment = 1E5
mortgage_time = 20 #years
mortgage_interest_rate = 4 #yearly percentage
property_taxes = 1 #yearly percentage
home_insurance = 1000 #yearly
home_maintenance = 5000 #yearly
hoa_fees = 100 #monthly
home_appreciation = 2 #yearly percentage, after inflation

###############################################################

investment_returns/=100
rent_increase/=100
mortgage_interest_rate/=100
property_taxes/=100
home_appreciation/=100

mortgage_principal = home_value+buying_fees+mortgage_fees-down_payment
mortgage_payments_number = mortgage_time*12
mortgage_monthly_interest_rate = mortgage_interest_rate/12
mortgage_payment = mortgage_principal*(mortgage_monthly_interest_rate*(1+mortgage_monthly_interest_rate)**mortgage_payments_number)/((1+mortgage_monthly_interest_rate)**mortgage_payments_number-1)

###############################################################
x=range(0,sim_time+1)

owning_cost=[property_taxes*home_value*(1+home_appreciation)**t+home_insurance+home_maintenance+hoa_fees*12 for t in x]
buy_cost=[mortgage_payment*12+owning if t<=mortgage_time else owning for t,owning in zip(x,owning_cost)]
rent_cost=[12*rent*(1+rent_increase)**t for t in x]
owning_cost=[t/12 for t in owning_cost]
buy_cost=[t/12 for t in buy_cost]
rent_cost=[t/12 for t in rent_cost]
higher_cost=[max(r,b) for r,b in zip(rent_cost,buy_cost)]

buy_value=[0 for t in x]
rent_value=[0 for t in x]
buy_value[0] = home_value
rent_value[0] = down_payment
rentbuycash_year=0
rentbuycash_cost=[0 for t in x]
rentbuycash_cost[0]=rent_cost[0]
rentbuycash_value=[0 for t in x]
rentbuycash_value[0] = down_payment
for i in range(1,sim_time+1):
    buy_value[i] = (buy_value[i-1]-home_value)*(1+investment_returns) + home_value
    rent_value[i] = rent_value[i-1]*(1+investment_returns)
    if buy_cost[i]<higher_cost[i]:
        buy_value[i] += 12*(higher_cost[i]-buy_cost[i])
    if rent_cost[i]<higher_cost[i]:
        rent_value[i] += 12*(higher_cost[i]-rent_cost[i])
    if rentbuycash_year==0 and rent_value[i] >= home_value+buying_fees:
        rentbuycash_year = i
for i in range(1,sim_time+1):
    if i<rentbuycash_year:
        rentbuycash_cost[i] = rent_cost[i]
        rentbuycash_value[i] = rent_value[i]
    elif i==rentbuycash_year:
        rentbuycash_cost[i] = owning_cost[i]
        rentbuycash_value[i] = rent_value[i]-home_value-buying_fees
    else:
        rentbuycash_cost[i] = owning_cost[i]
        rentbuycash_value[i] = rentbuycash_value[i-1]*(1+investment_returns)
        if owning_cost[i]<higher_cost[i]:
            rentbuycash_value[i] += 12*(higher_cost[i]-owning_cost[i])
buy_value_liquid=[t-home_value for t in buy_value]


###############################################################
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
fig = plt.figure()
gs = gridspec.GridSpec(2, 4, figure=fig)
ax_cost = fig.add_subplot(gs[0, :])
ax_value = fig.add_subplot(gs[1, :], sharex=ax_cost)

#cost over time
ax_cost.plot(x, buy_cost, label='Buying')
ax_cost.plot(x, rent_cost, label='Renting')
ax_cost.plot(x, rentbuycash_cost, label='Renting, then buying in cash')
ax_cost.plot(x, owning_cost, label='Owning', linestyle='--', linewidth=0.8, color='blue')
ax_cost.set_ylabel('Monthly cost')
ax_cost.set_xlabel('Time (years)')
ax_cost.grid(True)
ax_cost.legend()

#money over time
ax_value.plot(x, buy_value_liquid, label='Buying')
ax_value.plot(x, buy_value, label='Buying including home value', linestyle='--', linewidth=0.8, color='blue')
ax_value.plot(x, rent_value, label='Renting')
ax_value.plot(x, rentbuycash_value, label='Renting, then buying cash')
ax_value.set_ylabel('Money')
ax_value.set_xlabel('Time (years)')
ax_value.grid(True)
ax_value.legend()

plt.show()

###############################################################

print(f"Mortgage payment = {mortgage_payment:.2f}")
print()
print(f"At first:")
print(f"   Owning cost = {owning_cost[0]:.2f}")
print()
print(f"After {sim_time} years:")
print(f"   Rent          = {rent_cost[-1]:.2f}")
print(f"   House cost    = {buy_cost[-1]:.2f}")
print(f"   Renting value = {rent_value[-1]:.2f}")
print(f"   Buying value  = {buy_value[-1]:.2f}")
print(f"   Renting->Buying value = {rentbuycash_value[-1]:.2f}")
