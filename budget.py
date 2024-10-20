yearly_salary = 25000
yearly_capital_gains = 1000

#EXPENSES
bus_trip = 1.25
milk = 0.8
cookies = 2
bread = 1.15/16
butter = 2
breakfast = 0.25*milk + 2*bread + butter/50
snack = 0.25*milk + 2*cookies/20
other_meal = 4
dessert = 0.20
daily_food_budget = breakfast + 2*other_meal + snack + 2*dessert

                   #(qty,                   name,                   category)
monthly_expenses = [(800,                   'Rent',                 'Rent'),
                    (5*2*bus_trip,          'Bus',                  'Miscellaneous'),
                    (70,                    'Electricity',          'Utilities'),
                    (20,                    'Water',                'Utilities'),
                    (30,                    'Gas',                  'Utilities'),
                    (50,                    'Internet',             'Utilities'),
                    (20,                    'Phone',                'Utilities'),
                    (40,                    'Eating out',           'BS'),
                    (80,                    'Candles',              'BS'),
                    ]
yearly_expenses =  [(150,                   'Videogames',           'BS'),
                    (60,                    'Dentist checkup',      'Miscellaneous'),
                    ]
daily_expenses =   [(breakfast,             'Breakfast',            'Food'),
                    (snack,                 'Snack',                'Food'),
                    (other_meal*2,          'Lunch & Dinner',       'Food'),
                    (dessert*2,             'Dessert',              'Food'),
                    ]

#TAX BRACKETS
salary_tax_brackets = [(0, 0.19), (12450, 0.24), (20200, 0.3), (35200, 0.37), (60000, 0.45), (300000, 0.47)]; salary_tax_brackets.reverse()
capital_gains_tax_brackets = [(0, 0.19), (6000, 0.21), (50000, 0.23), (200000, 0.27), (300000, 0.28)]; capital_gains_tax_brackets.reverse()

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import defaultdict
import numpy as np
import math

def salary_taxes(salary):
    taxes = 0
    for bracket in salary_tax_brackets:
        if salary > bracket[0]:
            taxes += bracket[1] * (salary-bracket[0])
            salary = bracket[0]
    return taxes
def capital_gains_taxes(capital_gains):
    taxes = 0
    for bracket in capital_gains_tax_brackets:
        if capital_gains > bracket[0]:
            taxes += bracket[1] * (capital_gains-bracket[0])
            capital_gains = bracket[0]
    return taxes

monthly_IRPF = salary_taxes(yearly_salary)/12 + capital_gains_taxes(yearly_capital_gains)/12
monthly_income = (yearly_salary+yearly_capital_gains)/12 - monthly_IRPF
category_totals = defaultdict(float)
name_totals = defaultdict(float)
total_monthly_expenses = 0

yearly_type_total = 0
for amount, name, category in yearly_expenses:
    amount /= 12
    monthly_expenses.append((amount, name, category))
    yearly_type_total += amount

daily_type_total = 0
for amount, name, category in daily_expenses:
    amount *= 30
    monthly_expenses.append((amount, name, category))
    daily_type_total += amount

for amount, name, category in monthly_expenses:
    total_monthly_expenses += amount
    category_totals[category] += amount
    name_totals[name] += amount

monthly_discretionary_income = 0
if total_monthly_expenses < monthly_income:
    monthly_discretionary_income = monthly_income - total_monthly_expenses

#
#   PLOT
#
def pie_format_function(x):
    return '{:.2f}%\n{:.2f}€'.format(x, pie_format_number*x/100)
categories = list(category_totals.keys())
expenses = list(category_totals.values())
if monthly_discretionary_income > 0:
    categories += ['Discretionary income']
    expenses += [monthly_discretionary_income]
fig = plt.figure()
gs = gridspec.GridSpec(3, 5, figure=fig)
ax_main = fig.add_subplot(gs[:, :4])
pie_format_number = monthly_income
ax_main.pie(expenses, labels=categories, autopct=pie_format_function, pctdistance=0.9, startangle=90)
ax_main.set_title('Income by category')
ax1 = fig.add_subplot(gs[0, -1])  #top-right
if monthly_discretionary_income > 0:
    pie_format_number = yearly_salary/12
    ax1.pie([total_monthly_expenses, monthly_IRPF, monthly_discretionary_income], labels=['Expenses', 'IRPF', 'Discretionary income'], autopct=pie_format_function, startangle=90)
else:
    pie_format_number = total_monthly_expenses
    ax1.pie([total_monthly_expenses, monthly_IRPF], labels=['Expenses', 'IRPF'], autopct=pie_format_function, startangle=90)
ax1.set_title('Raw income')
pie_format_number = category_totals['BS']
if pie_format_number > 0:
    ax2 = fig.add_subplot(gs[1, -1])  #middle-right
    ax2.pie([x for x,_,y in monthly_expenses if y=='BS'], labels=[x for _,x,y in monthly_expenses if y=='BS'], autopct=pie_format_function, startangle=90, pctdistance=0.7)
    ax2.set_title('BS')
pie_format_number = total_monthly_expenses
ax2 = fig.add_subplot(gs[-1, -1])  #bottom-right
ax2.pie([yearly_type_total, total_monthly_expenses-yearly_type_total-daily_type_total, daily_type_total], labels=['Yearly','Monthly','Daily'], autopct=pie_format_function, startangle=90, pctdistance=0.7)
ax2.set_title('Expense budget types')
plt.show()


#pie_size = 0.5
#fig, ax = plt.subplots()
#ax.pie(outer_expenses, radius=1, labels=categories, autopct=pie_format_function, startangle=90, wedgeprops=dict(width=pie_size, edgecolor='w'))
#inner_wedges, _, _ = ax.pie(inner_expenses, radius=1-pie_size, autopct=pie_format_function, startangle=90, wedgeprops=dict(width=pie_size, edgecolor='w'))

#
#   TEXT REPORT
#
print()
print("Food")
print(f"Breakfast    =  {breakfast:.2f}€")
print(f"Snack        =  {snack:.2f}€")
print(f"Lunch/dinner =  {other_meal:.2f}€")
print(f"Dessert      =  {dessert:.2f}€")
print()
print(f"Daily = {daily_food_budget:.2f}€")
print()
print("-------------------------------")
print()
monthly_expenses.sort(key=lambda x: x[0], reverse=True)
category_totals = dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))
for tree_category in category_totals.keys():
    print(f"{tree_category}: {category_totals[tree_category]:.2f}€")
    name_list = []
    for amount, name, category in monthly_expenses:
        if category == tree_category:
            name_list.append(name)
    if len(name_list)==1 and name_list[0]==tree_category:
        continue
    else:
        for name in name_list:
            print(f"    {name}: {name_totals[name]:.2f}€")
print(f"Discretionary income: {monthly_discretionary_income:.2f}€")
print()
print(f"Net raw salary:             {yearly_salary/12:.2f} €")
print(f"Monthly IRPF:               {monthly_IRPF:.2f} €")
print(f"Net monthly salary:         {monthly_income:.2f} €")
print(f"Total monthly expenses:     {total_monthly_expenses:.2f} €")
print()
