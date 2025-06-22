from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QFileDialog
from PyQt5.QtOpenGL import QGLWidget

#from .test_cube import draw_object_from_file  # Import the new function

def draw_origin_arrows(self, linewidth, zoom, X, Y, Z):
    glColor3f(1,0,0)
    glLineWidth(linewidth)
    glBegin(GL_LINES)
    glVertex3f(X, Y, Z)
    glVertex3f(X+0.05*(-zoom), Y, Z)
    glEnd()

    glColor3f(0,1,0)
    #glLineWidth(linewidth)
    glBegin(GL_LINES)
    glVertex3f(X, Y, Z)
    glVertex3f(X, Y+0.05*(-zoom), Z)
    glEnd()

    glColor3f(0,0,1)
    #glLineWidth(linewidth)
    glBegin(GL_LINES)
    glVertex3f(X, Y, Z)
    glVertex3f(X, Y, Z+0.05*(-zoom))
    glEnd()


def draw_grid(self, linewidth=1, size=100, step=1, zoom=-10):
    glLineWidth(linewidth)
    glColor3f(0.8, 0.8, 0.8)  # Grey color
    glBegin(GL_LINES)

    if -zoom < 3:
        scale = 10  # Adjust scale based on zoom level
    else:
        scale = 1

    for i in range(-size, size + 1, step):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/scale, -size, 0)
        glVertex3f(i/scale, size, 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(-size, i/scale, 0)
        glVertex3f(size, i/scale, 0)      
    glEnd()

def draw_ruller(self, linewidth=2, size=1000, step=1, zoom = -10):
    glLineWidth(linewidth)
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_LINES)

    # Adjust scale based on zoom level
    if -zoom < 2:
        scale = 100  
    else:
        scale = 10

    #Drawing ruller lines: main axis
    for i in range(-size, size + 1, step):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/scale, 0, 0)
        glVertex3f(i/scale, 0.01*(-zoom), 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(0, i/scale, 0)
        glVertex3f(0.01*(-zoom), i/scale, 0)
    for i in range(0, 40 + 1, step):
        # Depth lines [ X | Y | Z ]
        glVertex3f(0, 0, i/scale)
        glVertex3f(0.01*(-zoom), 0, i/scale)

    for i in range(-size, size + 1, int(step*10)):
        # Vertical lines [ X | Y | Z ]
        glVertex3f(i/10, 0, 0)
        glVertex3f(i/10, 0.2, 0)
        # Horizontal lines [ X | Y | Z ]
        glVertex3f(0, i/10, 0)
        glVertex3f(0.2, i/10, 0)
    for i in range(0, 40 + 1, int(step*10)):
        # Depth lines [ X | Y | Z ]
        glVertex3f(0, 0, i/10)
        glVertex3f(0.2, 0, i/10)

    glVertex3f(-size, 0, 0)
    glVertex3f(size + 1, 0, 0)

    glVertex3f(0, -size, 0)
    glVertex3f(0, size + 1, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 4 + 1)  
    
    glEnd()