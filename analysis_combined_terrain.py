import numpy as np
import matplotlib.pyplot as plt

from subfunctions import F_net, get_gear_ratio
from subfunctions import rover, planet


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

Crr_array = np.linspace(0.01, 0.5, 25)
slope_array_deg = np.linspace(-15, 35, 25)

CRR, SLOPE = np.meshgrid(Crr_array, slope_array_deg)

VMAX = np.zeros(np.shape(CRR), dtype=float)

speed_reducer = rover['wheel_assembly']['speed_reducer']
Ng = get_gear_ratio(speed_reducer)

r = rover['wheel_assembly']['wheel']['radius']
omega_noload = rover['wheel_assembly']['motor']['speed_noload']

N = np.shape(CRR)[0]

for i in range(N):
    for j in range(N):

        Crr_sample = float(CRR[i, j])
        slope_sample = float(SLOPE[i, j])

        def fun(omega):
            return F_net(omega, slope_sample, rover, planet, Crr_sample)

        omega_max, err_est, numIter, exitFlag = fp_method(fun, 0, omega_noload)

        if exitFlag == 1:

            omega_wheel = omega_max / Ng
            v_max = r * omega_wheel
            VMAX[i, j] = v_max

        else:
            VMAX[i, j] = np.nan


plt.contourf(CRR, SLOPE, VMAX, levels=20)

plt.colorbar(label='Maximum Rover Velocity [m/s]')

plt.xlabel('Coefficient of Rolling Resistance, Crr')
plt.ylabel('Terrain Slope [deg]')
plt.title('Maximum Rover Velocity vs. Terrain Conditions')

plt.show()