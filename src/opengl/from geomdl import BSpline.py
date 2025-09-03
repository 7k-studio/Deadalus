from geomdl import BSpline
from geomdl import utilities
import numpy as np

# Example: build a surface from 4 curves (ps, ss, le, te)
# For demo we just fake some data (replace with your curve samples)

def make_curve_points(start, end, n=10):
    """Linear interpolation between start and end (placeholder for your spline evaluator)"""
    return [((1-t)*np.array(start) + t*np.array(end)).tolist() for t in np.linspace(0,1,n)]

# Suppose we have:
# leading edge (LE) and trailing edge (TE) curves sampled along Y
curve_le = make_curve_points([0,0,0], [0,1,0], n=10)   # left side
curve_te = make_curve_points([5,0,0], [5,1,0], n=10)   # right side

# pressure side (PS) and suction side (SS) curves sampled along X
curve_ps = make_curve_points([0,0,0], [5,0,0], n=10)   # bottom
curve_ss = make_curve_points([0,1,0], [5,1,0], n=10)   # top

# Now we need to form a 2D control net grid
# Simplest way: bilinear blending of curves (Coons-style for control points)
n_u, n_v = 10, 10
control_points = []
for i, u in enumerate(np.linspace(0,1,n_u)):
    row = []
    for j, v in enumerate(np.linspace(0,1,n_v)):
        # interpolate between curves
        c0 = (1-v)*np.array(curve_le[j]) + v*np.array(curve_te[j])
        c1 = (1-u)*np.array(curve_ps[i]) + u*np.array(curve_ss[i])
        # average (basic blending, replace with your real spline sampling)
        p = 0.5*(c0 + c1)
        row.append(p.tolist())
    control_points.append(row)

# Flatten the grid for geomdl
ctrlpts2d = control_points   # [u][v][xyz]
ctrlpts_flat = [pt for row in ctrlpts2d for pt in row]

# Build surface
surf = BSpline.Surface()

surf.degree_u = 3
surf.degree_v = 3

surf.set_ctrlpts(ctrlpts_flat, n_u, n_v)

# Generate knot vectors automatically (clamped uniform)
surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, n_u)
surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, n_v)

# Evaluate surface (discretize)
surf.delta = 0.05   # resolution (smaller = finer mesh)
surf.evaluate()

print("Surface points:", len(surf.evalpts))  # evaluated points

'''

Copyright (C) 2025 Jakub Kamyk

This file is part of AirFLOW.

AirFLOW is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

AirFLOW is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AirFLOW.  If not, see <http://www.gnu.org/licenses/>.

'''

import sys
import math
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtOpenGL import QGLFormat
from PyQt5.QtWidgets import QOpenGLWidget

# PyOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

import src.opengl.bckgrd as background
import src.opengl.construction as construction
from src.globals import PROJECT


