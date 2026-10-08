#efficiency_visualization
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from subfunctions import motor

effcy = motor['effcy']
effcy_tau = motor['effcy_tau']
tau_max = motor['torque_stall']
tau_min = motor['torque_noload']

effcy_fun = interp1d(effcy_tau, effcy, kind = 'cubic', fill_value = 'extrapolate')

tau = np.linspace(tau_min, tau_max, 100)
effcy = effcy_fun(tau)

plt.figure(figsize=(8,5))
plt.scatter(tau, effcy, marker='*')
plt.title('Motor Torque vs Efficiency')
plt.xlabel('Motor Torque')
plt.ylabel('Efficiency')
plt.grid(True)
plt.tight_layout()
plt.show

