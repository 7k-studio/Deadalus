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
import logging
import math
import numpy as np

from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d

class Line:
    def __init__(self):
        self.start_point = []
        self.end_point = []
        self.geom = []
    
    def create(self):
        self.geom = self.start_point
        self.geom.append(self.end_point)

class BSpline:
    def __init__(self, program):
        self.DEADALUS = program
        self.control_points = []
        self.geom = []
    
    def create(self, degree=None, resolution=None):
        print('Control poiints', self.control_points)
        coords = [np.array(c) for c in self.control_points]
        print('Coords:', coords)
        l = len(coords[0])  # number of control points
        
        if degree == None:
            degree = len(self.control_points[0])-1
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
            f = int(self.DEADALUS.preferences['general']['performance'])
        else:
            f = resolution

        u3=np.linspace(0,1,(max(l*f/100,f)),endpoint=True)
        
        self.geom = splev(u3, tck)