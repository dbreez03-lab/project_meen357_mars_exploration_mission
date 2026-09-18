#analysis_terrain_slope
import matplotlib.pyplot as plt
from subfunctions import F_net, get_gear_ratio
import numpy as np

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

def fp_method(fun, a, b, err_max = 1e-5, iter_max = 1000):
    if a> b:
        raise Exception("lower bound must be less than upper bound")
    numIter = 0
    done = False
    exitFlag = 0
    
    fa = fun(a)
    fb = fun(b)
    if fa*fb > 0:
        return "bad bracket", None, 0, -1
    elif fa == 0:
        return a, 0, 0, 1
    elif fb == 0:
        return b, 0, 0, 1
    
    c_old = a
    
    while not done:
        numIter += 1
        c = ((a * fb) - (b * fa)) / (fb - fa)
        fc = fun(c)
        
        if abs(c) < 1e-12:
            err_est = abs((c-c_old) /c)
        else:
            err_est = abs(c-c_old)
        if abs(fc) < 1e-16 or err_est <= err_max:
            done = True
            root = c
            exitFlag = 1
        elif numIter >= iter_max:
            done = True
            root = c
            exitFlag = 0
        else:
            if fa * fc > 0:
                a = c
                fa = fc
            else:
                b = c
                fb = fc
                c_old = c
    return root, err_est, numIter, exitFlag

Crr = 0.15
slope_array_deg = np.linspace(-15,35,25)
v_max = np.zeros(len(slope_array_deg), dtype=np.float64)

Ng = get_gear_ratio(speed_reducer)
r = wheel['radius']
omega_nl = motor['speed_noload']

for i, alpha in enumerate(slope_array_deg):
    def f_net_obj(omega_val):
        res = F_net(np.array([omega_val]), np.array([alpha]), rover, planet, Crr)
        return float(res[0]) if isinstance(res, np.ndarray) else float(res)
    
    try:
        omega_prime, err, iters, flag = fp_method(f_net_obj, 0.0, omega_nl, err_max=1e-5)
        if flag == 1 and omega_prime is not None:
            v_max[i] = r * (omega_prime / Ng)
        else:
            v_max[i] = np.nan
    except Exception:
        v_max[i] = np.nan

plt.figure(figsize=(8, 5))
plt.plot(slope_array_deg, v_max, 'b-o', linewidth=2)
plt.title('Maximum Attainable Rover Speed vs. Terrain Slope')
plt.xlabel('Terrain Angle [deg]')
plt.ylabel('Maximum Rover Speed [m/s]')
plt.grid(True)
plt.tight_layout()
plt.show()