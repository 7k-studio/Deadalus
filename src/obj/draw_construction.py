'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DEADALUS.

DEADALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DEADALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DEADALUS.  If not, see <http://www.gnu.org/licenses/>.

'''

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import class_airfoil
import tools_program as tools

''' 
This script helps to visualize the leading and trailing edge control points of an airfoil design.
It calculates the control points based on given parameters and plots them using matplotlib.
'''

airfoil = class_airfoil.Airfoil()

# Creating orignin points
p_le_org = [airfoil.params['origin_X'], airfoil.params['origin_Y']+airfoil.LE.params['offset']]
p_te_org = tools.vec_translate(p_le_org, airfoil.params['stretch'], airfoil.params["incidence"])

# Creating up (u) and down (d) point for Leading Edge PS and SS handle 
p_le_u = tools.vec_translate(p_le_org, airfoil.LE.params['thickness']/2, 90+airfoil.LE.params["angle"])
p_le_d = tools.vec_translate(p_le_org, -airfoil.LE.params['thickness']/2, 90+airfoil.LE.params["angle"])

# Creating up (u) and down (d) point for Trailing Edge PS and SS handle 
p_te_u = tools.vec_translate(p_te_org, airfoil.TE.params['thickness']/2, 90+airfoil.TE.params["angle"])
p_te_d = tools.vec_translate(p_te_org, -airfoil.TE.params['thickness']/2, 90+airfoil.TE.params["angle"])

#===================================
# Creating handle for Pressure Side
#===================================
try:
    p_ps_fwd_tan = tools.vec_translate(p_le_u, airfoil.PS.params['fwd_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.PS.params["fwd_wedge"]))
except ZeroDivisionError:
    p_ps_fwd_tan = p_le_u

try:
    p_ps_rwd_tan = tools.vec_translate(p_te_u, -airfoil.PS.params['rwd_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.PS.params["rwd_wedge"]))
except ZeroDivisionError:
    p_ps_fwd_tan = p_te_u

try:
    p_ps_fwd_crv = tools.vec_translate(p_ps_fwd_tan, airfoil.PS.params['fwd_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.PS.params["fwd_wedge"]+airfoil.PS.params["fwd_slope"]))
except ZeroDivisionError:
    p_ps_fwd_crv = p_ps_fwd_tan

try:
    p_ps_rwd_crv = tools.vec_translate(p_ps_rwd_tan, -airfoil.PS.params['rwd_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.PS.params["rwd_wedge"]+airfoil.PS.params["rwd_slope"]))
except ZeroDivisionError:
    p_ps_fwd_tan = p_ps_rwd_tan

#===================================
# Creating handle for Suction Side
#===================================
try:
    p_ss_fwd_tan = tools.vec_translate(p_le_d, airfoil.SS.params['fwd_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.SS.params["fwd_wedge"]))
except ZeroDivisionError:
    p_ss_fwd_tan = p_le_d

try:
    p_ss_rwd_tan = tools.vec_translate(p_te_d, -airfoil.SS.params['rwd_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.SS.params["rwd_wedge"]))
except ZeroDivisionError:
    p_ss_fwd_tan = p_te_d

try:
    p_ss_fwd_crv = tools.vec_translate(p_ss_fwd_tan, airfoil.SS.params['fwd_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.SS.params["fwd_wedge"]+airfoil.SS.params["fwd_slope"]))
except ZeroDivisionError:
    p_ss_fwd_tan = p_ss_fwd_tan

try:
    p_ss_rwd_crv = tools.vec_translate(p_ss_rwd_tan, -airfoil.SS.params['rwd_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.SS.params["rwd_wedge"]+airfoil.SS.params["rwd_slope"]))
except ZeroDivisionError:
    p_ss_rwd_crv = p_ss_rwd_tan

#===================================
# Creating handle for Leading Edge
#===================================
try:
    p_le_ps_tan = tools.vec_translate(p_le_u, -airfoil.LE.params['ps_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.PS.params["fwd_wedge"]))
except ZeroDivisionError:
    p_le_ps_tan = p_le_u

try:
    p_le_ss_tan = tools.vec_translate(p_le_d, -airfoil.LE.params['ss_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.PS.params["rwd_wedge"]))
except ZeroDivisionError:
    p_le_ss_tan = p_le_d

try:
    p_le_ps_crv = tools.vec_translate(p_le_ps_tan, -airfoil.LE.params['ps_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.PS.params["fwd_wedge"]+airfoil.LE.params["ps_slope"]))
except ZeroDivisionError:
    p_le_ps_crv = p_le_ps_tan

try:
    p_le_ss_crv = tools.vec_translate(p_le_ss_tan, -airfoil.LE.params['ss_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.LE.params["angle"]+airfoil.PS.params["rwd_wedge"]+airfoil.LE.params["ss_slope"]))
except ZeroDivisionError:
    p_le_ss_tan = p_le_ss_tan

#===================================
# Creating handle for Trailing Edge
#===================================
try:
    p_te_ps_tan = tools.vec_translate(p_te_u, airfoil.TE.params['ps_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.PS.params["fwd_wedge"]))
except ZeroDivisionError:
    p_te_ps_tan = p_te_u

try:
    p_te_ss_tan = tools.vec_translate(p_te_d, airfoil.TE.params['ss_tan']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.PS.params["rwd_wedge"]))
except ZeroDivisionError:
    p_te_ss_tan = p_te_d

try:
    p_te_ps_crv = tools.vec_translate(p_te_ps_tan, airfoil.TE.params['ps_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.PS.params["fwd_wedge"]+airfoil.TE.params["ps_slope"]))
except ZeroDivisionError:
    p_te_ps_crv = p_te_ps_tan

try:
    p_te_ss_crv = tools.vec_translate(p_te_ss_tan, airfoil.TE.params['ss_curv']/airfoil.params['stretch'], (airfoil.params["incidence"]+airfoil.TE.params["angle"]+airfoil.PS.params["rwd_wedge"]+airfoil.TE.params["ss_slope"]))
except ZeroDivisionError:
    p_te_ss_tan = p_te_ss_tan


# p_te_end = [p_te_org[0]-airfoil.TE.params['depth']*math.cos(np.radians(airfoil.TE.params['angle'])), p_te_org[1]-(airfoil.TE.params['depth']*math.sin(np.radians(airfoil.TE.params['angle'])))]
# a3 = math.tan(np.radians(90+airfoil.TE.params['angle']))
# a4 = math.tan(np.radians(airfoil.PS.params['rwd_wedge']+airfoil.TE.params['angle']))
# a5 = math.tan(np.radians(airfoil.SS.params['rwd_angle']+airfoil.TE.params['angle']))
# b3 = p_te_org[1]-a3*p_te_org[0]
# b3p = p_te_end[1]-a3*p_te_end[0]
# b4 = p_te_end[1]+(airfoil.TE.params['thickness']/2*math.cos(np.radians(airfoil.TE.params['angle'])))-a4*(p_te_end[0]-airfoil.TE.params['thickness']/2*math.sin(np.radians(airfoil.TE.params['angle'])))
# b5 = p_te_end[1]-(airfoil.TE.params['thickness']/2*math.cos(np.radians(airfoil.TE.params['angle'])))-a5*(p_te_end[0]+airfoil.TE.params['thickness']/2*math.sin(np.radians(airfoil.TE.params['angle'])))
# p_te_t = [(b4-b3)/(a3-a4),a3*((b4-b3)/(a3-a4))+b3] # G1 upper point
# p_te_d = [(b5-b3)/(a3-a5),a3*((b5-b3)/(a3-a5))+b3] # G1 lower point
# p_te_ps = [(b4-b3p)/(a3-a4),a3*((b4-b3p)/(a3-a4))+b3p] # G0 with with the pressure side
# p_te_ss = [(b5-b3p)/(a3-a5),a3*((b5-b3p)/(a3-a5))+b3p] # G0 with with the suction side
# te_constr = np.vstack([p_te_ss, p_te_d, p_te_t, p_te_ps]).T
# p_ps_le = p_le_ps
# p_ps_te = p_te_ps
# p_ps_1 = [airfoil.params['origin_X']+airfoil.PS.params['fwd_tan'], a1*(airfoil.params['origin_X']+airfoil.PS.params['fwd_tan'])+b1]
# p_ps_2 = [p_ps_te[0]-airfoil.PS.params['rwd_tan'], a4*(p_ps_te[0]-airfoil.PS.params['rwd_tan'])+b4]   
# ps_constr = np.vstack([p_ps_le, p_ps_1, p_ps_2, p_ps_te]).T
# p_ss_le = p_le_ss
# p_ss_te = p_te_ss
# p_ss_1 = [airfoil.params['origin_X']+airfoil.SS.params['fwd_accel'], a2*(airfoil.params['origin_X']+airfoil.SS.params['fwd_accel'])+b2]
# p_ss_2 = [p_ss_te[0]-airfoil.SS.params['rwd_accel'], a5*(p_ss_te[0]-airfoil.SS.params['rwd_accel'])+b5]   
# ss_constr = np.vstack([p_ss_le, p_ss_1, p_ss_2, p_ss_te]).T
# # Generate Splines
le_constr = np.vstack([p_le_u, p_le_ps_tan, p_le_ps_crv, p_le_ss_crv, p_le_ss_tan, p_le_d]).T

te_constr = np.vstack([p_te_u, p_te_ps_tan, p_te_ps_crv, p_te_ss_crv, p_te_ss_tan, p_te_d]).T

ps_constr = np.vstack([p_le_u, p_ps_fwd_tan, p_ps_fwd_crv, p_ps_rwd_crv, p_ps_rwd_tan, p_te_u]).T

ss_constr = np.vstack([p_le_d, p_ss_fwd_tan, p_ss_fwd_crv, p_ss_rwd_crv, p_ss_rwd_tan, p_te_d]).T

le_spline = tools.CreateBSpline(le_constr)
te_spline = tools.CreateBSpline(te_constr)
ps_spline = tools.CreateBSpline(ps_constr)
ss_spline = tools.CreateBSpline(ss_constr)

'''
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

