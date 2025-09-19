import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

u_start = [[0.03999127, 0.2,        0.88999564, 0.98999564],
           [0.02501396, 0.08972666, 0.03169268, 0.00499127],
           [0.,         0.,         0.,         0.        ]]

u_end = [[0.03999127, 0.2,        0.88999564, 0.98999564],
         [0.12501396, 0.18972666, 0.13169268, 0.10499127],
         [0.3,        0.3  ,      0.3  ,      0.3       ]]

v_start = [[0.03999127, 0.03999127, 0.03999127],
           [0.02501396, 0.12501396, 0.12501396],
           [0. ,         0.2   ,     0.3       ]]

v_end = [[0.98999564,  0.98999564, 0.98999564],
         [0.00499127,  0.10499127, 0.10499127],
         [0. ,          0.2   ,     0.3       ]]

# Build the 4x3 grid of control points by interpolation
control_points = np.zeros((4, 3, 3))  # (u, v, xyz)

for u in range(4):
    for v in range(3):
        # Interpolate between u_start and u_end for each u, along v
        p0 = np.array([u_start[0][u], u_start[1][u], u_start[2][u]])
        p1 = np.array([u_end[0][u], u_end[1][u], u_end[2][u]])
        t = v / 2.0  # v in [0,1,2] for 3 points
        control_points[u, v, :] = (1 - t) * p0 + t * p1

for v in range(3):
    for u in range(4):
        # Interpolate between v_start and v_end for each v, along u
        p0 = np.array([v_start[0][v], v_start[1][v], v_start[2][v]])
        p1 = np.array([v_end[0][v], v_end[1][v], v_end[2][v]])
        t = u / 3.0  # u in [0,1,2,3] for 4 points
        # Average with previous value for smooth grid
        control_points[u, v, :] = (control_points[u, v, :] + ((1 - t) * p0 + t * p1)) / 2

# Optionally, print or use the grid
print("Control points grid (4x3x3):")
print(control_points)

def draw_dashed_line(p1, p2, dash_length=0.02, gap_length=0.02):
    """Draw a dashed line between p1 and p2."""
    p1 = np.array(p1)
    p2 = np.array(p2)
    diff = p2 - p1
    length = np.linalg.norm(diff)
    direction = diff / length if length != 0 else diff
    n_dashes = int(length // (dash_length + gap_length))
    for i in range(n_dashes + 1):
        start = p1 + direction * (i * (dash_length + gap_length))
        end = start + direction * dash_length
        if np.linalg.norm(end - p1) > length:
            end = p2
        glBegin(GL_LINES)
        glVertex3fv(start)
        glVertex3fv(end)
        glEnd()

# Add rotation state
rot_x, rot_y = 20, -30
last_x, last_y = 0, 0
dragging = False

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0.5, 0.15, 2.0, 0.5, 0.15, 0.0, 0, 1, 0)
    glRotatef(rot_x, 1, 0, 0)
    glRotatef(rot_y, 0, 1, 0)
    glPointSize(8)
    glColor3f(1.0, 1.0, 0.0)  # yellow
    glBegin(GL_POINTS)
    for u in range(control_points.shape[0]):
        for v in range(control_points.shape[1]):
            glVertex3fv(control_points[u, v])
    glEnd()

    # Draw dashed lines in u direction (along v)
    glColor3f(1.0, 1.0, 0.0)
    for u in range(control_points.shape[0]):
        for v in range(control_points.shape[1] - 1):
            draw_dashed_line(control_points[u, v], control_points[u, v + 1])

    # Draw dashed lines in v direction (along u)
    for v in range(control_points.shape[1]):
        for u in range(control_points.shape[0] - 1):
            draw_dashed_line(control_points[u, v], control_points[u + 1, v])

    glutSwapBuffers()

def reshape(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / float(height), 0.1, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def keyboard(key, x, y):
    global rot_x, rot_y
    if key == b'\x1b':  # ESC
        glutLeaveMainLoop()
    elif key == b'w':
        rot_x -= 5
        glutPostRedisplay()
    elif key == b's':
        rot_x += 5
        glutPostRedisplay()
    elif key == b'a':
        rot_y -= 5
        glutPostRedisplay()
    elif key == b'd':
        rot_y += 5
        glutPostRedisplay()

def special_keys(key, x, y):
    global rot_x, rot_y
    if key == GLUT_KEY_UP:
        rot_x -= 5
    elif key == GLUT_KEY_DOWN:
        rot_x += 5
    elif key == GLUT_KEY_LEFT:
        rot_y -= 5
    elif key == GLUT_KEY_RIGHT:
        rot_y += 5
    glutPostRedisplay()

def mouse(button, state, x, y):
    global dragging, last_x, last_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            dragging = True
            last_x, last_y = x, y
        elif state == GLUT_UP:
            dragging = False

def motion(x, y):
    global rot_x, rot_y, last_x, last_y
    if dragging:
        rot_y += (x - last_x)
        rot_x += (y - last_y)
        last_x, last_y = x, y
        glutPostRedisplay()

def visualize_control_points():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"NURBS Surface Control Grid")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutMainLoop()



if __name__ == "__main__":
    print("Control points grid (4x3x3):")
    print(control_points)
    visualize_control_points()