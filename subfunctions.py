import numpy as np
import math
from scipy.special import erf
from scipy.interpolate import interp1d
from scipy.integrate import simpson
from scipy.integrate import solve_ivp
from define_experiment import experiment1

experiment, end_event = experiment1()

speed_reducer = {
    "type": 'reverted',
    'diam_pinion': 0.04, #m
    'diam_gear': 0.07, #m
    'mass': 1.5 #kg
}
wheel = {
    "radius" : 0.30, #m
    "mass" : 1.0 #kg
}
motor = {
    'torque_stall': 170, #N/m
    'torque_noload': 0, #N/m
    'speed_noload': 3.80, #rad/s
    'mass': 5.0, #kg
    'effcy_tau': np.array([0, 10, 20, 40, 70, 165]),
    'effcy': np.array([0, 0.55, 0.75, 0.71, 0.50, 0.05])
}
chassis = {
    'mass': 659.0 #kg
}
science_payload = {
    'mass': 75.0 #kg
}
power_subsys = {
    'mass': 90.0 #kg
}
planet = {
    'g': 3.72 #m/s^2
}
wheel_assembly = {
    'wheel': wheel,
    'speed_reducer': speed_reducer,
    'motor': motor,
}
rover = {
    'wheel_assembly': wheel_assembly,
    'chassis': chassis,
    'science_payload': science_payload,
    'power_subsys': power_subsys,
}

def tau_dcmotor(omega,motor):
  if not isinstance(motor,dict):
    raise Exception('motor must be a dictionary')

  arr = np.array(omega)
  if arr.ndim > 1:
    raise Exception('omega must be a scalar or 1D array')
  
  tau_s = motor['torque_stall']
  tau_nl = motor['torque_noload']
  omega_nl = motor['speed_noload']

  is_scalar = np.isscalar(omega)
  w_arr = np.atleast_1d(omega)

  tau_arr = tau_s - ((tau_s - tau_nl) / omega_nl) * w_arr
  
  tau_arr[w_arr < 0] = tau_s
  tau_arr[w_arr > omega_nl] = 0

  if is_scalar:
    return tau_arr[0]
  else:
    return tau_arr
    
def F_net(omega, terrain_angle, rover, planet, Crr):
    if not isinstance(rover,dict):
        raise Exception('rover must be a dictionary')
    if not isinstance(planet,dict):
        raise Exception('planet must be a dictionary')
    if not np.isscalar(Crr) or Crr <= 0:
        raise Exception('Crr must be a positive scalar')
        
    arr_omega = np.array(omega)
    arr_terrain_angle = np.array(terrain_angle)
    
    if arr_omega.ndim > 1:
        raise Exception('omega must be a scalar or 1D array')
    if arr_terrain_angle.ndim > 1:
        raise Exception('terrain angle must be a scalar or 1D array')
        
    if arr_omega.size != arr_terrain_angle.size:
        raise Exception('omega and terrain_angle must be the same size')
    if np.any(arr_terrain_angle < -75):
        raise Exception('terrain angle must be between -75 and 75 degrees')
    elif np.any(arr_terrain_angle > 75):
        raise Exception('terrain angle must be between -75 and 75 degrees')

    Fd = F_drive(omega, rover)
    Fgt = F_gravity(terrain_angle, rover, planet)
    Frr = F_rolling(omega, terrain_angle, rover, planet, Crr)
    
    f_net = Fd + Fgt + Frr
    
    return f_net
  
def get_mass(rover):
#computes the total mass of the rover. uses info in rover dict
   
    if isinstance(rover,dict) != True:
        raise Exception('Input must be a dict')
     
    chassis_mass = rover['chassis']['mass']
    payload_mass = rover['science_payload']['mass']
    power_mass = rover['power_subsys']['mass']
    motor_mass = rover['wheel_assembly']['motor']['mass']
    reducer_mass = rover['wheel_assembly']['speed_reducer']['mass']
    wheel_mass = rover['wheel_assembly']['wheel']['mass']
   
    m = chassis_mass + payload_mass + power_mass + 6 * (motor_mass + reducer_mass + wheel_mass)
           
    return(m)
   

