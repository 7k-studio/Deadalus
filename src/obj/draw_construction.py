import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

''' 
This script helps to visualize the leading and trailing edge control points of an airfoil design.
It calculates the control points based on given parameters and plots them using matplotlib.
'''

params = {
    "chord": 1,
    "origin_X": 0,
    "origin_Y": 0,
    "le_thickness": 0.05,
    "le_depth": 0.4,
    "le_offset": 0.0,
    "le_angle": -24.02,
    "te_thickness": 0.01,
    "te_depth": 0.01,
    "te_offset": 0.0,
    "te_angle": -85.05,
    "ps_fwd_angle": 0,
    "ps_rwd_angle": 0,
    "ps_fwd_accel": 0.20,
    "ps_rwd_accel": 0.10,
    "ss_fwd_angle": 0,
    "ss_rwd_angle": 0,
    "ss_fwd_accel": 0.16,
    "ss_rwd_accel": 0.10
}

p_le_start = [params['origin_X'], params['origin_Y']+params['le_offset']]
p_le_end = [p_le_start[0]+params['le_depth']*math.cos(np.radians(params['le_angle'])),p_le_start[1]+(params['le_depth']*math.sin(np.radians(params['le_angle'])))]
a0 = math.tan(np.radians(90+params['le_angle'])) # Directional param of the leading edge straight and the pararel one
a1 = math.tan(np.radians(params['ps_fwd_angle']+params['le_angle'])) # Directional param of the pressure side forward slope
a2 = math.tan(np.radians(params['ss_fwd_angle']+params['le_angle'])) # Directional param of the suction side forward slope
b0 = p_le_start[1]-a0*p_le_start[0] # Positional parameter of the leading edge straight 'Origin Point'
b0p = p_le_end[1]-a0*p_le_end[0]
b1 = p_le_end[1]+(params['le_thickness']/2*math.cos(np.radians(params['le_angle'])))-a1*(p_le_end[0]-(params['le_thickness']/2*math.sin(np.radians(params['le_angle']))))
b2 = p_le_end[1]-(params['le_thickness']/2*math.cos(np.radians(params['le_angle'])))-a2*(p_le_end[0]+(params['le_thickness']/2*math.sin(np.radians(params['le_angle']))))
p_le_t = [(b1-b0)/(a0-a1),a0*((b1-b0)/(a0-a1))+b0] # G1 upper point
p_le_d = [(b2-b0)/(a0-a2),a0*((b2-b0)/(a0-a2))+b0] # G1 lower point
p_le_ps = [(b1-b0p)/(a0-a1),a0*((b1-b0p)/(a0-a1))+b0p] # G0 with with the pressure side
p_le_ss = [(b2-b0p)/(a0-a2),a0*((b2-b0p)/(a0-a2))+b0p] # G0 with with the suction side
le_constr = np.vstack([p_le_ss, p_le_d, p_le_t, p_le_ps]).T
p_te_start = [params['origin_X']+params['chord'], params['origin_Y']+params['te_offset']]
p_te_end = [p_te_start[0]-params['te_depth']*math.cos(np.radians(params['te_angle'])), p_te_start[1]-(params['te_depth']*math.sin(np.radians(params['te_angle'])))]
a3 = math.tan(np.radians(90+params['te_angle']))
a4 = math.tan(np.radians(params['ps_rwd_angle']+params['te_angle']))
a5 = math.tan(np.radians(params['ss_rwd_angle']+params['te_angle']))
b3 = p_te_start[1]-a3*p_te_start[0]
b3p = p_te_end[1]-a3*p_te_end[0]
b4 = p_te_end[1]+(params['te_thickness']/2*math.cos(np.radians(params['te_angle'])))-a4*(p_te_end[0]+params['te_thickness']*math.sin(np.radians(params['te_angle'])))
b5 = p_te_end[1]-(params['te_thickness']/2*math.cos(np.radians(params['te_angle'])))-a5*(p_te_end[0]-params['te_thickness']*math.sin(np.radians(params['te_angle'])))
p_te_t = [(b4-b3)/(a3-a4),a3*((b4-b3)/(a3-a4))+b3] # G1 upper point
p_te_d = [(b5-b3)/(a3-a5),a3*((b5-b3)/(a3-a5))+b3] # G1 lower point
p_te_ps = [(b4-b3p)/(a3-a4),a3*((b4-b3p)/(a3-a4))+b3p] # G0 with with the pressure side
p_te_ss = [(b5-b3p)/(a3-a5),a3*((b5-b3p)/(a3-a5))+b3p] # G0 with with the suction side
te_constr = np.vstack([p_te_ss, p_te_d, p_te_t, p_te_ps]).T
p_ps_le = p_le_ps
p_ps_te = p_te_ps
p_ps_1 = [params['origin_X']+params['ps_fwd_accel'], a1*(params['origin_X']+params['ps_fwd_accel'])+b1]
p_ps_2 = [p_ps_te[0]-params['ps_rwd_accel'], a4*(p_ps_te[0]-params['ps_rwd_accel'])+b4]   
ps_constr = np.vstack([p_ps_le, p_ps_1, p_ps_2, p_ps_te]).T
p_ss_le = p_le_ss
p_ss_te = p_te_ss
p_ss_1 = [params['origin_X']+params['ss_fwd_accel'], a2*(params['origin_X']+params['ss_fwd_accel'])+b2]
p_ss_2 = [p_ss_te[0]-params['ss_rwd_accel'], a5*(p_ss_te[0]-params['ss_rwd_accel'])+b5]   
ss_constr = np.vstack([p_ss_le, p_ss_1, p_ss_2, p_ss_te]).T

