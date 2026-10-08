#experiment visualization
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from define_experiment import experiment1

experiment, end_event = experiment1() #imports for exp1

alpha_dist = experiment['alpha_dist']
alpha_deg = experiment['alpha_deg']

dist = np.linspace(0.0, alpha_dist, 100)
alpha_fun = interp1d(alpha_dist, alpha_deg, kind = 'cubic', fill_value = 'extrapolate')
terrain_angle = alpha_fun(dist)

plt.figure(figsize=(8,5))
plt.scatter(dist, terrain_angle, marker='*')
plt.title('Terrain Angle vs Position')
plt.xlabel('Position')
plt.ylabel('Terrain Angle')
plt.grid(True)
plt.tight_layout()
plt.show