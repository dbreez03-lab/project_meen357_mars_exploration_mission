#study_parachute_size.py

#create visualizations of changing parachue size

#results, 
#EDL System Altitude 11 km
#EDL System Velocity -590 m/s
#Rockets Off
#Parachute Deployed, not ejected
#Heat shield Not ejected
#Sky crane Off
#Speed controller Off
#Position controller Off

#parachute diameters of 14 to 19 meters at h = 0.5m intervals

#create a 3 x 1 array of plots plt.subplots command
# 1. simulated time vs parachute diameter
# 2. rover speed at simulation termination vs parachute diameter
# 3. rover landing success (1=success; 0= failure) vs. parachute diameter


#reqq
# 1.reaches ground safety
# 2.time it takes to get rover toground(minimze time)

import numpy as np
import matplotlib.pyplot as plt
from define_edl_system import *
from subfunctions_EDL import *
from define_planet import *
from define_mission_events import *

for i in np.arange(14.0, 19.5, 0.5):
# *************************************
# load dicts that define the EDL system (includes rover), planet,
# mission events and so forth.
    edl_system = define_edl_system_1()
    mars = define_planet()
    mission_events = define_mission_events()


# Overrides what might be in the loaded data to establish our desired
# initial conditions
    edl_system['altitude'] = 11000    # [m] initial altitude
    edl_system['velocity'] = -590     # [m/s] initial velocity
    edl_system['parachute']['deployed'] = True   # our parachute is open
    edl_system['parachute']['ejected'] = False   # and still attached
    edl_system['rover']['on_ground'] = False # the rover has not yet landed
    edl_system['parachute']['diameter'] = i

    tmax = 2000   # [s] maximum simulated time
    
    # the simulation. changing last argument to false turns off message echo
    [t, Y, edl_system] = simulate_edl(edl_system, mars, mission_events, tmax, False)
    
    fig, axs = plt.subplots(3,1, figsize(8,10))
    plt.tight_layout()
    axs[0].plot(t, Y[0, :])
    axs[0].set_title('velocity vs. time', fontsize=10)
    axs[0].grid()
    axs[1].plot(t,Y[1, :])
    axs[1].set_title('altitude vs. time', fontsize=10)
    axs[1].grid()
    axs[2].plot(t,Y[2, :])
    axs[2].set_title('fuel mass vs. time', fontsize=10)
    axs[2].grid()
    axs[3].plot(t,Y[3, :])
    axs[3].set_title('speed error integral vs. time', fontsize=10)
    axs[3].grid()
    axs[4].plot(t,Y[4, :])
    axs[4].set_title('position error integral vs. time', fontsize=10)
    axs[4].grid()
    axs[5].plot(t,Y[5, :])
    axs[5].set_title('velocity of rover relative to sky crane vs. time', fontsize=10)
    axs[5].grid()
    axs[6].plot(t,Y[6, :])
    axs[6].set_title('position of rover relative to sky crane vs. time', fontsize=10)
    axs[6].grid()

    print(f'{i} meters')
    
    