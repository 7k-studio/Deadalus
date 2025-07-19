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

def draw_origin_arrows(self, zoom, origin_x, origin_y, origin_z, quality=32):
    """Draw a tube from given origin."""
    diameter = 0.008 * zoom
    length = 0.075
    arrow = length + 0.02

    glLineWidth(2)
    
    # X Axis
    glColor3f(1, 0, 0) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter / 3) * math.cos(angle)
        z = origin_z + (diameter / 3) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(origin_x, y, z)
        glVertex3f(origin_x-(length * zoom), y, z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x-(arrow*zoom), origin_y, origin_z)
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(origin_x-(length*zoom), y, z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x-(length*zoom), origin_y, origin_z) 
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(origin_x-(length*zoom), y, z)
    glEnd()


    # Y Axis
    glColor3f(0, 1, 0) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 3) * math.cos(angle)
        z = origin_z + (diameter / 3) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, origin_y, z)
        glVertex3f(x, origin_y-(length * zoom), z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y-(arrow*zoom), origin_z)  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_y + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(x, origin_y-(length*zoom), z)
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y-(length*zoom), origin_z) 
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(x, origin_y-(length*zoom), z)
    glEnd()



    # Z Axis
    glColor3f(0, 0, 1) # Set tube color to dark grey
    angle_step = 2 * math.pi / quality

    glBegin(GL_QUAD_STRIP)
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter / 3) * math.cos(angle)
        y = origin_y + (diameter / 3) * math.sin(angle)

        # Draw the top and bottom vertices of the tube
        glVertex3f(x, y, origin_z)
        glVertex3f(x, y, origin_z - (length * zoom))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z-(arrow*zoom))  # Center of the base circle
    for i in range(quality + 1):
        angle = i * angle_step
        y = origin_y + (diameter) * math.cos(angle)
        z = origin_z + (diameter) * math.sin(angle)
        glVertex3f(x, y, origin_z-(length*zoom))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(origin_x, origin_y, origin_z-(length*zoom)) 
    for i in range(quality + 1):
        angle = i * angle_step
        x = origin_x + (diameter) * math.cos(angle)
        y = origin_y + (diameter) * math.sin(angle)
        glVertex3f(x, y, origin_z-(length*zoom))
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