from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import
import math

from obj.car import Wheels

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
    
def draw_cube():
    """Draw a simple cube."""
    glBegin(GL_QUADS)
    # Define vertices for a cube
    glColor3f(1, 0, 0)  # Red
    glVertex3f(-1, -1, -1)
    glVertex3f(-1, 1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(1, -1, -1)
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

def draw_airfoil(self, segment):
    """Draw an airfoil using coordinates from a file, extruded along the z-axis."""
    glLineWidth(2)
    le = segment.geom['le']
    te = segment.geom['te']
    ps = segment.geom['ps']
    ss = segment.geom['ss']

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

def draw_wing(self, wing, no_of_segments):
    """Draw a wing using coordinates from a file, extruded along the z-axis."""
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

        z_parent = getattr(segment_parent, 'origin_Z', 0)
        z_child = getattr(segment_child, 'origin_Z', 0)

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