def get_gear_ratio(speed_reducer):
    if isinstance(speed_reducer,dict) != True:
        raise Exception('Input must be a dict')
       
    if speed_reducer['type'].lower() != 'reverted':
        raise Exception('Speed reducer type must be reverted')    
   
    diam_pinion = speed_reducer['diam_pinion']
    diam_gear = speed_reducer['diam_gear']
   
    Ng = (diam_gear / diam_pinion)**2
       
    return(Ng)

   
def F_drive(omega, rover):
    if (np.isscalar(omega) or isinstance(omega, np.ndarray)) != True:
        raise Exception('Omega must be a scalar or numpy array')

    if not isinstance(rover, dict):
        raise Exception('Rover must be a dictionary')

    motor = rover['wheel_assembly']['motor']
    speed_reducer = rover['wheel_assembly']['speed_reducer']
    radius = rover['wheel_assembly']['wheel']['radius']

    tau_motor = tau_dcmotor(omega, motor)
    Ng = get_gear_ratio(speed_reducer)
   
    tau_wheel = Ng * tau_motor

    Fd_one = tau_wheel / radius
    Fd = 6 * Fd_one

    return Fd


def F_gravity(terrain_angle, rover, planet):
    if (np.isscalar(terrain_angle) or isinstance(terrain_angle, np.ndarray)) != True:
        raise Exception('Terrain angle must be a scalar or numpy array')

    if isinstance(rover, dict) != True:
        raise Exception('Rover must be a dictionary')

    if isinstance(planet, dict) != True:
        raise Exception('Planet must be a dictionary')

    if np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception('Terrain angle must be between -75 and 75 degrees')

    m = get_mass(rover)
    g = planet['g']

    #positive terrain angle upwards
    alpha = np.radians(terrain_angle)

    # negative is the downward direction
    Fgt = -m * g * np.sin(alpha)

    Fgt = np.array(Fgt)

    return Fgt
   


def F_rolling(omega, terrain_angle, rover, planet, Crr):
    if ((np.isscalar(omega) or isinstance(omega, np.ndarray)) and (np.isscalar(terrain_angle) or isinstance(terrain_angle, np.ndarray))) != True:
        raise Exception('Omega and/or Terrain Angle must be a scalar or numpy array')
    elif np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception('Terrain angle must be between -75 and 75 degrees')

    #B
    if (isinstance(rover, dict) and isinstance(planet, dict))!= True:
        raise Exception('Rover and/or Planet must be a dictionary')
    #C  
    if np.isscalar(Crr) != True or Crr <= 0:
        raise Exception('Crr must be a positive scalar')
   
    #D
    if np.size(omega) != np.size(terrain_angle):
        raise Exception('Omega and terrain angle must be the same size')

    m = get_mass(rover)
    g = planet['g']

    speed_reducer = rover['wheel_assembly']['speed_reducer']
    r = rover['wheel_assembly']['wheel']['radius']

    Ng = get_gear_ratio(speed_reducer)
    omega_wheel = omega / Ng
    v_rover = r * omega_wheel

    alpha = np.radians(terrain_angle)
    Fn = m * g * np.cos(alpha)

    Frr_simple = Crr * Fn
    Frr = -erf(40 * v_rover) * Frr_simple

    return Frr

def motorW(v, rover):
    """
    Calculates angular velocity of the motor using translational velocity and the rover dictionary as inputs.
    """
    if((isinstance(v, np.ndarray)) or (np.isscalar(v))) != True:
        raise Exception('Translational velocity must be a scalar or numpy array')
    if (isinstance(rover, dict) != True):
        raise Exception('Rover must be a dictionary')
    
    r = (rover['wheel_assembly']['wheel']['radius'])
    speed_reducer = (rover['wheel_assembly']['speed_reducer'])
    Ng = get_gear_ratio(speed_reducer)
    
    w = Ng * v / r
    
    return w

def rover_dynamics(t, y, rover, planet, experiment):
    """
    Creates the two derivative equations of velocity and acceleration. It does this by taking in time, position, and dictionaries. 
    """
    if np.isscalar(t) != True:
        raise Exception('Time sample must be a scalar')
    if (y.ndim == 1 or y.size == 2) != True :
        raise Exception('y must be a two element array')
    if (isinstance(rover, dict) != True):
        raise Exception('Rover must be a dictionary')   
    if (isinstance(planet, dict) != True):
        raise Exception('Planet must be a dictionary')  
    if (isinstance(experiment, dict) != True):
        raise Exception('Experiment must be a dictionary')
        
    v = y[0]
    x = y[1]
    
    alpha_fun = interp1d(experiment['alpha_dist'], experiment['alpha_deg'], kind = 'cubic', fill_value='extrapolate')
    terrain_angle = alpha_fun(x)
    
    w = motorW(v, rover) #same as omega
    Crr = (experiment['Crr'])
    f_net = F_net(w, terrain_angle, rover, planet, Crr)
    mass = get_mass(rover)
    a = f_net/mass
    
    dydt = np.array([v,a])
    
    return dydt