class Viewport3D(QOpenGLWidget):
    """
    Simple CAD-like OpenGL viewport with:
      - Orbit rotation around a center (target)
      - Pan/translate view
      - Zoom (mouse wheel or right-drag)

    Controls:
      - Left Mouse Drag: Orbit (yaw/pitch)
      - Middle Mouse Drag: Pan (translate target in view plane)
      - Right Mouse Drag: Dolly Zoom (forward/back)
      - Mouse Wheel: Zoom in/out
      - Double-click Left: Reset view
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setMouseTracking(True)

        # Camera / view state
        self.target = QtGui.QVector3D(0.0, 0.0, 0.0)  # center of rotation
        self.distance = 8.0                            # camera distance from target
        self.yaw = 45.0                                # degrees around Y
        self.pitch = 20.0                              # degrees around X (clamped)

        self.fov_y = 45.0                              # field of view
        self.near = 0.05
        self.far = 1000.0

        # Interaction
        self._last_pos = None
        self._active_button = None

        # Pan offsets are stored by moving the target in world space
        # but we compute deltas in view space and transform to world

    # -------- OpenGL setup --------
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glClearColor(0.10, 0.12, 0.14, 1.0)  # dark background

        # Light (very simple)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 8.0, 5.0, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 1.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))

    def resizeGL(self, w, h):
        h = max(1, h)
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov_y, w / float(h), self.near, self.far)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set up camera (orbit around target)
        eye = self._spherical_to_cartesian(self.distance, math.radians(self.yaw), math.radians(self.pitch))
        eye = QtGui.QVector3D(eye[0], eye[1], eye[2]) + self.target

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(eye.x(), eye.y(), eye.z(),
                  self.target.x(), self.target.y(), self.target.z(),
                  0.0, 1.0, 0.0)

        self._draw_grid()
        #self._draw_axes()
        #self._draw_demo_geometry()

        # Drawing objects
        for i in range(len(PROJECT.project_components)):

            background.draw_origin_arrows(self, zoom=self.distance, origin_x=PROJECT.project_components[i].params['origin_X'], origin_y=PROJECT.project_components[i].params['origin_Y'], origin_z=PROJECT.project_components[i].params['origin_Z'])
            #print(f"Drawing component {i+1}/{len(PROJECT.project_components)}")

            for j in range(len(PROJECT.project_components[i].wings)):
                #solid.draw_cube(PROJECT.project_components[i].wings[j].params['origin_X'],PROJECT.project_components[i].wings[j].params['origin_Y'],PROJECT.project_components[i].wings[j].params['origin_Z'],0.2)
                construction.draw_cp_net(PROJECT.project_components[i].wings[j], self.distance)
                #print(f"  Drawing wing {j+1}/{len(PROJECT.project_components[i].wings)}")
                
                for k in range(len(PROJECT.project_components[i].wings[j].segments)):
                    #print(f"    Drawing segment {k+1}/{len(PROJECT.project_components[i].wings[j].segments)}")
                    try:
                        # Check for errors before drawing
                        error = glGetError()
                        if error != GL_NO_ERROR:
                            print(f"OpenGL Error before airfoil: {(error)}") #gluErrorString

                        construction.draw_wireframe(self, i, j, k)
                        
                        #shapes.draw_wing(self, PROJECT.project_components[i].wings[j], len(PROJECT.project_components[i].wings[j].segments))
                        # Check for errors after drawing
                        error = glGetError()
                        if error != GL_NO_ERROR:
                            print(f"OpenGL Error after airfoil: {(error)}") #gluErrorString
                    except IndexError:
                        print("No airfoil data available to draw.")



    # -------- Interaction --------
    def mousePressEvent(self, event):
        self._last_pos = event.pos()
        self._active_button = event.button()
        self.setCursor(QtCore.Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        self._active_button = None
        self._last_pos = None
        self.unsetCursor()

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.reset_view()

    def mouseMoveEvent(self, event):
        if self._last_pos is None or self._active_button is None:
            return
        dx = event.x() - self._last_pos.x()
        dy = event.y() - self._last_pos.y()

        if self._active_button == QtCore.Qt.LeftButton:
            # Orbit (adjust yaw/pitch)
            self.yaw -= dx * 0.4
            self.pitch += dy * 0.3
            self.pitch = max(-89.5, min(89.5, self.pitch))
            self.update()

        elif self._active_button == QtCore.Qt.MidButton:
            # Pan (translate target in the camera's right/up directions)
            self._pan(dx, dy)
            self.update()

        elif self._active_button == QtCore.Qt.RightButton:
            # Dolly zoom (drag vertically)
            self._dolly(dy)
            self.update()

        self._last_pos = event.pos()

    def wheelEvent(self, event):
        # Zoom with wheel (true CAD-feel: scale with distance)
        delta_steps = event.angleDelta().y() / 120.0  # 120 per notch
        factor = math.pow(0.9, delta_steps)           # 10% per notch
        self.distance = max(0.05, self.distance * factor)
        self.update()

    def reset_view(self):
        self.target = QtGui.QVector3D(0.0, 0.0, 0.0)
        self.distance = 8.0
        self.yaw = 45.0
        self.pitch = 20.0
        self.update()

    # -------- Helpers --------
    def _spherical_to_cartesian(self, r, yaw_rad, pitch_rad):
        # Y-up, yaw around +Y, pitch around +X right-handed
        x = r * math.cos(pitch_rad) * math.sin(yaw_rad)
        y = r * math.sin(pitch_rad)
        z = r * math.cos(pitch_rad) * math.cos(yaw_rad)
        return x, y, z

    def _camera_basis(self):
        # Compute camera basis vectors (right, up, forward) in world space
        yaw_r = math.radians(self.yaw)
        pitch_r = math.radians(self.pitch)
        # forward from target to camera is -look vector; we want camera forward (from eye toward target)
        # Build direction from eye to target (negative of eye dir from target)
        fx = -math.cos(pitch_r) * math.sin(yaw_r)
        fy = -math.sin(pitch_r)
        fz = -math.cos(pitch_r) * math.cos(yaw_r)
        forward = QtGui.QVector3D(fx, fy, fz)
        forward.normalize()
        up = QtGui.QVector3D(0.0, 1.0, 0.0)
        right = QtGui.QVector3D.crossProduct(forward, up)
        right.normalize()
        up_corrected = QtGui.QVector3D.crossProduct(right, forward)
        up_corrected.normalize()
        return right, up_corrected, forward

    def _pan(self, dx, dy):
        # Convert pixel delta to world-space move at current depth
        w = max(1, self.width())
        h = max(1, self.height())
        right, up, _ = self._camera_basis()
        # Pixel to world at target depth: scale by tan(fov/2) and distance
        scale_y = 2.0 * self.distance * math.tan(math.radians(self.fov_y * 0.5)) / h
        scale_x = scale_y * (w / float(h))
        move = right * (-dx * scale_x) + up * (dy * scale_y)
        self.target += move

    def _dolly(self, dy):
        # Dragging down (positive dy) increases distance
        factor = math.pow(1.01, dy)
        self.distance = max(0.05, min(self.far * 0.5, self.distance * factor))

    # -------- Drawing helpers --------
    def _draw_axes(self, length=1.5, width=2.0):
        glDisable(GL_LIGHTING)
        glLineWidth(width)
        glBegin(GL_LINES)
        # X - red
        glColor3f(1.0, 0.2, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(length, 0.0, 0.0)
        # Y - green
        glColor3f(0.2, 1.0, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, length, 0.0)
        # Z - blue
        glColor3f(0.2, 0.4, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, length)
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    def _draw_grid(self, half_size=10, step=1.0):
        glDisable(GL_LIGHTING)
        glColor3f(0.35, 0.38, 0.42)
        glBegin(GL_LINES)
        for i in range(-half_size, half_size + 1):
            glVertex3f(i * step, 0.0, -half_size * step)
            glVertex3f(i * step, 0.0, half_size * step)
            glVertex3f(-half_size * step, 0.0, i * step)
            glVertex3f(half_size * step, 0.0, i * step)
        glEnd()
        # Highlight origin axes on grid
        glColor3f(0.55, 0.58, 0.62)
        glBegin(GL_LINES)
        glVertex3f(-half_size * step, 0.0, 0.0)
        glVertex3f(half_size * step, 0.0, 0.0)
        glVertex3f(0.0, 0.0, -half_size * step)
        glVertex3f(0.0, 0.0, half_size * step)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_demo_geometry(self):
        # A lit cube at the origin, so you can see rotation around target
        glPushMatrix()
        glTranslatef(0.0, 0.5, 0.0)
        glScalef(1.0, 1.0, 1.0)
        glColor3f(0.85, 0.85, 0.88)
        self._draw_unit_cube()
        glPopMatrix()

    def _draw_unit_cube(self):
        # Draw a unit cube centered at origin spanning [-0.5, 0.5]
        vertices = [
            (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5), ( 0.5,  0.5,  0.5), (-0.5,  0.5,  0.5),  # front
            (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5), ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5),  # back
        ]
        faces = [
            (0, 1, 2, 3, (0, 0, 1)),   # front
            (1, 5, 6, 2, (1, 0, 0)),   # right
            (5, 4, 7, 6, (0, 0, -1)),  # back
            (4, 0, 3, 7, (-1, 0, 0)),  # left
            (3, 2, 6, 7, (0, 1, 0)),   # top
            (4, 5, 1, 0, (0, -1, 0)),  # bottom
        ]
        glBegin(GL_QUADS)
        for (a, b, c, d, n) in faces:
            glNormal3f(*n)
            glVertex3f(*vertices[a])
            glVertex3f(*vertices[b])
            glVertex3f(*vertices[c])
            glVertex3f(*vertices[d])
        glEnd()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAD-like OpenGL Viewport (PyQt5)")
        self.resize(1000, 700)

        self.viewport = Viewport3D(self)
        self.setCentralWidget(self.viewport)

        # Status bar with quick hints
        self.status = self.statusBar()
        self.status.showMessage("LMB: Orbit | MMB: Pan | RMB/Wheel: Zoom | Double LMB: Reset")


def configure_surface_format():
    fmt = QSurfaceFormat()
    fmt.setDepthBufferSize(24)
    fmt.setStencilBufferSize(8)
    fmt.setVersion(2, 1)  # compatibility profile is fine for fixed-function
    fmt.setProfile(QSurfaceFormat.CompatibilityProfile)
    fmt.setSamples(4)  # MSAA
    QSurfaceFormat.setDefaultFormat(fmt)


def main():
    configure_surface_format()
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
