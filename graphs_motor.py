#graphs_motor.py
import matplotlib.pyplot as plt
import numpy as np
from subfunctions import tau_dcmotor, motor
#plot motor shaft speed vs motor shaft torque
#plot motor power vs motor shaft torque
#plot motor power vs motor shaft speed

omega = motor['speed_noload']
tau = motor['torque_stall']
tau_noload = motor['torque_noload']

arr_omega = np.linspace(0.0, omega, 300, dtype=np.float64)
arr_tau = tau_dcmotor(arr_omega, motor) 

power = arr_tau * arr_omega

plt.figure(figsize=(8,10))
#subplot; speed v torque
plt.subplot(2,2,1)
plt.plot(arr_tau, arr_omega, 'b-', linewidth=2)
plt.xlabel('Motor Shaft Torque [N*m]')
plt.ylabel('Motor Shaft Speed [rad/s]')
plt.title('Motor Shaft Torque vs. Motor Shaft Speed')
plt.grid(True)

#subplot; power v torque
plt.subplot(2,2,2)
plt.plot(arr_tau, power, 'r-', linewidth=2)
plt.xlabel('Motor Shaft Torque [N*m]')
plt.ylabel('Power [W]')
plt.title('Motor Shaft Torque vs. Power')
plt.grid(True)

#subplot; power v speed
plt.subplot(2,1,2)
plt.plot(arr_omega, power, 'g-', linewidth=2)
plt.ylabel('Power [W]')
plt.xlabel('Motor Shaft Speed [rad/s]')
plt.title('Power vs. Motor Shaft Speed')
plt.grid(True)

plt.tight_layout()
plt.show()
