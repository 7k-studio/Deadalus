'''

Copyright (C) 2025 Jakub Kamyk

This file is part of AirFLOW.

AirFLOW is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

AirFLOW is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AirFLOW.  If not, see <http://www.gnu.org/licenses/>.

'''

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import
import math
import numpy as np

from src.obj.car import Wheels

def draw_cp_net(object, zoom):
    glPointSize(8.0)
    glColor3f(1, 1, 0)  # Yellow points
    glBegin(GL_POINTS)

    for i in range(len(object.segments)):
        for key in object.segments[i].control_points:
            points = np.array(object.segments[i].control_points[key]).T
            for point in points:
                z = object.segments[i].params['origin_Z'] if key in ['le', 'ps', 'ss', 'te'] else point[2]
                glVertex3f(point[0], point[1], z)
    glEnd()

    # Now draw dashed lines
    for i in range(len(object.segments)):
        for key in object.segments[i].control_points:
            points = np.array(object.segments[i].control_points[key]).T
            z = object.segments[i].params['origin_Z'] if key in ['le', 'ps', 'ss', 'te'] else None
            for j in range(len(points) - 1):
                p1 = points[j]
                p2 = points[j + 1]
                if z is not None:
                    p1 = [p1[0], p1[1], z]
                    p2 = [p2[0], p2[1], z]
                draw_dashed_line(p1, p2, zoom=zoom)

def draw_dashed_line(p1, p2, base_dash_length=0.01, zoom=1):
    """Draw dashed line between points p1 and p2."""
    from numpy import array, linalg

    zoom = abs(zoom) if zoom != 0 else 0.001  # avoid divide-by-zero
    dash_length = base_dash_length * zoom

    p1 = array(p1)
    p2 = array(p2)
    vec = p2 - p1
    length = linalg.norm(vec)
    dir_vec = vec / length 

    num_dashes = int(length / (2 * dash_length))
    for i in range(num_dashes):
        start = p1 + dir_vec * (2 * i) * dash_length
        end = p1 + dir_vec * (2 * i + 1) * dash_length
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        glVertex3fv(start)
        glVertex3fv(end)
        glEnd()