X_LE = np.linspace(0,0.2,10)
X_TE = np.linspace(params['chord']-0.2,params['chord'],10)

print("Leading Edge Control Points:")
print(le_constr)
print("Trailing Edge Control Points:")
print(te_constr)
print("Pressure Side Control Points:")
print(ps_constr)
print("Suction Side Control Points:")
print(ss_constr)

#plt.plot(X_LE, a0*X_LE+b0, label='Leading Edge Straight: a3')  # Plot the leading edge straight line
#plt.plot(X_LE, a0*X_LE+b0p, label='Leading Edge Parallel: a3')  # Plot the leading edge parallel line
#plt.plot(X_LE, a1*X_LE+b1, label='Pressure Side Forward Slope: a4')
#plt.plot(X_LE, a2*X_LE+b2, label='Suction Side Forward Slope: a5')
#plt.plot(X_LE, -1/a0*X_LE+(p_le_start[1]+1/a0*p_le_start[0]), label='Trailing Edge Straight: -1/a3')  # Plot the trailing edge straight line

#plt.plot(X_TE, a3*X_TE+b3, label='Trailing Edge Straight: a3')  # Plot the leading edge straight line
#plt.plot(X_TE, a3*X_TE+b3p, label='Trailing Edge Parallel: a3')  # Plot the leading edge parallel line
#plt.plot(X_TE, a4*X_TE+b4, label='Pressure Side Forward Slope: a4')
#plt.plot(X_TE, a5*X_TE+b5, label='Suction Side Forward Slope: a5')
#plt.plot(X_TE, -1/a3*X_TE+(p_te_start[1]+1/a3*p_te_start[0]), label='Trailing Edge Straight: -1/a3')  # Plot the trailing edge straight line

plt.plot(p_le_start[0], p_le_start[1], 'x', color='black',label='Leading Edge Start')
plt.plot(p_le_end[0], p_le_end[1], 'o', color='black', label='Leading Edge End')
#plt.plot(p_te_start[0], p_te_start[1], 'x', color='black',label='Trailing Edge Start')
#plt.plot(p_te_end[0], p_te_end[1], 'o', color='black', label='Trailing Edge End')

plt.plot(le_constr[0, :], le_constr[1, :], 'r-', label='Leading Edge')
#plt.plot(te_constr[0, :], te_constr[1, :], 'b-', label='Trailing Edge')
#plt.plot(ps_constr[0, :], ps_constr[1, :], 'g-', label='Pressure Side')
#plt.plot(ss_constr[0, :], ss_constr[1, :], 'y-', label='Suction Side')

# Add scatter plots for control points
plt.scatter(le_constr[0, :], le_constr[1, :], color='r')
#plt.scatter(te_constr[0, :], te_constr[1, :], color='b')
#plt.scatter(ps_constr[0, :], ps_constr[1, :], color='g')
#plt.scatter(ss_constr[0, :], ss_constr[1, :], color='y')
plt.axis('equal')  # <-- Use this to set equal aspect ratio for the current axes
plt.legend()
plt.show()