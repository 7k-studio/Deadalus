from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import gluPerspective  # Add this import

def draw_cube(self, size=1.0):
    """Draw a cube centered at the origin."""
    vertices = [
        [-size, -size, -size],
        [size, -size, -size],
        [size, size, -size],
        [-size, size, -size],
        [-size, -size, size],
        [size, -size, size],
        [size, size, size],
        [-size, size, size],
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
        (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
        (0, 4), (1, 5), (2, 6), (3, 7),  # Connecting edges
    ]
    glColor3f(0.0, 0.0, 1.0)  # Set cube color to blue
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def draw_cube_2():
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

