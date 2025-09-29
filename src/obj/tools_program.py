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
#import src.globals as globals
import numpy as np
from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d

def normalize(vector):
    length = sum(x ** 2 for x in vector) ** 0.5
    if length == 0:
        return vector
    return [x / length for x in vector]

def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)

def lerp(start, end, t):
    return start + (end - start) * t

def deg2rad(degrees):
    return degrees * (math.pi / 180)

def rad2deg(radians):
    return radians * (180 / math.pi)

def convert_ndarray_to_list(obj):
    """Recursively convert numpy arrays in dict/list to lists."""
    if isinstance(obj, dict):
        return {k: convert_ndarray_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarray_to_list(i) for i in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
    
def convert_list_to_ndarray(obj):
    """Recursively convert lists in the object to numpy arrays where appropriate."""
    if isinstance(obj, list):
        # Only convert to ndarray if all elements are numbers or all are lists (for arrays of arrays)
        if all(isinstance(x, (int, float, complex)) for x in obj):
            return np.array(obj)
        elif all(isinstance(x, list) for x in obj):
            return np.array([convert_list_to_ndarray(x) for x in obj])
        else:
            return [convert_list_to_ndarray(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: convert_list_to_ndarray(v) for k, v in obj.items()}
    else:
        return obj
    
def CreateBSpline(const_points):

    l=len(const_points[0])

    t=np.linspace(0,1,l-2,endpoint=True)
    t=np.append([0,0,0],t)
    t=np.append(t,[1,1,1])

    tck=[t,[const_points[0],const_points[1]],3]

    
    # Use a faster method for performance
    u3=np.linspace(0,1,(max(l*3,75)),endpoint=True)

    spline = splev(u3, tck)

    return spline

def CreateBSpline_3D(const_points, degree, resolution=None):
    coords = [np.array(c) for c in const_points]
    l = len(coords[0])  # number of control points
    
    # Safety: adjust degree if not enough points
    degree = min(degree, l - 1)
    
    # Knot vector for clamped B-spline
    t = np.concatenate((
        np.zeros(degree),                   # start knots
        np.linspace(0, 1, l - degree + 1),  # interior knots
        np.ones(degree)                     # end knots
    ))
    
    tck = [t, coords, degree]
    
    # Sampling resolution
    if resolution == None:
        f = int(globals.DEADALUS.preferences['general']['performance'])
    else:
        f = resolution

    u3=np.linspace(0,1,(max(l*f/100,f)),endpoint=True)
    
    spline = splev(u3, tck)

    return spline

def safe_date(val):
    import datetime
    if isinstance(val, (datetime.date, datetime.datetime)):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return val

def vec_translate(points, magnitude, angle):
    print(points)
    angle_radians = deg2rad(angle)
    dx = magnitude * math.cos(angle_radians)
    dy = magnitude * math.sin(angle_radians)

    translated_points = [points[0] + dx, points[1] + dy]

    return translated_points