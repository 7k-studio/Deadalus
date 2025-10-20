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
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import
import math

from src.obj.car import Wheels
from src.globals import PROJECT

logger = logging.getLogger(__name__)

def draw_airfoil_wireframe(self, component_idx, wing_idx, segment_idx):
    """Draw an airfoil using coordinates from a file, extruded along the z-axis."""
    glLineWidth(2)

    segment = PROJECT.project_components[component_idx].wings[wing_idx].segments[segment_idx]
    le = segment.geom['le']
    te = segment.geom['te']
    ps = segment.geom['ps']
    ss = segment.geom['ss']

    if not all(arr is not None and len(arr) > 0 for arr in [le, te, ps, ss]):
        logger.error("Invalid airfoil data")
        return
    
    color = {'le': [0.0, 0.0, 1.0], 
             'te': [1.0, 1.0, 0.0], 
             'ps': [0.0, 1.0, 0.0], 
             'ss': [1.0, 0.0, 0.0], 
             'le_ps': [0.0, 1.0, 0.0], 
             'le_ss': [1.0, 0.0, 0.0],
             'te_ps': [0.0, 1.0, 0.0],
             'te_ss': [1.0, 0.0, 0.0]}

    for key in ['le', 'te', 'ps', 'ss', 'le_ps', 'le_ss', 'te_ps', 'te_ss']:
        if len(segment.geom[key]) > 0:
            # Draw edges connecting front and back faces
            glColor3f(color[key][0], color[key][1], color[key][2])
            glBegin(GL_LINES)
            for i in range(len(le[0])-1):
                glVertex3f(segment.geom[key][0][i], segment.geom[key][1][i], segment.geom[key][2][i])
                glVertex3f(segment.geom[key][0][i+1], segment.geom[key][1][i+1], segment.geom[key][2][i+1])
            glEnd()


def draw_connection_wireframe(self, segment):
    """Draw an airfoil using coordinates from a file, extruded along the z-axis."""
    glLineWidth(2)
    le_ps = segment.geom['le_ps']
    te_ps = segment.geom['te_ps']
    le_ss = segment.geom['le_ss']
    te_ss = segment.geom['te_ss']

    if not all(arr is not None and len(arr) > 0 for arr in [le_ps, te_ps, le_ss, te_ss]):
        logger.error("Invalid airfoil data:", segment.geom)
        return

    # Draw edges connecting front and back faces
    glColor3f(0.0, 0.0, 1.0)  # Blue color for leading edge
    glBegin(GL_LINES)
    for i in range(len(le_ps[0])-1):
        glVertex3f(le_ps[0][i], le_ps[1][i], segment.params['origin_Z'])
        glVertex3f(le_ps[0][i+1], le_ps[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(0.0, 1.0, 0.0)  # Green color for presssure side
    glBegin(GL_LINES)
    for i in range(len(te_ps[0])-1):
        glVertex3f(te_ps[0][i], te_ps[1][i], segment.params['origin_Z'])
        glVertex3f(te_ps[0][i+1], te_ps[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(1.0, 0.0, 0.0)  # Red color for suction side
    glBegin(GL_LINES)
    for i in range(len(le_ss[0])-1):
        glVertex3f(le_ss[0][i], le_ss[1][i], segment.params['origin_Z'])
        glVertex3f(le_ss[0][i+1], le_ss[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(1.0, 1.0, 0.0)  # Yellow color for trailing edge
    glBegin(GL_LINES)
    for i in range(len(te_ss[0])-1):
        glVertex3f(te_ss[0][i], te_ss[1][i], segment.params['origin_Z'])
        glVertex3f(te_ss[0][i+1], te_ss[1][i+1], segment.params['origin_Z'])
    glEnd()