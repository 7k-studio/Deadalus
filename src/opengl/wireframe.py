from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import
import math

from src.obj.car import Wheels

def draw_airfoil_wireframe(self, segment):
    """Draw an airfoil using coordinates from a file, extruded along the z-axis."""
    glLineWidth(2)
    try:
        le = segment.geom['le']
        te = segment.geom['te']
        ps = segment.geom['ps']
        ss = segment.geom['ss']
    except AttributeError:
        segment.update_airfoil()
        

    if not all(arr is not None and len(arr) > 0 for arr in [le, te, ps, ss]):
        print("Invalid airfoil data:", segment.geom)
        return

    # Draw edges connecting front and back faces
    glColor3f(0.0, 0.0, 1.0)  # Blue color for leading edge
    glBegin(GL_LINES)
    for i in range(len(le[0])-1):
        glVertex3f(le[0][i], le[1][i], segment.params['origin_Z'])
        glVertex3f(le[0][i+1], le[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(0.0, 1.0, 0.0)  # Green color for presssure side
    glBegin(GL_LINES)
    for i in range(len(ps[0])-1):
        glVertex3f(ps[0][i], ps[1][i], segment.params['origin_Z'])
        glVertex3f(ps[0][i+1], ps[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(1.0, 0.0, 0.0)  # Red color for suction side
    glBegin(GL_LINES)
    for i in range(len(ss[0])-1):
        glVertex3f(ss[0][i], ss[1][i], segment.params['origin_Z'])
        glVertex3f(ss[0][i+1], ss[1][i+1], segment.params['origin_Z'])
    glEnd()

    glColor3f(1.0, 1.0, 0.0)  # Yellow color for trailing edge
    glBegin(GL_LINES)
    for i in range(len(te[0])-1):
        glVertex3f(te[0][i], te[1][i], segment.params['origin_Z'])
        glVertex3f(te[0][i+1], te[1][i+1], segment.params['origin_Z'])
    glEnd()

def draw_connection_wireframe(self, segment):
    """Draw an airfoil using coordinates from a file, extruded along the z-axis."""
    glLineWidth(2)
    le_ps = segment.geom['le_ps']
    te_ps = segment.geom['te_ps']
    le_ss = segment.geom['le_ss']
    te_ss = segment.geom['te_ss']

    if not all(arr is not None and len(arr) > 0 for arr in [le_ps, te_ps, le_ss, te_ss]):
        print("Invalid airfoil data:", segment.geom)
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