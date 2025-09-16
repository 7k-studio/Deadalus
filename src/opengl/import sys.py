import sys
import math
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QSurfaceFormat
from PyQt5.QtOpenGL import QGLFormat
from PyQt5.QtWidgets import QOpenGLWidget
from geomdl import BSpline, utilities

# PyOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *

class Viewport3D(QOpenGLWidget):


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
        #glEnable(GL_CULL_FACE)
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
        
        # Example data (shortened to your sample)
        ps_seg1 = np.array([
            [0.03999127, 0.02501396, 0.0],
            [0.2,        0.08972666, 0.0],
            [0.88999564, 0.03169268, 0.0],
            [0.98999564, 0.00499127, 0.0]
        ])

        ps_seg2 = np.array([
            [0.03999127, 0.22501396, 0.3],
            [0.2,        0.28972666, 0.3],
            [0.88999564, 0.23169268, 0.3],
            [0.98999564, 0.20499127, 0.3]
        ])

        le_ps = np.array([
            [0.03999127, 0.02501396, 0.0],
            [0.03999127, 0.02501396, 0.1],
            [0.03999127, 0.22501396, 0.2],
            [0.03999127, 0.22501396, 0.3]
        ])

        te_ps = np.array([
            [0.98999564, 0.00499127, 0.0],
            [0.98999564, 0.00499127, 0.1],
            [0.98999564, 0.20499127, 0.2],
            [0.98999564, 0.20499127, 0.3]
        ])


        # Build grid [u][v]
        # u: chordwise, v: spanwise
        control_points = [
            [list(le_ps[0]), list(le_ps[1]), list(le_ps[2]), list(le_ps[3])],
            [list(ps_seg1[1]), list(0.25*(ps_seg1[1]+ps_seg2[1]+le_ps[1]+te_ps[1])), 
                            list(0.25*(ps_seg1[1]+ps_seg2[1]+le_ps[2]+te_ps[2])),
                            list(ps_seg2[1])],
            [list(ps_seg1[2]), list(0.25*(ps_seg1[2]+ps_seg2[2]+le_ps[1]+te_ps[1])), 
                            list(0.25*(ps_seg1[2]+ps_seg2[2]+le_ps[2]+te_ps[2])),
                            list(ps_seg2[2])],
            [list(te_ps[0]), list(te_ps[1]), list(te_ps[2]), list(te_ps[3])]
        ]

        # Flatten grid
        n_u = len(control_points)      # rows
        n_v = len(control_points[0])   # cols
        ctrlpts_flat = [pt for row in control_points for pt in row]

        # Define surface
        surf = BSpline.Surface()
        surf.degree_u = 3
        surf.degree_v = 3
        surf.set_ctrlpts(ctrlpts_flat, n_u, n_v)

        # Knot vectors
        surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, n_u)
        surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, n_v)

        # Evaluate
        # Set evaluation delta
        surf.delta = (0.05, 0.05)   # finer grid in u and v

        # Evaluate surface
        surf.evaluate()

        # After surf.evaluate()
        res_u = surf.sample_size[0]  # number of points along U
        res_v = surf.sample_size[1]  # number of points along V

        # Reshape into 2D grid [i][j]
        grid = [[surf.evalpts[i * res_v + j] for j in range(res_v)] for i in range(res_u)]

        # Now draw quads
        glColor3f(0.8, 0.8, 0.9)
        for i in range(res_u - 1):
            for j in range(res_v - 1):
                p0 = grid[i][j]
                p1 = grid[i][j+1]
                p2 = grid[i+1][j+1]
                p3 = grid[i+1][j]

                glBegin(GL_QUADS)
                glVertex3fv(p0)
                glVertex3fv(p1)
                glVertex3fv(p2)
                glVertex3fv(p3)
                glEnd()

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
