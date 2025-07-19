from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QFileDialog
from PyQt5.QtOpenGL import QGLWidget
import math

#from .test_cube import draw_object_from_file  # Import the new function
from . import shapes  # Import the shapes module
from . import bckgrd

import src.globals as globals

from src.obj.car import Wheels

Wheels = Wheels()

class ViewportOpenGL(QGLWidget):
    def __init__(self, parent=None):
        super(ViewportOpenGL, self).__init__(parent)
        self.zoom = -10.0
        self.rotation = [0, 0, 0]
        self.translation = [0, 0, 0]
        self.CoR = [0, 0, 0]
        self.lastPos = QPoint()
        self.show_dot = True
        self.orthogonal = False  # Add a flag for orthogonal view

    def initializeGL(self):
        glClearColor(220/255, 220/255, 220/255, 1)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.orthogonal:
            # Set up an orthographic projection
            size = max(1, -self.zoom)  # Ensure size is positive and respects zoom
            aspect = w / h if h != 0 else 1
            glOrtho(-size * aspect, size * aspect, -size, size, 0.1, 50.0)
        else:
            # Set up a perspective projection
            gluPerspective(45, w / h if h != 0 else 1, 0.1, 50.0)

        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.translation[0], self.translation[1], self.zoom)
        glTranslatef(self.CoR[0], self.CoR[1], self.CoR[2])
        glRotatef(self.rotation[0], 1.0, 0.0, 0.0)
        glRotatef(self.rotation[1], 0.0, 1.0, 0.0)
        glRotatef(self.rotation[2], 0.0, 0.0, 1.0)
        glTranslatef(-self.CoR[0], -self.CoR[1], -self.CoR[2])

        #Drawing background elements
        bckgrd.draw_grid(self, linewidth=1, zoom=self.zoom)
        bckgrd.draw_ruller(self, zoom=self.zoom)

        # Drawing objects
        for i in range(len(globals.PROJECT.project_components)):

            bckgrd.draw_origin_arrows(self, zoom=self.zoom, origin_x=globals.PROJECT.project_components[i].params['origin_X'], origin_y=globals.PROJECT.project_components[i].params['origin_Y'], origin_z=globals.PROJECT.project_components[i].params['origin_Z'])
            #print(f"Drawing component {i+1}/{len(globals.PROJECT.project_components)}")

            for j in range(len(globals.PROJECT.project_components[i].wings)):
                #print(f"  Drawing wing {j+1}/{len(globals.PROJECT.project_components[i].wings)}")
                for k in range(len(globals.PROJECT.project_components[i].wings[j].segments)):
                    #print(f"    Drawing segment {k+1}/{len(globals.PROJECT.project_components[i].wings[j].segments)}")
                    try:
                        # Check for errors before drawing
                        error = glGetError()
                        if error != GL_NO_ERROR:
                            print(f"OpenGL Error before airfoil: {(error)}") #gluErrorString

                        shapes.draw_airfoil(self, globals.PROJECT.project_components[i].wings[j].segments[k])
                        shapes.draw_wing(self, globals.PROJECT.project_components[i].wings[j], len(globals.PROJECT.project_components[i].wings[j].segments))
                        # Check for errors after drawing
                        error = glGetError()
                        if error != GL_NO_ERROR:
                            print(f"OpenGL Error after airfoil: {(error)}") #gluErrorString
                    except IndexError:
                        print("No airfoil data available to draw.")

        shapes.draw_tube(self, Wheels.wheel_front_X, Wheels.wheel_front_Y, Wheels.wheel_front_Z, Wheels.diameter, Wheels.width, quality=32)
        shapes.draw_tube(self, Wheels.wheel_rear_X, Wheels.wheel_rear_Y, Wheels.wheel_rear_Z, Wheels.diameter, Wheels.width, quality=32)

    def draw_cor(self, position, size=5):
        glPointSize(size)
        glBegin(GL_POINTS)
        glColor3f(1, 0, 0)  # Red color
        glVertex3f(*position)
        glEnd()

    def mousePressEvent(self, event):
        self.lastPos = event.pos()
        self.show_dot = True
        self.update()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.translation[0] += dx * 0.01
            self.translation[1] -= dy * 0.01
            self.CoR[0] += dx * 0.01
            self.CoR[1] -= dy * 0.01

        self.lastPos = event.pos()
        self.update()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        # Zoom in or out based on the wheel movement
        intensity = pow(math.e, (2*self.zoom+5)) + 120
        self.zoom += event.angleDelta().y() / intensity
        print(f"Zoom level updated: {self.zoom}")  # Print the zoom value to the console
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