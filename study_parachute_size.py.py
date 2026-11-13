import numpy as np
import matplotlib.pyplot as plt
from define_edl_system import *
from subfunctions_EDL import *
from define_planet import *
from define_mission_events import *
from redefine_edl_system import *

# *************************************
# load dicts that define the EDL system (includes rover), planet,
# mission events and so forth.



tmax = 2000   # [s] maximum simulated time

paramin = 14 # Smallest parahcute diameter being checked
paramax = 19 # Larget parahcute diameter being checked
stepsize = 0.5 #how much we are changing our values by

TimeTermList = [] #empty list, will be the time taken of the simulation
SpeedTermList = [] #empty list, will be the rover speed with respect to ground
SuccessList = [] #empty list, will be if the rover made it to the ground
ParaDia = [] #empty list, will be the diameters of the chutes we are testing

for i in np.arange(paramin, paramax+stepsize, stepsize):
    
    ParaDia.append(i) # adding to the list of diameters
    
    edl_system = define_edl_system_1() #was in the main
    mars = define_planet() #was in the main
    mission_events = define_mission_events() #was in the main
    
    edl_system = redefine_edl_system(edl_system) #changed the values based on new siuation
    edl_system['parachute']['diameter'] = i #changing the parachute diameter for each trial

    # the simulation. changing last argument to false turns off message echo
    [t, Y, edl_system] = simulate_edl(edl_system, mars, mission_events, tmax, False) #conduting the tests
    

    TimeTermList.append(t[-1]) #the last time in the array of times is the final time
    #learned this based on all the plots before it was always just t
    
    touchspeed = Y[5, -1]+Y[0,-1] # adding speed rover and rover relative to the crane is equal to rover speed relative to ground
    # learned this by speed + rover_rel_vel and axs[5].plot(t,Y[5, :]) --> velocity of rover relative to sky crane and axs[0].plot(t, Y[0, :]) --> velocity
    # thus we knew which part of Y had the array of info we needed
    
    
    SpeedTermList.append(touchspeed) #adding to list
    
    # checked in the console the parts of edl_system and found that this is in it
    # Also knew that if speed is greater than danger the rover breaks on impact
    if edl_system['rover']['on_ground'] == True and (abs(touchspeed) <= abs(edl_system['sky_crane']['danger_speed'])):
        SuccessList.append(int(1))
    else:
        SuccessList.append(int(0))
    
fig, axes = plt.subplots(3,1)
fig.tight_layout()
axes[0].plot(ParaDia, TimeTermList, 'bo-')
axes[0].set_xlabel('Diameter of Parachute (m)', fontsize = 8)
axes[0].set_ylabel('Simulated Time (s)', fontsize = 8)
axes[1].plot(ParaDia, SpeedTermList, 'ro-')
axes[1].set_xlabel('Diameter of Parachute (m)', fontsize = 8)
axes[1].set_ylabel('Rover speed relative to ground (m/s)', fontsize = 8)
axes[2].plot(ParaDia, SuccessList, 'go-')
axes[2].set_xlabel('Diameter of Parachute (m)', fontsize = 8)
axes[2].set_ylabel('Landing Success', fontsize = 8)
