#experiment visualization
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from define_experiment import experiment1

experiment, end_event = experiment1() #imports for exp1

#loads dictionary experiment
alpha_dist = experiment['alpha_dist']
alpha_deg = experiment['alpha_deg']

dist = np.linspace(0.0, alpha_dist, 100)

#interpolates values of effcy_tau(x) and effcy(y) using a third order polynomial 'cubic'
#third order polynomial interpolation passes through 4 data points and for each value runs through
#the general form P(x) = ax^3 + bx^2 + cx + d and is a system of equations that solves for the any value
#corresponding to alpha_deg
alpha_fun = interp1d(alpha_dist, alpha_deg, kind = 'cubic', fill_value = 'extrapolate')
terrain_angle = alpha_fun(dist)#calls function alpha_fun

plt.figure(figsize=(8,5))
plt.scatter(dist, terrain_angle, marker='*')
plt.title('Terrain Angle vs Position')
plt.xlabel('Position')
plt.ylabel('Terrain Angle')
plt.grid(True)
plt.tight_layout()
plt.show
