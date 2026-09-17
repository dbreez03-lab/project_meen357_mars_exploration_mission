import numpy as np
import math
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
    'mass': 5.0 #kg
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

  if is_scalar:
    return tau_arr[0]
  else:
    return tau_arr
    
def F_net(omega, terrain_angle, rover, planet, Crr):
  arr_omega = np.array(omega)
  if arr_omega.ndim > 1:
    raise Exception('omega must be a scalar or 1D array')
  arr_terrain_angle = np.array(terrain_angle)
  if arr_terrain_angle.ndim > 1:
    raise Exception('terrain angle must be a scalar or 1D array')

  if terrain_angle < -75:
    raise Exception('terrain angle must be between -75 and 75 degrees')
  elif terrain_angle > 75:
    raise Exception('terrain angle must be between -75 and 75 degrees')
  
  if not isinstance(rover,dict):
    raise Exception('rover must be a dictionary')
  if not isinstance(planet,dict):
    raise Exception('planet must be a dictionary')

  arr_crr = np.array(Crr)
  if not np.isscalar(arr_crr):
    raise Exception('Crr must be a scalar')
  
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
   

def get_gear_ratio(speed):
    if isinstance(speed,dict) != True:
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
    if ((np.isscalar(omega) or isinstance(omega, np.ndarray)) or (np.isscalar(terrain_angle) or isinstance(terrain_angle, np.ndarray))) != True:
        raise Exception('Omega and/or Terrain Angle must be a scalar or numpy array')
    elif np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception('Terrain angle must be between -75 and 75 degrees')

    #B
    if (isinstance(rover, dict) or isinstance(planet, dict))!= True:
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
    Frr = -math.erf(40 * v_rover) * Frr_simple

    return Frr
