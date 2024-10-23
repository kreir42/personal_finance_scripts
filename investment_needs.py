investments = [300, 500, 1000, 2000, 2500] #monthly investments to highlight
min_returns = 0.04 #minimum yearly returns to consider
max_returns = 0.12 #maximum yearly returns to consider
initial = 3500
final = 2.5E6
start_age = 25
max_age = 90

colorbar_center = 1000

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

num_points = 1000

min_rate = pow(min_returns+1, 1/12)
max_rate = pow(max_returns+1, 1/12)

#needed investment vs returns
x = np.linspace(min_rate, max_rate, num=num_points)
display_x = np.linspace(min_returns*100, max_returns*100, num=num_points)
y = np.linspace(1, (max_age-start_age)*12, num=num_points)
display_y = np.linspace(start_age+1, max_age, num=num_points)
X,Y = np.meshgrid(x,y)
z = (final-initial*pow(X,Y)) * (X-1)/(pow(X,Y)-1)
levels = [0, 100, 150, 200, 300, 400, 500, 750, 1000, 1250, 1500, 1750, 2000, 2500, 3000, 5000, 10000, 1000000]
norm = TwoSlopeNorm(vmin=0, vcenter=colorbar_center, vmax=10000)
plt.contourf(display_x, display_y, z, cmap='RdYlGn_r', levels=levels, norm=norm)
plt.colorbar(label='Needed monthly investment')
contour_lines = plt.contour(display_x, display_y, z, colors='black', levels=investments, norm=norm)
plt.clabel(contour_lines, fmt='%1.2f', fontsize=10)
plt.xlabel('Annual returns (%)')
plt.ylabel('Age (years)')
plt.grid(True)
plt.tight_layout()
plt.show()
