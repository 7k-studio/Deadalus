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

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import
import numpy as np
import math
from geomdl import BSpline, utilities

from src.obj.car import Wheels

def draw_tube(self, origin_x, origin_y, origin_z, diameter, width, quality=32):
    """Draw a tube from given origin."""
    glLineWidth(2)
    glColor3f(0.5, 0.5, 0.5) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z)
        glVertex3f(x, y, origin_z + width)
    glEnd()

    # Draw the end caps
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z)  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)
        glVertex3f(x, y, origin_z + width)
    glEnd()

    glColor3f(0.0, 0.0, 0.0)  # Black color for edges
    glBegin(GL_LINES)

    x_old = origin_x + (diameter / 2) * math.cos(0)
    y_old = origin_y + (diameter / 2) * math.sin(0)

    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z)
        glVertex3f(x_old, y_old, origin_z)

        x_old = x
        y_old = y
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z)  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)
        glVertex3f(x, y, origin_z + width)
    glEnd()

    glColor3f(0.0, 0.0, 0.0)  # Black color for edges
    glBegin(GL_LINES)
    x_old = origin_x + (diameter / 2) * math.cos(0)
    y_old = origin_y + (diameter / 2) * math.sin(0)

    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 2) * math.cos(angle)
        y = origin_y + (diameter / 2) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z + width)
        glVertex3f(x_old, y_old, origin_z + width)

        x_old = x
        y_old = y
    glEnd()
    
def draw_cube(origin_x, origin_y, origin_z, width):
    """Draw a simple cube."""
    glBegin(GL_LINES)
    # Define vertices for a cube
    glColor3f(0, 1, 0)  # Green
    glVertex3f(origin_x, origin_y-width/2, origin_z)
    glVertex3f(origin_x, origin_y+width/2, origin_z)
    glVertex3f(origin_x-width, origin_y+width/2, origin_z)
    glVertex3f(origin_x-width, origin_y-width/2, origin_z)
    # Add other faces...
    glEnd()
    
def draw_object_from_file(filepath, extrusion=1.0):
    """Draw an object using coordinates from a file, extruded along the z-axis."""
    vertices = []
    with open(filepath, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith("Name:"):
                x, y = map(float, line.split())
                vertices.append((x, y))

    #print(vertices)
    # Create front and back faces
    front_face = [(x, y, 0) for x, y in vertices]
    back_face = [(x, y, extrusion) for x, y in vertices]

    # Draw the front and back faces
    glColor3f(0.5, 0.5, 0.5)  # Grey color
    glBegin(GL_QUADS)
    for i in range(len(vertices) - 1):
        # Front face
        glVertex3f(*front_face[i])
        glVertex3f(*front_face[i + 1])
        glVertex3f(*back_face[i + 1])
        glVertex3f(*back_face[i])
    glEnd()

    # Draw edges connecting front and back faces
    glColor3f(0.0, 0.0, 0.0)  # Black color for edges
    glBegin(GL_LINES)
    for i in range(len(vertices)):
        glVertex3f(*front_face[i])
    for i in range(len(vertices)):
        glVertex3f(*back_face[i])
    glEnd()

def draw_wing(self, wing, no_of_segments):
    """Draw a wing using coordinates from a file, extruded along the z-axis."""
    print('Drawing wing')
    glColor3f(0.5, 0.5, 0.5)  # Grey color for the wing

    for seg_idx in range(no_of_segments - 1):
        segment_parent = wing.segments[seg_idx]
        segment_child = wing.segments[seg_idx + 1]

        ps_parent = segment_parent.geom['ps']  # list of (x, y)
        ps_child = segment_child.geom['ps']  # list of (x, y)

        ss_parent = segment_parent.geom['ss']  # list of (x, y)
        ss_child = segment_child.geom['ss']  # list of (x, y)

        le_parent = segment_parent.geom['le']  # list of (x, y)
        le_child = segment_child.geom['le']  # list of (x, y)

        te_parent = segment_parent.geom['te']  # list of (x, y)
        te_child = segment_child.geom['te']  # list of (x, y)

        z_parent = segment_parent.params['origin_Z']
        z_child = segment_child.params['origin_Z']

        if ps_parent is None or ps_child is None or len(ps_parent) != len(ps_child):
            print(f"Invalid airfoil data for segments {seg_idx} and {seg_idx + 1}:")
            continue

        glBegin(GL_QUADS)
        for i in range(len(ps_parent[0]) - 1):
            glVertex3f(ps_parent[0][i],     ps_parent[1][i],     z_parent)
            glVertex3f(ps_parent[0][i+1],   ps_parent[1][i+1],   z_parent)
            glVertex3f(ps_child[0][i+1],   ps_child[1][i+1],   z_child)
            glVertex3f(ps_child[0][i],     ps_child[1][i],     z_child)
        glEnd()

        glBegin(GL_QUADS)
        for i in range(len(ss_parent[0]) - 1):
            glVertex3f(ss_parent[0][i],     ss_parent[1][i],     z_parent)
            glVertex3f(ss_parent[0][i+1],   ss_parent[1][i+1],   z_parent)
            glVertex3f(ss_child[0][i+1],   ss_child[1][i+1],   z_child)
            glVertex3f(ss_child[0][i],     ss_child[1][i],     z_child)
        glEnd()

        glBegin(GL_QUADS)
        for i in range(len(le_parent[0]) - 1):
            glVertex3f(le_parent[0][i],     le_parent[1][i],     z_parent)
            glVertex3f(le_parent[0][i+1],   le_parent[1][i+1],   z_parent)
            glVertex3f(le_child[0][i+1],   le_child[1][i+1],   z_child)
            glVertex3f(le_child[0][i],     le_child[1][i],     z_child)
        glEnd()

        glBegin(GL_QUADS)
        for i in range(len(te_parent[0]) - 1):
            glVertex3f(te_parent[0][i],     te_parent[1][i],     z_parent)
            glVertex3f(te_parent[0][i+1],   te_parent[1][i+1],   z_parent)
            glVertex3f(te_child[0][i+1],   te_child[1][i+1],   z_child)
            glVertex3f(te_child[0][i],     te_child[1][i],     z_child)
        glEnd()

def draw_b_spline_surf(segment):
    """
    Create a NURBS surface from a 2D grid of control points.

    control_grid: list of rows (u-direction), each row is list of [x,y,z] points
                  shape = [n_u][n_v], with n_u, n_v in [2..6]
    """

    for key in ['le', 'ps', 'te', 'ss']:
        face = segment.surfaces[key]
        if face != []:
            
            #current_front = glGetIntegerv(GL_FRONT_FACE)

            glColor3f(0.8, 0.8, 0.9)
            for quad in face:
                p0, p1, p2, p3 = quad
                glBegin(GL_QUADS)
                glVertex3fv(p0)
                glVertex3fv(p1)
                glVertex3fv(p2)
                glVertex3fv(p3)
                glEnd()
            
            # Restore front face state
            #glFrontFace(current_front)