def mechpower(v, rover):
    if((isinstance(v, np.ndarray)) or (np.isscalar(v))) != True:
        raise Exception('Translational velocity must be a scalar or numpy array')
    if(isinstance(rover, dict) != True):
        raise Exception('Rover must be a dictionary')
    
    omega = motorW(v, rover)   
    tau = tau_dcmotor(omega, motor)
    P = tau * omega
    
    return P

def battenergy(t, v, rover):
    if len(t) != len(v):
        raise Exception('Array t and v are not the same size')
    if isinstance(rover, dict) != True:
        raise Exception('Rover is not a dictionary')
        
    omega = motorW(v, rover) 
    tau = tau_dcmotor(omega, motor)
    
    power = mechpower(v, rover)
    
    effcy = motor['effcy']
    effcy_tau = motor['effcy_tau']

    effcy_fun = interp1d(effcy_tau, effcy, kind = 'cubic', fill_value = 'extrapolate')
    effcy = effcy_fun(tau)

    
    E = simpson(effcy*power, x=t)
    
    return E

def simulate_rover(rover, planet, experiment, end_event):
    if isinstance(rover, dict) != True:
        raise Exception('Rover must be a dictonary')
    if isinstance(planet, dict) != True:
        raise Exception('Planet must be a dictonary')
    if isinstance(experiment, dict) != True:
        raise Exception('Experiment must be a dictonary')
    if isinstance(end_event, dict) != True:
        raise Exception('end_event must be a dictonary')
        
    tspan = experiment['time_range']
    y0 = experiment['initial_conditions']
    events = end_of_mission_event(end_event)
    
    fun = lambda t, y: rover_dynamics(t, y, rover, planet, experiment)
    sol = solve_ivp (fun, tspan, y0, method = 'RK45', max_step = 0.5, events = events)
    t = sol.t
    v = sol.y[0, :]
    x = sol.y[1, :]
    
    rover['telemetry'] = {}
    rover['telemetry']['Time'] = t
    rover['telemetry']['velocity'] = v
    rover['telemetry']['position'] = x
    rover['telemetry']['completion_time'] = t[-1]-t[0]
    rover['telemetry']['distance_traveled'] = x[-1] - x[0]
    rover['telemetry']['max_velocity'] = np.max(v)
    rover['telemetry']['average_velocity'] = (x[-1] - x[0])/(t[-1]-t[0])
    rover['telemetry']['power'] = mechpower(v, rover)
    rover['telemetry']['battery_energy'] = battenergy(t, v, rover)
    rover['telemetry']['energy_per_distance'] = (battenergy(t, v, rover))/(x[-1] - x[0])
    
    return rover
    
def end_of_mission_event(end_event):
    """
    Defines an event that terminates the mission simulation. Mission is over
    when rover reaches a certain distance, has moved for a maximum simulation
    time or has reached a minimum velocity.
    """
    mission_distance = end_event['max_distance']
    mission_max_time = end_event['max_time']
    mission_min_velocity = end_event['min_velocity']
    # Assume that y[1] is the distance traveled
    distance_left = lambda t,y: mission_distance - y[1]
    distance_left.terminal = True
    time_left = lambda t,y: mission_max_time - t
    time_left.terminal = True
    velocity_threshold = lambda t,y: y[0] - mission_min_velocity;
    velocity_threshold.terminal = True
    velocity_threshold.direction = -1
    # terminal indicates whether any of the conditions can lead to the
    # termination of the ODE solver. In this case all conditions can terminate
    # the simulation independently.
    # direction indicates whether the direction along which the different
    # conditions is reached matters or does not matter. In this case, only
    # the direction in which the velocity treshold is arrived at matters
    # (negative)
    events = [distance_left, time_left, velocity_threshold]
    return events

