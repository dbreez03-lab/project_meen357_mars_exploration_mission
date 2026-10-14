import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from subfunctions import simulate_rover
from subfunctions import rover, planet, experiment, end_event

rover = simulate_rover(rover, planet, experiment, end_event)

table = pd.DataFrame({
    'Variables': ['Completion Time' , 'Distance Traveled', 'Max Velocity', 
                 'Average Velocity', 'Battery Energy', 'Energy per Distance'],
    'Value': [rover['telemetry']['completion_time'], rover['telemetry']['distance_traveled'],
              rover['telemetry']['max_velocity'], rover['telemetry']['average_velocity'],
              rover['telemetry']['battery_energy'], rover['telemetry']['energy_per_distance']],
    'Units': ['s', 'm', 'm/s', 'm/s', 'J', 'J/m']
    })

print(table)




fig, axs = plt.subplots(3)
fig.subplots_adjust(hspace = 1.4)
axs[0].set_title('Position vs. Time')
axs[0].plot(rover['telemetry']['Time'], rover['telemetry']['position'])
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Postion (m)')
axs[1].set_title('Velocity vs. Time')
axs[1].plot(rover['telemetry']['Time'], rover['telemetry']['velocity'])
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Velocity (m/s)')
axs[2].set_title('Power vs. Time')
axs[2].plot(rover['telemetry']['Time'], rover['telemetry']['power'])
axs[2].set_xlabel('Time (s)')
axs[2].set_ylabel('Power (W)')


