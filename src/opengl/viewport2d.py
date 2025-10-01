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
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QFont
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_10
from OpenGL.GLU import gluOrtho2D, gluProject  # Add this import
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QFileDialog
from PyQt5.QtOpenGL import QGLWidget
import math
import numpy as np

#from .test_cube import draw_object_from_file  # Import the new function
from . import construction
from . import wireframe
from . import solid
from . import bckgrd

import src.globals as globals

import src.obj.objects2D as objects2D

class ViewportOpenGL(QGLWidget):
    def __init__(self, parent=None):
        super(ViewportOpenGL, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zoom = 2.0
        self.translation = [-0.5, 0, 0]
        self.lastPos = QPoint()
        self.airfoil = None
        self.reference = None
        self.viewport_settings = globals.DEADALUS.preferences["airfoil_designer"]["viewport"]
        self.airfoil_settings = globals.DEADALUS.preferences["airfoil_designer"]["airfoil"]
    
    def set_airfoil_to_display(self, airfoil):
        self.airfoil = airfoil
        self.update()
    
    def set_reference_to_display(self, reference):
        self.reference = reference
        self.update()

    def initializeGL(self):
        glutInit()  # Initialize GLUT to enable text rendering
        glClearColor(250/255, 250/255, 250/255, 1)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / h if h > 0 else 1
        half_width = self.zoom * aspect
        half_height = self.zoom
        gluOrtho2D(-half_width, half_width, -half_height, half_height)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.translation[0], self.translation[1], 0)

        #Drawing background elements
        if self.viewport_settings["grid"]["show"] == True:
            self.draw_grid()
        if self.viewport_settings["ruler"]["show"] == True:
            self.draw_ruler()

        if self.airfoil:
            self.draw_airfoil(self.airfoil)
            if self.airfoil_settings["control_points"]["show"] == True:
                self.draw_cp_net(self.airfoil, self.zoom)
            if self.airfoil_settings["construction"]["show"] == True:
                self.draw_dashed_line(self.airfoil, 0.01, self.zoom)
        if self.reference: 
            if self.reference.format == 'selig':
                self.draw_airfoil_selig_format(self.reference)
            #self.fit_to_airfoil(self.airfoil)

    def draw_cor(self, position, size=5):
        glPointSize(size)
        glBegin(GL_POINTS)
        glColor3f(1, 0, 0)  # Red color
        glVertex3f(*position)
        glEnd()

    def draw_grid(self):
        glColor3f(0.85, 0.85, 0.85)
        glBegin(GL_LINES)

        if self.zoom < 1.2:
            size = 1000
            step = 1
        if self.zoom > 10:
            size = 1000
            step = 100
        if self.zoom > 1.1 and self.zoom < 10: 
            size = 1000
            step = 10

        for i in range(-size, size+1, step):
            glVertex2f(i/10, -size/10)
            glVertex2f(i/10, size/10)
            glVertex2f(-size/10, i/10)
            glVertex2f(size/10, i/10)
        glEnd()

    def draw_ruler(self, size=20):
        """Draws a ruler with tick marks and labels using OpenGL."""
        glDisable(GL_DEPTH_TEST)
        glColor3f(0.3, 0.3, 0.3)

        # Draw X and Y axes
        glBegin(GL_LINES)
        glVertex2f(-size, 0)
        glVertex2f(size, 0)
        glVertex2f(0, -size)
        glVertex2f(0, size)
        glEnd()

        # Draw tick marks and labels
        tick_spacing = 1.0  # Adjust tick spacing based on zoom level
        if self.zoom > 10:
            tick_spacing = 10.0
        elif self.zoom > 2:
            tick_spacing = 1.0
        elif self.zoom < 1:
            tick_spacing = 0.1

        # X-axis ticks and labels
        for x in self.frange(-size, size, tick_spacing):
            glBegin(GL_LINES)
            glVertex2f(x, -0.02*self.zoom)
            glVertex2f(x, 0.02*self.zoom)
            glEnd()
            if x != 0:  # Avoid drawing "0" at the origin twice
                self.draw_text(f"{x:.1f}m", x, -self.zoom*0.1)

        # Y-axis ticks and labels
        for y in self.frange(-size, size, tick_spacing):
            glBegin(GL_LINES)
            glVertex2f(-0.02*self.zoom, y)
            glVertex2f(0.02*self.zoom, y)
            glEnd()
            if y != 0:  # Avoid drawing "0" at the origin twice
                self.draw_text(f"{y:.1f}m", -self.zoom*0.1, y)

        glEnable(GL_DEPTH_TEST)

    def draw_text(self, text, x, y):
        """Renders text at the specified (x, y) position using OpenGL."""
        glColor3f(0, 0, 0)  # Black color for text
        glRasterPos2f(x, y)
        for char in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord(char))

    def frange(self, start, stop, step):
        """Range for floats."""
        while start < stop:
            yield start
            start += step

    def world_to_screen(self, x, y):
        """Map OpenGL world coords → Qt screen coords for text placement."""
        model = glGetDoublev(GL_MODELVIEW_MATRIX)
        proj = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        winX, winY, winZ = gluProject(x, y, 0.0, model, proj, viewport)
        return winX, self.height() - winY  # flip Y for Qt

    def mousePressEvent(self, event):
        self.lastPos = event.pos()
        self.show_dot = True
        self.update()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.translation[0] += dx * (self.zoom / 300)
            self.translation[1] -= dy * (self.zoom / 300)

        self.lastPos = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom *= 0.9  # zoom in
        else:
            self.zoom *= 1.1  # zoom out
        self.resizeGL(self.width(), self.height())
        self.update()

    def mouseReleaseEvent(self, event):
        self.show_dot = False
        self.update()

    def toggle_projection(self):
        """Toggle between perspective and orthogonal views."""
        self.orthogonal = not self.orthogonal
        #self.resizeGL(self.width(), self.height())  # Ensure projection matrix is updated
        self.resizeGL(1200, 800)
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_P:
            self.toggle_projection()
        self.update()
        #return super().keyPressEvent(a0)

    def draw_airfoil(self, Current_Airfoil):
        '''
        Plots an airfoil based on objects Airfoil stored in obj.arf.py defined by folowing gorup of parameters:

        Base parameters:
            chord, origin_X, origin_Y
        Leading Edge parameters:
            le_thickness, le_depth, le_offset, le_angle
        Trailing Edge parameters:
            te_thickness, te_depth, te_offset, te_angle
        Pressure Side parameters:
            ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel
        Suction Side parameters:    
            ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel
        '''

        # Extract parameters
        Current_Airfoil.update()
        glDisable(GL_DEPTH_TEST)
    
        color = self.airfoil_settings['wireframe']['color']

        for key in ['le', 'te', 'ps', 'ss']:
            vec_length = len(Current_Airfoil.geom[key][0])
            if vec_length > 0:
                # Draw edges connecting front and back faces
                glColor3f(*color[key])
                glBegin(GL_LINE_STRIP)
                for i in range(vec_length):
                    x = Current_Airfoil.geom[key][0][i]
                    y = Current_Airfoil.geom[key][1][i]
                    glVertex3f(x, y, 0.0)  # force z=0
                glEnd()             
    
    def fit_to_airfoil(self, airfoil):
        xs = airfoil.geom['ps'][0] + airfoil.geom['ss'][0]
        ys = airfoil.geom['ps'][1] + airfoil.geom['ss'][1]
        if not xs or not ys:
            return
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        self.zoom = -max(width, height) * 0.6
        self.translation = [-(min(xs)+max(xs))/2, -(min(ys)+max(ys))/2, 0]

    def draw_cp_net(self, airfoil, zoom):
        
        color = self.airfoil_settings['control_points']['color']
        glPointSize(6.0)

        for key in airfoil.constr:
            glColor3f(color[key][0], color[key][1], color[key][2])
            glBegin(GL_POINTS)
            points = np.array(airfoil.constr[key]).T
            #print(f"{key}: ", points)
            for point in points:
                glVertex3f(point[0], point[1], 0.0)
            glEnd()

    def draw_dashed_line(self, airfoil, base_dash_length=0.01, zoom=1):
        """Draw dashed line between points p1 and p2."""
        from numpy import array, linalg

        for key in airfoil.constr:
            points = np.array(airfoil.constr[key]).T
            z = 0 if key in ['le', 'ps', 'ss', 'te'] else None
            for j in range(len(points) - 1):
                p1 = points[j]
                #print(p1)
                p2 = points[j + 1]
                if z is not None:
                    p1 = [p1[0], p1[1], z]
                    p2 = [p2[0], p2[1], z]
                #print(f"{key}: ", points)

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

    def draw_airfoil_selig_format(self, reference_airfoil):
        '''
        Plots an airfoil based on objects Airfoil stored in obj.arf.py defined by folowing gorup of parameters:

        Base parameters:
            chord, origin_X, origin_Y
        Leading Edge parameters:
            le_thickness, le_depth, le_offset, le_angle
        Trailing Edge parameters:
            te_thickness, te_depth, te_offset, te_angle
        Pressure Side parameters:
            ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel
        Suction Side parameters:    
            ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel
        '''

        # Extract parameters
        #reference_airfoil.update()
        glDisable(GL_DEPTH_TEST)
    
        color = self.airfoil_settings['wireframe']['color']

        vec_length = len(reference_airfoil.top_curve[0])
        if vec_length > 0:
            # Draw edges connecting front and back faces
            glColor3f(0.5,0.5,0.5)
            glBegin(GL_LINE_STRIP)
            for i in range(vec_length):
                x = reference_airfoil.top_curve[0][i]
                y = reference_airfoil.top_curve[1][i]
                glVertex3f(x, y, 0.0)  # force z=0
            glEnd()
        
        vec_length = len(reference_airfoil.dwn_curve[0])
        if vec_length > 0:

            glColor3f(0.5,0.5,0.5)
            glBegin(GL_LINE_STRIP)
            for i in range(vec_length):
                x = reference_airfoil.dwn_curve[0][i]
                y = reference_airfoil.dwn_curve[1][i]
                glVertex3f(x, y, 0.0)  # force z=0
            glEnd()