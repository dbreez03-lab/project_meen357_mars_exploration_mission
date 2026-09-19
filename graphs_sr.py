import numpy as np
import matplotlib.pyplot as plt

from subfunctions import tau_dcmotor, get_gear_ratio
from subfunctions import rover

motor = rover['wheel_assembly']['motor']
speed_reducer = rover['wheel_assembly']['speed_reducer']

omega_motor = np.linspace(0, motor['speed_noload'], 100)
tau_motor = tau_dcmotor(omega_motor, motor)
Ng = get_gear_ratio(speed_reducer)

omega_out = omega_motor / Ng
tau_out = Ng * tau_motor
power_out = tau_out * omega_out


plt.subplot(3, 1, 1)
plt.plot(tau_out, omega_out)
plt.xlabel('Speed Reducer Output Torque [Nm]')
plt.ylabel('Speed Reducer Output Speed [rad/s]')


plt.subplot(3, 1, 2)
plt.plot(tau_out, power_out)
plt.xlabel('Speed Reducer Output Torque [Nm]')
plt.ylabel('Speed Reducer Output Power [W]')


plt.subplot(3, 1, 3)
plt.plot(omega_out, power_out)
plt.xlabel('Speed Reducer Output Speed [rad/s]')
plt.ylabel('Speed Reducer Output Power [W]')

plt.show()