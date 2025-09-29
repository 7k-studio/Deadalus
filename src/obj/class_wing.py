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
import math
import numpy as np
from geomdl import BSpline, utilities

from src.utils.tools_program import CreateBSpline_3D
import src.globals as globals
import src.obj.objects2D as objects2D
import src.obj.class_spar as Spar

from geomdl import NURBS
from geomdl import tessellate
from geomdl import knotvector

logger = logging.getLogger(__name__)

class Wing:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.infos = {'name': 'wing',
                      'creation_date': '',
                      'modification_date': ''}
        
        self.spar = Spar()
        self.ribs = []
        self.skin = []
        
        
        self.params = {
            'origin_X': 0,
            'origin_Y': 0,
            'origin_Z': 0,   
        }

        self.geom = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

        self.control_points = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

        
    
    def move(self, cmp_X:float, cmp_Y:float, cmp_Z:float, wng_X:float, wng_Y:float, wng_Z:float, seg_X:float, seg_Y:float, seg_Z:float):

        move_X = cmp_X + wng_X + seg_X
        move_Y = cmp_Y + wng_Y + seg_Y
        move_Z = cmp_Z + wng_Z

        self.logger.info(f"Moving WING geometry by X:{move_X}, Y:{move_Y}, Z:{move_Z}...")

        tmp_le = np.vstack([self.geom['le'][0] + move_X, self.geom['le'][1] + move_Y, self.geom['le'][2] + move_Z])
        tmp_ps = np.vstack([self.geom['ps'][0] + move_X, self.geom['ps'][1] + move_Y, self.geom['ps'][2] + move_Z])
        tmp_ss = np.vstack([self.geom['ss'][0] + move_X, self.geom['ss'][1] + move_Y, self.geom['ss'][2] + move_Z])
        tmp_te = np.vstack([self.geom['te'][0] + move_X, self.geom['te'][1] + move_Y, self.geom['te'][2] + move_Z])

        tmp_c_le = np.vstack([self.control_points['le'][0] + move_X, self.control_points['le'][1] + move_Y, self.control_points['le'][2] + move_Z])
        tmp_c_ps = np.vstack([self.control_points['ps'][0] + move_X, self.control_points['ps'][1] + move_Y, self.control_points['ps'][2] + move_Z])
        tmp_c_ss = np.vstack([self.control_points['ss'][0] + move_X, self.control_points['ss'][1] + move_Y, self.control_points['ss'][2] + move_Z])
        tmp_c_te = np.vstack([self.control_points['te'][0] + move_X, self.control_points['te'][1] + move_Y, self.control_points['te'][2] + move_Z])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def scale(self, scale:float):

        self.logger.info(f"Scaling WING geometry by {scale}...")

        tmp_le = scale * np.array(self.geom['le'])
        tmp_ps = scale * np.array(self.geom['ps'])
        tmp_ss = scale * np.array(self.geom['ss'])
        tmp_te = scale * np.array(self.geom['te'])

        tmp_c_le = scale * np.array(self.control_points['le'])
        tmp_c_ps = scale * np.array(self.control_points['ps'])
        tmp_c_ss = scale * np.array(self.control_points['ss'])
        tmp_c_te = scale * np.array(self.control_points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def rotate(self, aoa:float):

        self.logger.info(f"Rotating WING geometry by {aoa} degrees...")

        theta = np.radians(float(aoa))
        rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                                [np.sin(theta), np.cos(theta)]])

        tmp_le = np.dot(rotation_matrix, self.geom['le'])
        tmp_ps = np.dot(rotation_matrix, self.geom['ps'])
        tmp_ss = np.dot(rotation_matrix, self.geom['ss'])
        tmp_te = np.dot(rotation_matrix, self.geom['te'])

        tmp_c_le = np.dot(rotation_matrix, self.control_points['le'])
        tmp_c_ps = np.dot(rotation_matrix, self.control_points['ps'])
        tmp_c_ss = np.dot(rotation_matrix, self.control_points['ss'])
        tmp_c_te = np.dot(rotation_matrix, self.control_points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te
    
    def update(self, grandparent_index, parent_index, item_index):
        self.logger.info("Updating WING geometry...")
        self.transform(grandparent_index, parent_index, item_index)
        self.build_connection()
        self.build_b_spline_surf()

    def transform(self, grandparent_index, parent_index, item_index):

        cmp_X = globals.PROJECT.project_components[grandparent_index].params['origin_X']
        cmp_Y = globals.PROJECT.project_components[grandparent_index].params['origin_Y']
        cmp_Z = globals.PROJECT.project_components[grandparent_index].params['origin_Z']

        wng_X = globals.PROJECT.project_components[grandparent_index].wings[parent_index].params['origin_X']
        wng_Y = globals.PROJECT.project_components[grandparent_index].wings[parent_index].params['origin_Y']
        wng_Z = globals.PROJECT.project_components[grandparent_index].wings[parent_index].params['origin_Z']

        seg_X = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['origin_X']
        seg_Y = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['origin_Y']
        seg_Z = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['origin_Z']
        scale = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['scale']
        incidence = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['incidence']

        self.logger.info("Transforming WING geometry...")
        #self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.scale(scale)
        #self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.move(cmp_X, cmp_Y, wng_X, wng_Y, seg_X, seg_Y)
        #self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.rotate(incidence)
        self.logger.info("Done!")

    def build_connection(self):
        self.logger.info("Building connection...")
        if len(self.segments) > 1:
            for i in range(len(self.segments)-1):
                
                parent_le_ps_seg_anchor = np.array(self.segments[i].control_points['ps'])[:,0] #Coordinates of anchor of le and ps -> list: [X,Y,Z]
                child_le_ps_seg_anchor = np.array(self.segments[i+1].control_points['ps'])[:,0]

                parent_te_ps_seg_anchor = np.array(self.segments[i].control_points['ps'])[:,-1]
                child_te_ps_seg_anchor = np.array(self.segments[i+1].control_points['ps'])[:,-1]

                parent_le_ss_seg_anchor = np.array(self.segments[i].control_points['ss'])[:,0]
                child_le_ss_seg_anchor = np.array(self.segments[i+1].control_points['ss'])[:,0]

                parent_te_ss_seg_anchor = np.array(self.segments[i].control_points['ss'])[:,-1]
                child_te_ss_seg_anchor = np.array(self.segments[i+1].control_points['ss'])[:,-1]

                if self.segments[i].anchor == 'G0' and self.segments[i+1].anchor == 'G0':

                    parent_le_ps_tan_cp = None
                    parent_le_ss_tan_cp = None
                    parent_te_ss_tan_cp = None
                    parent_te_ps_tan_cp = None

                    child_le_ps_tan_cp = None
                    child_le_ss_tan_cp = None
                    child_te_ss_tan_cp = None
                    child_te_ps_tan_cp = None

                if self.segments[i].anchor == 'G0' and self.segments[i+1].anchor == 'G1':

                    parent_le_ps_tan_cp = np.array([parent_le_ps_seg_anchor[0] , parent_le_ps_seg_anchor[1], (parent_le_ps_seg_anchor[2] + 0)])
                    parent_le_ss_tan_cp = np.array([parent_le_ss_seg_anchor[0], parent_le_ss_seg_anchor[1], (parent_le_ss_seg_anchor[2] + 0)])
                    parent_te_ss_tan_cp = np.array([parent_te_ss_seg_anchor[0], parent_te_ss_seg_anchor[1], (parent_te_ss_seg_anchor[2] + 0)])
                    parent_te_ps_tan_cp = np.array([parent_te_ps_seg_anchor[0] , parent_te_ps_seg_anchor[1], (parent_te_ps_seg_anchor[2] + 0)])

                    child_le_ps_tan_cp = np.array([child_le_ps_seg_anchor[0] , child_le_ps_seg_anchor[1], (child_le_ps_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])
                    child_le_ss_tan_cp = np.array([child_le_ss_seg_anchor[0], child_le_ss_seg_anchor[1], (child_le_ss_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])
                    child_te_ps_tan_cp = np.array([child_te_ps_seg_anchor[0] , child_te_ps_seg_anchor[1], (child_te_ps_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])
                    child_te_ss_tan_cp = np.array([child_te_ss_seg_anchor[0], child_te_ss_seg_anchor[1], (child_te_ss_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])


                if self.segments[i].anchor == 'G1' and self.segments[i+1].anchor == 'G0':

                    parent_le_ps_tan_cp = np.array([parent_le_ps_seg_anchor[0] , parent_le_ps_seg_anchor[1], (parent_le_ps_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_le_ss_tan_cp = np.array([parent_le_ss_seg_anchor[0], parent_le_ss_seg_anchor[1], (parent_le_ss_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_te_ss_tan_cp = np.array([parent_te_ss_seg_anchor[0], parent_te_ss_seg_anchor[1], (parent_te_ss_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_te_ps_tan_cp = np.array([parent_te_ps_seg_anchor[0] , parent_te_ps_seg_anchor[1], (parent_te_ps_seg_anchor[2] + self.segments[i].params['tan_accel'])])

                    child_le_ps_tan_cp = np.array([parent_le_ps_seg_anchor[0] , parent_le_ps_seg_anchor[1], (parent_le_ps_seg_anchor[2] + 0)])
                    child_le_ss_tan_cp = np.array([parent_le_ss_seg_anchor[0], parent_le_ss_seg_anchor[1], (parent_le_ss_seg_anchor[2] + 0)])
                    child_te_ps_tan_cp = np.array([parent_te_ss_seg_anchor[0], parent_te_ss_seg_anchor[1], (parent_te_ss_seg_anchor[2] + 0)])
                    child_te_ss_tan_cp = np.array([parent_te_ps_seg_anchor[0] , parent_te_ps_seg_anchor[1], (parent_te_ps_seg_anchor[2] + 0)])
                
                if self.segments[i].anchor == 'G1' and self.segments[i+1].anchor == 'G1':

                    parent_le_ps_tan_cp = np.array([parent_le_ps_seg_anchor[0] , parent_le_ps_seg_anchor[1], (parent_le_ps_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_le_ss_tan_cp = np.array([parent_le_ss_seg_anchor[0], parent_le_ss_seg_anchor[1], (parent_le_ss_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_te_ss_tan_cp = np.array([parent_te_ss_seg_anchor[0], parent_te_ss_seg_anchor[1], (parent_te_ss_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_te_ps_tan_cp = np.array([parent_te_ps_seg_anchor[0] , parent_te_ps_seg_anchor[1], (parent_te_ps_seg_anchor[2] + self.segments[i].params['tan_accel'])])

                    child_le_ps_tan_cp = np.array([child_le_ps_seg_anchor[0] , child_le_ps_seg_anchor[1], (child_le_ps_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])
                    child_le_ss_tan_cp = np.array([child_le_ss_seg_anchor[0], child_le_ss_seg_anchor[1], (child_le_ss_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])
                    child_te_ps_tan_cp = np.array([child_te_ps_seg_anchor[0] , child_te_ps_seg_anchor[1], (child_te_ps_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])
                    child_te_ss_tan_cp = np.array([child_te_ss_seg_anchor[0], child_te_ss_seg_anchor[1], (child_te_ss_seg_anchor[2] - self.segments[i+1].params['tan_accel'])])

                if self.segments[i].anchor == 'G2':
                    factor = (parent_le_ps_seg_anchor[0] - child_le_ps_seg_anchor[0]) / 10

                tmp_le_ps = [p for p in (parent_le_ps_seg_anchor,parent_le_ps_tan_cp,child_le_ps_tan_cp,child_le_ps_seg_anchor) if p is not None]
                tmp_te_ps = [p for p in (parent_te_ps_seg_anchor,parent_te_ps_tan_cp,child_te_ps_tan_cp,child_te_ps_seg_anchor) if p is not None]
                tmp_le_ss = [p for p in (parent_le_ss_seg_anchor,parent_le_ss_tan_cp,child_le_ss_tan_cp,child_le_ss_seg_anchor) if p is not None]
                tmp_te_ss = [p for p in (parent_te_ss_seg_anchor,parent_te_ss_tan_cp,child_te_ss_tan_cp,child_te_ss_seg_anchor) if p is not None]

                if tmp_le_ps: 
                    self.logger.debug(f"tmp_le_ps: {tmp_le_ps}")
                    self.segments[i].control_points['le_ps'] = np.array(tmp_le_ps).T
                    self.logger.debug(f"le_ps: {self.segments[i].control_points['le_ps']}")
                
                if tmp_te_ps:
                    self.logger.debug(f"tmp_te_ps: {tmp_te_ps}")
                    self.segments[i].control_points['te_ps'] = np.array(tmp_te_ps).T
                    self.logger.debug(f"te_ps: {self.segments[i].control_points['te_ps']}")

                if tmp_le_ss:
                    self.logger.debug(f"tmp_le_ss: {tmp_le_ss}")
                    self.segments[i].control_points['le_ss'] = np.array(tmp_le_ss).T
                    self.logger.debug(f"le_ss: {self.segments[i].control_points['le_ss']}")

                if tmp_te_ss:
                    self.logger.debug(f"tmp_te_ss: {tmp_te_ss}")
                    self.segments[i].control_points['te_ss'] = np.array(tmp_te_ss).T
                    self.logger.debug(f"te_ss: {self.segments[i].control_points['te_ss']}")

                degree = len(tmp_le_ps)-1
                self.logger.debug(f'Degree: {degree}')

                self.segments[i].geom['le_ps'] = CreateBSpline_3D(self.segments[i].control_points['le_ps'], degree)
                self.segments[i].geom['te_ps'] = CreateBSpline_3D(self.segments[i].control_points['te_ps'], degree)
                self.segments[i].geom['le_ss'] = CreateBSpline_3D(self.segments[i].control_points['le_ss'], degree)
                self.segments[i].geom['te_ss'] = CreateBSpline_3D(self.segments[i].control_points['te_ss'], degree)

                u_start_cp = self.segments[i].control_points['ps']
                u_end_cp   = self.segments[i+1].control_points['ps']
                v_start_cp = self.segments[i].control_points['le_ps']
                v_end_cp   = self.segments[i].control_points['te_ps']

                # Build grid [u][v]
                uv_grid = make_uv_grid_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].uv_grid['ps'] = uv_grid #[[list(p) for p in row] for row in surf]

                u_start_cp = self.segments[i].control_points['ss']
                u_end_cp = self.segments[i+1].control_points['ss']
                v_start_cp = self.segments[i].control_points['le_ss']
                v_end_cp = self.segments[i].control_points['te_ss']

                # Build grid [u][v]
                uv_grid = make_uv_grid_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].uv_grid['ss'] = uv_grid

                u_start_cp = self.segments[i].control_points['le']
                u_end_cp = self.segments[i+1].control_points['le']
                v_start_cp = self.segments[i].control_points['le_ss']
                v_end_cp = self.segments[i].control_points['le_ps']

                # Build grid [u][v]
                uv_grid = make_uv_grid_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].uv_grid['le'] = uv_grid

                u_start_cp = self.segments[i].control_points['te']
                #u_start_cp = u_start_cp[:, ::-1]
                u_end_cp = self.segments[i+1].control_points['te']
                #u_end_cp = u_end_cp[:, ::-1]
                v_start_cp = self.segments[i].control_points['te_ss']
                v_end_cp = self.segments[i].control_points['te_ps']

                # Build grid [u][v]
                uv_grid = make_uv_grid_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].uv_grid['te'] = uv_grid

                self.logger.debug(f'Grid or surf: {uv_grid}')
                #self.build_b_spline_surf()

        self.logger.info(f'Connection between two segments established')

    def build_b_spline_surf(self):
        """
        Create a NURBS surface from a 2D grid of control points.

        control_grid: list of rows (u-direction), each row is list of [x,y,z] points
                    shape = [n_u][n_v], with n_u, n_v in [2..6]
        """
        for segment in self.segments:
            for key in ['le', 'ps', 'te', 'ss']:
                control_points = np.array(segment.uv_grid[key])
                
                if control_points.size > 0:
                    segment.surfaces[key] = make_nurbs_surface_points(control_points)

def build_surface_mesh(surf):
    """
    Create faces (quads) from geomdl evaluated surface (surf.evalpts)
    Returns list of quads: [(p0,p1,p2,p3), ...] where each p* is [x,y,z].
    """
    res_u, res_v = surf.sample_size
    grid = [[surf.evalpts[i * res_v + j] for j in range(res_v)] for i in range(res_u)]
    faces = []
    for i in range(res_u - 1):
        for j in range(res_v - 1):
            p0 = grid[i][j]
            p1 = grid[i][j + 1]
            p2 = grid[i + 1][j + 1]
            p3 = grid[i + 1][j]
            faces.append((p0, p1, p2, p3))
    return faces

def make_surface(control_grid):
    """
    Create a NURBS surface from a 2D grid of control points.
    control_grid: list of rows (u-direction), each row is list of [x,y,z] points
    """
    n_u = len(control_grid)
    n_v = len(control_grid[0]) if n_u > 0 else 0

    ctrlpts_flat = [ [float(p[0]), float(p[1]), float(p[2])] for row in control_grid for p in row ]

    surf = BSpline.Surface()
    surf.degree_u = min(2, n_u - 1) if n_u > 0 else 1
    surf.degree_v = min(2, n_v - 1) if n_v > 0 else 1
    surf.set_ctrlpts(ctrlpts_flat, n_u, n_v)
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, n_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, n_v)

    d = 0.05 * int(globals.DEADALUS.preferences['general']['performance']) / 100
    surf.delta = (d, d)
    surf.evaluate()
    return surf

def resample_curve(points, n_out):
    """Resample a polyline curve (array Nx3) to n_out points by linear interpolation"""
    points = np.array(points)
    # chord length parameterization
    dists = np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))
    dists = np.insert(dists, 0, 0.0)
    t = dists / dists[-1]

    t_new = np.linspace(0, 1, n_out)
    resampled = np.zeros((n_out, 3))
    for k in range(3):  # x,y,z separately
        resampled[:, k] = np.interp(t_new, t, points[:, k])
    return resampled

def sample_curve(points, t):
    """
    Linear (chord-length) evaluation of a polyline at param t in [0,1].
    points: Nx3 numpy array or list. Returns length-3 numpy array.
    """
    pts = np.asarray(points, dtype=float)
    n = len(pts)
    if n == 0:
        return np.zeros(3, dtype=float)
    if n == 1:
        return pts[0].copy()
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    d = np.insert(np.cumsum(seg), 0, 0.0)
    total = d[-1]
    if total <= 1e-12:
        return pts[0].copy()
    d = d / total
    t = float(np.clip(t, 0.0, 1.0))
    out = np.empty(3, dtype=float)
    for k in range(3):
        out[k] = np.interp(t, d, pts[:, k])
    return out

def make_nurbs_surface_points(control_points):
    samples_u=int(globals.DEADALUS.preferences["general"]["performance"]/3+7)
    samples_v=int(globals.DEADALUS.preferences["general"]["performance"]/3+7)
    u_count, v_count, _ = control_points.shape
    surf = NURBS.Surface()
    surf.degree_u = min(3, u_count - 1)
    surf.degree_v = min(3, v_count - 1)
    # Add weight 1.0 to each control point
    ctrlpts = [list(pt) + [1.0] for pt in control_points.reshape(-1, 3)]
    surf.set_ctrlpts(ctrlpts, u_count, v_count)
    surf.knotvector_u = knotvector.generate(surf.degree_u, u_count)
    surf.knotvector_v = knotvector.generate(surf.degree_v, v_count)
    # Evaluate surface points
    surf.sample_size = samples_u
    surf.sample_size_v = samples_v
    surf_points = np.array(surf.evalpts).reshape(samples_u, samples_v, 3)
    return surf_points

def make_uv_grid_from_boundaries(u_start, u_end, v_start, v_end):
    """
    Build control grid (list of rows) using a discrete Coons patch.
    Accepts u_start/u_end/v_start/v_end in either Nx3 form.
    Returns grid as Python list: [nu][nv][3].
    """
    u_count = len(u_start[0])
    v_count = len(v_start[0])

    # Build the control points grid
    control_points = np.zeros((u_count, v_count, 3))  # (u, v, xyz)

    for u in range(u_count):
        for v in range(v_count):
            tu = u / (u_count - 1) if u_count > 1 else 0
            tv = v / (v_count - 1) if v_count > 1 else 0
            # u-direction curve at v
            cu = (1 - tu) * np.array([v_start[0][v], v_start[1][v], v_start[2][v]]) + tu * np.array([v_end[0][v], v_end[1][v], v_end[2][v]])
            # v-direction curve at u
            cv = (1 - tv) * np.array([u_start[0][u], u_start[1][u], u_start[2][u]]) + tv * np.array([u_end[0][u], u_end[1][u], u_end[2][u]])
            # corners
            p00 = np.array([u_start[0][0], u_start[1][0], u_start[2][0]])
            p10 = np.array([u_start[0][u_count-1], u_start[1][u_count-1], u_start[2][u_count-1]])
            p01 = np.array([u_end[0][0], u_end[1][0], u_end[2][0]])
            p11 = np.array([u_end[0][u_count-1], u_end[1][u_count-1], u_end[2][u_count-1]])
            bilinear = (1 - tu) * (1 - tv) * p00 + tu * (1 - tv) * p10 + (1 - tu) * tv * p01 + tu * tv * p11
            control_points[u, v, :] = cu + cv - bilinear

    # Optionally, print or use the grid
    logger.info(f"Control points grid ({u_count}x{v_count}x3) established")
    logger.debug(control_points)

    return control_points

def build_b_spline_surf_for_segment(segment):
    """
    Build & cache BSpline surfaces for each surface grid in a segment.
    This separates heavy evaluation from paintGL.
    """
    for key in ['le', 'ps', 'te', 'ss']:
        grid = segment.uv_grid.get(key)
        if not grid:
            continue
        # Ensure a proper Python list of lists
        control_points = grid
        n_u = len(control_points)
        n_v = len(control_points[0]) if n_u > 0 else 0
        if n_u < 2 or n_v < 2:
            segment.surfaces[key] = []
            continue

        # sanitize ctrl pts to float lists
        ctrlpts_flat = [[float(p[0]), float(p[1]), float(p[2])]
                        for row in control_points for p in row]

        surf = BSpline.Surface()
        surf.degree_u = min(2, n_u - 1)
        surf.degree_v = min(2, n_v - 1)
        surf.set_ctrlpts(ctrlpts_flat, n_u, n_v)
        surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, n_u)
        surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, n_v)

        res = -0.00056 * globals.DEADALUS.preferences["general"]["performance"] + 0.1
        surf.delta = (res, res)
        surf.evaluate()
        segment.surfaces[key] = build_surface_mesh(surf)