'''

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

plt.plot(p_le_org[0], p_le_org[1], 'x', color='black',label='Leading Edge Start')
plt.plot(p_te_org[0], p_te_org[1], 'x', color='black', label='Leading Edge End')

plt.plot(p_le_u[0], p_le_u[1], 'o', color='black', label='Leading Edge End')
plt.plot(p_le_d[0], p_le_d[1], 'o', color='black', label='Leading Edge End')
plt.plot(p_te_u[0], p_te_u[1], 'o', color='black', label='Leading Edge End')
plt.plot(p_te_d[0], p_te_d[1], 'o', color='black', label='Leading Edge End')

plt.plot(p_ps_fwd_tan[0], p_ps_fwd_tan[1], 'o', color='green', label='Pressure Side End')
plt.plot(p_ps_fwd_crv[0], p_ps_fwd_crv[1], 'o', color='green', label='Pressure Side End')
plt.plot(p_ps_rwd_tan[0], p_ps_rwd_tan[1], 'o', color='green', label='Pressure Side End')
plt.plot(p_ps_rwd_crv[0], p_ps_rwd_crv[1], 'o', color='green', label='Pressure Side End')

plt.plot(p_ss_fwd_tan[0], p_ss_fwd_tan[1], 'o', color='red', label='Suction Side End')
plt.plot(p_ss_fwd_crv[0], p_ss_fwd_crv[1], 'o', color='red', label='Suction Side End')
plt.plot(p_ss_rwd_tan[0], p_ss_rwd_tan[1], 'o', color='red', label='Suction Side End')
plt.plot(p_ss_rwd_crv[0], p_ss_rwd_crv[1], 'o', color='red', label='Suction Side End')

plt.plot(p_le_ps_tan[0], p_le_ps_tan[1], 'o', color='blue', label='Leading Edge End')
plt.plot(p_le_ps_crv[0], p_le_ps_crv[1], 'o', color='blue', label='Leading Edge End')
plt.plot(p_le_ss_tan[0], p_le_ss_tan[1], 'o', color='blue', label='Leading Edge End')
plt.plot(p_le_ss_crv[0], p_le_ss_crv[1], 'o', color='blue', label='Leading Edge End')

plt.plot(p_te_ps_tan[0], p_te_ps_tan[1], 'o', color='cyan', label='Trailing Edge End')
plt.plot(p_te_ps_crv[0], p_te_ps_crv[1], 'o', color='cyan', label='Trailing Edge End')
plt.plot(p_te_ss_tan[0], p_te_ss_tan[1], 'o', color='cyan', label='Trailing Edge End')
plt.plot(p_te_ss_crv[0], p_te_ss_crv[1], 'o', color='cyan', label='Trailing Edge End')

# plt.plot(p_te_org[0], p_te_org[1], 'o', color='black', label='Trailing Edge Start')
# plt.plot(p_te_end[0], p_te_end[1], 'o', color='black', label='Trailing Edge End')
# plt.plot(p_te_t[0], p_te_t[1], 'o', color='black', label='Trailing Edge End')
# plt.plot(p_te_d[0], p_te_d[1], 'o', color='black', label='Trailing Edge End')

# plt.plot(le_constr[0, :], le_constr[1, :], 'r-', label='Leading Edge')
# plt.plot(te_constr[0, :], te_constr[1, :], 'b-', label='Trailing Edge')
# plt.plot(ps_constr[0, :], ps_constr[1, :], 'g-', label='Pressure Side')
# plt.plot(ss_constr[0, :], ss_constr[1, :], 'y-', label='Suction Side')

# Add scatter plots for control points
#plt.scatter(le_constr[0, :], le_constr[1, :], color='r')
#plt.scatter(te_constr[0, :], te_constr[1, :], color='b')
#plt.scatter(ps_constr[0, :], ps_constr[1, :], color='g')
#plt.scatter(ss_constr[0, :], ss_constr[1, :], color='y')

plt.plot(le_spline[0], le_spline[1], color='r')
plt.plot(te_spline[0], te_spline[1], color='b')
plt.plot(ss_spline[0], ss_spline[1], color='g')
plt.plot(ps_spline[0], ps_spline[1], color='y')

plt.axis('equal')  # <-- Use this to set equal aspect ratio for the current axes
plt.legend()
plt.show()