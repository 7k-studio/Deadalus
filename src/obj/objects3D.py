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

import math
import numpy as np

from src.utils.tools_program import CreateBSpline_3D
import src.globals as globals
import src.obj.objects2D as objects2D

class Segment:
    def __init__(self):
        self.infos = {'name': 'segment',
                      'creation_date': '',
                      'modification_date': ''}
        
        self.airfoil = objects2D.Airfoil()
        self.anchor = 'G0' # G1 or G2 later add 'segment'

        self.params = {
            'origin_X': 0,
            'origin_Y': 0,
            'origin_Z': 0,
            'incidence': 0,
            'scale': 1,
            'tan_accel': 0.1,
            #'curv_accel': 0.1,
            #'curv_theta': 0   
        }

        self.control_points = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': [],
            'le_ps': [],
            'te_ps': [],
            'le_ss': [],
            'te_ss': []
        }

        self.surfaces_grid = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

        self.geom = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': [],
            'le_ps': [],
            'te_ps': [],
            'le_ss': [],
            'te_ss': []
        }

    def move_airfoil(self, cmp_X:float, cmp_Y:float, cmp_Z:float, wng_X:float, wng_Y:float, wng_Z:float, seg_X:float, seg_Y:float, seg_Z:float):

        move_X = cmp_X + wng_X + seg_X
        move_Y = cmp_Y + wng_Y + seg_Y
        move_Z = cmp_Z + cmp_Z

        print(f"> Moving airfoil geometry by X:{move_X}, Y:{move_Y}, Z:{move_Z}...")

        tmp_le = np.vstack([self.geom['le'][0] + move_X, self.geom['le'][1] + move_Y, self.geom['le'][2] + move_Z])
        tmp_ps = np.vstack([self.geom['ps'][0] + move_X, self.geom['ps'][1] + move_Y, self.geom['ps'][2] + move_Z])
        tmp_ss = np.vstack([self.geom['ss'][0] + move_X, self.geom['ss'][1] + move_Y, self.geom['ss'][2] + move_Z])
        tmp_te = np.vstack([self.geom['te'][0] + move_X, self.geom['te'][1] + move_Y, self.geom['te'][2] + move_Z])

        tmp_c_le = np.vstack([self.control_points['le'][0] + move_X, self.control_points['le'][1] + move_Y, self.control_points['le'][2] + move_Z])
        tmp_c_ps = np.vstack([self.control_points['ps'][0] + move_X, self.control_points['ps'][1] + move_Y, self.control_points['ps'][2] + move_Z])
        tmp_c_ss = np.vstack([self.control_points['ss'][0] + move_X, self.control_points['ss'][1] + move_Y, self.control_points['ss'][2] + move_Z])
        tmp_c_te = np.vstack([self.control_points['te'][0] + move_X, self.control_points['te'][1] + move_Y, self.control_points['te'][2] + move_Z])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def scale_airfoil(self, scale:float):

        print(f"> Scaling airfoil geometry by {scale}...")

        tmp_le = scale * np.array(self.geom['le'])
        tmp_ps = scale * np.array(self.geom['ps'])
        tmp_ss = scale * np.array(self.geom['ss'])
        tmp_te = scale * np.array(self.geom['te'])

        tmp_c_le = scale * np.array(self.control_points['le'])
        tmp_c_ps = scale * np.array(self.control_points['ps'])
        tmp_c_ss = scale * np.array(self.control_points['ss'])
        tmp_c_te = scale * np.array(self.control_points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def rotate_airfoil(self, aoa: float, center=(0.0, 0.0)):
        print(f"> Rotating airfoil geometry by {aoa} degrees around {center}...")

        cx, cy = center
        theta = np.radians(float(aoa))
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta),  np.cos(theta)]
        ])

        def rotate_points(points):
            # points shape: (2, N)
            center_col = np.array([[cx], [cy]])  # shape (2, 1) for broadcasting
            xy_rotated = rotation_matrix @ (points[:2] - center_col) + center_col
            return np.vstack([xy_rotated, points[2]])  # keep original Z

        tmp_le = rotate_points(self.geom['le'])
        tmp_ps = rotate_points(self.geom['ps'])
        tmp_ss = rotate_points(self.geom['ss'])
        tmp_te = rotate_points(self.geom['te'])

        tmp_c_le = rotate_points(self.control_points['le'])
        tmp_c_ps = rotate_points(self.control_points['ps'])
        tmp_c_ss = rotate_points(self.control_points['ss'])
        tmp_c_te = rotate_points(self.control_points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te
    
    def update_segment(self):

        print("Updating airfoil geometry...")

        self.control_points['le'] = self.airfoil.constr['le']
        control_points_Z = [self.params['origin_Z']] * len(self.airfoil.constr['le'][0])
        self.control_points['le'] = np.vstack([self.control_points['le'], control_points_Z])

        self.control_points['ps'] = self.airfoil.constr['ps']
        control_points_Z = [self.params['origin_Z']] * len(self.airfoil.constr['ps'][0])
        self.control_points['ps'] = np.vstack([self.control_points['ps'], control_points_Z])

        self.control_points['ss'] = self.airfoil.constr['ss']
        control_points_Z = [self.params['origin_Z']] * len(self.airfoil.constr['ss'][0])
        self.control_points['ss'] = np.vstack([self.control_points['ss'], control_points_Z])

        self.control_points['te'] = self.airfoil.constr['te']
        control_points_Z = [self.params['origin_Z']] * len(self.airfoil.constr['te'][0])
        self.control_points['te'] = np.vstack([self.control_points['te'], control_points_Z])

        self.geom['le'] = CreateBSpline_3D(self.control_points['le'], len(self.airfoil.constr['le'][0])-1)
        self.geom['ps'] = CreateBSpline_3D(self.control_points['ps'], len(self.airfoil.constr['ps'][0])-1)
        self.geom['ss'] = CreateBSpline_3D(self.control_points['ss'], len(self.airfoil.constr['ss'][0])-1)
        self.geom['te'] = CreateBSpline_3D(self.control_points['te'], len(self.airfoil.constr['te'][0])-1)

        #print(self.geom['le'])
        #print(self.geom['ps'])
        #print(self.geom['ss'])
        #print(self.geom['te'])

    def transform_airfoil(self, grandparent_index, parent_index, item_index):

        self.update_segment()

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

        print("Transforming airfoil geometry...")
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.scale_airfoil(scale)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.move_airfoil(cmp_X, cmp_Y, cmp_Z, wng_X, wng_Y, wng_Z, seg_X, seg_Y, seg_Z)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.rotate_airfoil(incidence, (wng_X, wng_Y))
        print(".")
        print("Done!")

class Wing:
    def __init__(self):
        self.infos = {'name': 'wing',
                      'creation_date': '',
                      'modification_date': ''}
        
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

        self.segments = []
    
    def move_wing(self, wng_X:float, wng_Y:float):

        move_X = wng_X
        move_Y = wng_Y

        print(f"> Moving wing geometry by X:{move_X}, Y:{move_Y}...")

        tmp_le = np.vstack([self.geom['le'][0] + move_X, self.geom['le'][1] + move_Y])
        tmp_ps = np.vstack([self.geom['ps'][0] + move_X, self.geom['ps'][1] + move_Y])
        tmp_ss = np.vstack([self.geom['ss'][0] + move_X, self.geom['ss'][1] + move_Y])
        tmp_te = np.vstack([self.geom['te'][0] + move_X, self.geom['te'][1] + move_Y])

        tmp_c_le = np.vstack([self.control_points['le'][0] + move_X, self.control_points['le'][1] + move_Y])
        tmp_c_ps = np.vstack([self.control_points['ps'][0] + move_X, self.control_points['ps'][1] + move_Y])
        tmp_c_ss = np.vstack([self.control_points['ss'][0] + move_X, self.control_points['ss'][1] + move_Y])
        tmp_c_te = np.vstack([self.control_points['te'][0] + move_X, self.control_points['te'][1] + move_Y])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def scale_airfoil(self, scale:float):

        print(f"> Scaling airfoil geometry by {scale}...")

        tmp_le = scale * np.array(self.geom['le'])
        tmp_ps = scale * np.array(self.geom['ps'])
        tmp_ss = scale * np.array(self.geom['ss'])
        tmp_te = scale * np.array(self.geom['te'])

        tmp_c_le = scale * np.array(self.control_points['le'])
        tmp_c_ps = scale * np.array(self.control_points['ps'])
        tmp_c_ss = scale * np.array(self.control_points['ss'])
        tmp_c_te = scale * np.array(self.control_points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def rotate_airfoil(self, aoa:float):

        print(f"> Rotating airfoil geometry by {aoa} degrees...")

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
    
    def update_airfoil(self):
        print("Restoring airfoil geometry...")
        self.geom['le'] = self.airfoil.geom['le']
        self.geom['ps'] = self.airfoil.geom['ps']
        self.geom['ss'] = self.airfoil.geom['ss']
        self.geom['te'] = self.airfoil.geom['te']

        self.control_points['le'] = self.airfoil.constr['le']
        self.control_points['ps'] = self.airfoil.constr['ps']
        self.control_points['ss'] = self.airfoil.constr['ss']
        self.control_points['te'] = self.airfoil.constr['te']

    def transform_airfoil(self, grandparent_index, parent_index, item_index):

        self.update_wing()

        cmp_X = globals.PROJECT.project_components[grandparent_index].origin_X
        cmp_Y = globals.PROJECT.project_components[grandparent_index].origin_Y
        cmp_Z = globals.PROJECT.project_components[grandparent_index].origin_Z

        wng_X = globals.PROJECT.project_components[grandparent_index].wings[parent_index].origin_X
        wng_Y = globals.PROJECT.project_components[grandparent_index].wings[parent_index].origin_Y
        wng_Z = globals.PROJECT.project_components[grandparent_index].wings[parent_index].origin_Z

        seg_X = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['origin_X']
        seg_Y = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['origin_Y']
        seg_Z = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['origin_Z']
        scale = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['scale']
        incidence = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].params['incidence']

        print("Transforming airfoil geometry...")
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.scale_airfoil(scale)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.move_airfoil(cmp_X, cmp_Y, wng_X, wng_Y, seg_X, seg_Y)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.rotate_airfoil(incidence)
        print(".")
        print("Done!")

    def build_connection(self):
        print("Building connection...")
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

                if self.segments[i].anchor == 'G0':

                    parent_le_ps_tan_cp = None
                    parent_le_ss_tan_cp = None
                    parent_te_ss_tan_cp = None
                    parent_te_ps_tan_cp = None

                if self.segments[i+1].anchor == 'G0':

                    child_le_ps_tan_cp = None
                    child_le_ss_tan_cp = None
                    child_te_ss_tan_cp = None
                    child_te_ps_tan_cp = None

                if self.segments[i].anchor == 'G1':

                    parent_le_ps_tan_cp = np.array([parent_le_ps_seg_anchor[0] , parent_le_ps_seg_anchor[1], (parent_le_ps_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_le_ss_tan_cp = np.array([parent_le_ss_seg_anchor[0], parent_le_ss_seg_anchor[1], (parent_le_ss_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_te_ss_tan_cp = np.array([parent_te_ss_seg_anchor[0], parent_te_ss_seg_anchor[1], (parent_te_ss_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                    parent_te_ps_tan_cp = np.array([parent_te_ps_seg_anchor[0] , parent_te_ps_seg_anchor[1], (parent_te_ps_seg_anchor[2] + self.segments[i].params['tan_accel'])])
                
                if self.segments[i+1].anchor == 'G1':

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
                    #print("tmp le ps: ", tmp_le_ps)
                    self.segments[i].control_points['le_ps'] = np.array(tmp_le_ps).T
                    #print("le ps: ", self.segments[i].control_points['le_ps'])
                
                if tmp_te_ps:
                    #print("tmp_te_ps:", tmp_te_ps)
                    self.segments[i].control_points['te_ps'] = np.array(tmp_te_ps).T

                if tmp_le_ss:
                    #print("tmp_le_ss:", tmp_le_ss)
                    self.segments[i].control_points['le_ss'] = np.array(tmp_le_ss).T

                if tmp_te_ss:
                    #print("tmp_te_ss:", tmp_te_ss)
                    self.segments[i].control_points['te_ss'] = np.array(tmp_te_ss).T

                degree = len(tmp_le_ps)-1
                #print('Degree: ', degree)

                self.segments[i].geom['le_ps'] = CreateBSpline_3D(self.segments[i].control_points['le_ps'], degree)
                self.segments[i].geom['te_ps'] = CreateBSpline_3D(self.segments[i].control_points['te_ps'], degree)
                self.segments[i].geom['le_ss'] = CreateBSpline_3D(self.segments[i].control_points['le_ss'], degree)
                self.segments[i].geom['te_ss'] = CreateBSpline_3D(self.segments[i].control_points['te_ss'], degree)

                u_start_cp = self.segments[i].control_points['ps']
                u_end_cp = self.segments[i+1].control_points['ps']
                v_start_cp = self.segments[i].control_points['le_ps']
                v_end_cp = self.segments[i].control_points['te_ps']

                # Build grid [u][v]
                # u: chordwise, v: spanwise
                surf = make_surface_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].surfaces_grid['ps'] = surf #[[list(p) for p in row] for row in surf]

                u_start_cp = self.segments[i].control_points['ss']
                u_end_cp = self.segments[i+1].control_points['ss']
                v_start_cp = self.segments[i].control_points['te_ss']
                v_end_cp = self.segments[i].control_points['le_ss']

                # Build grid [u][v]
                # u: chordwise, v: spanwise
                surf = make_surface_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].surfaces_grid['ss'] = surf

                u_start_cp = self.segments[i].control_points['le']
                u_end_cp = self.segments[i+1].control_points['le']
                v_start_cp = self.segments[i].control_points['le_ss']
                v_end_cp = self.segments[i].control_points['le_ps']

                # Build grid [u][v]
                # u: chordwise, v: spanwise
                surf = make_surface_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].surfaces_grid['le'] = surf

                u_start_cp = self.segments[i].control_points['te']
                u_end_cp = self.segments[i+1].control_points['te']
                v_start_cp = self.segments[i].control_points['te_ps']
                v_end_cp = self.segments[i].control_points['te_ss']

                # Build grid [u][v]
                # u: chordwise, v: spanwise
                surf = make_surface_from_boundaries(u_start_cp, u_end_cp, v_start_cp, v_end_cp)
                self.segments[i].surfaces_grid['te'] = surf

        print(f'WNGWB > Wing > build_connection > Connection between two segments established')

from geomdl import BSpline, utilities

def make_surface(control_grid):
    """
    Create a NURBS surface from a 2D grid of control points.

    control_grid: list of rows (u-direction), each row is list of [x,y,z] points
                  shape = [n_u][n_v], with n_u, n_v in [2..6]
    """
    n_u = len(control_grid)
    n_v = len(control_grid)

    # Flatten row-major
    ctrlpts_flat = [pt for row in control_grid for pt in row]

    surf = BSpline.Surface()

    # Degrees: choose min(cubic, n-1)
    surf.degree_u = min(3, n_u - 1)
    surf.degree_v = min(3, n_v - 1)

    surf.set_ctrlpts(ctrlpts_flat, n_u, n_v)

    # Auto knot vectors
    surf.knotvector_u = utilities.generate_knot_vector(surf.degree_u, n_u)
    surf.knotvector_v = utilities.generate_knot_vector(surf.degree_v, n_v)

    # Evaluation resolution
    d = 0.05 * int(globals.AIRFLOW.preferences['general']['performance'])/100
    surf.delta = (d, d)
    surf.evaluate()

    return surf

def resample_curve(points, n_out):
    """Resample a polyline curve (array Nx3) to n_out points by linear interpolation"""
    points = np.array(points)
    #print("points: ", points)
    # chord length parameterization
    dists = np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))
    dists = np.insert(dists, 0, 0.0)
    t = dists / dists[-1]

    t_new = np.linspace(0, 1, n_out)
    resampled = np.zeros((n_out, 3))
    for k in range(3):  # x,y,z separately
        resampled[:, k] = np.interp(t_new, t, points[:, k])
    return resampled

def ensure_points(points):
    points = np.asarray(points)
    if points.shape[0] == 3 and points.shape[1] != 3:
        return points.T  # transpose to Nx3
    return points

import numpy as np

def _ensure_points(arr):
    arr = np.asarray(arr, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D array for points, got shape {arr.shape}")
    # Accept Nx3 or 3xN
    if arr.shape[1] == 3:
        return arr
    if arr.shape[0] == 3:
        return arr.T
    raise ValueError(f"Points must be Nx3 or 3xN, got shape {arr.shape}")

def _resample_polyline(points, n_out):
    """
    Construct a NURBS surface from 4 boundary splines.
    ps_seg1, ps_seg2, le_ps, te_ps are arrays of shape (N,3), (M,3), ...
    
    Chord-length resample Nx3 polyline to n_out points.
    """
    pts = np.asarray(points, dtype=float)
    if len(pts) == n_out:
        return pts
    if len(pts) == 1:
        return np.repeat(pts, n_out, axis=0)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    total = seg.sum()
    if total <= 1e-12:
        # all the same point
        return np.repeat(pts[:1], n_out, axis=0)
    t = np.insert(np.cumsum(seg), 0, 0.0) / total
    t_new = np.linspace(0.0, 1.0, n_out)
    out = np.empty((n_out, 3))
    for k in range(3):
        out[:, k] = np.interp(t_new, t, pts[:, k])
    return out

def make_surface_from_boundaries(ps_seg1, ps_seg2, le_ps, te_ps, snap_corners=True):
    """
    Construct a surface control grid from 4 boundary polylines using a Coons patch.
    Inputs can be Nx3 or 3xN arrays.
    Returns a Python list with shape [nu][nv][3].
    """
    # Normalize shapes to Nx3
    ps1 = _ensure_points(ps_seg1)
    ps2 = _ensure_points(ps_seg2)
    le  = _ensure_points(le_ps)
    te  = _ensure_points(te_ps)

    # Unify counts per opposite pair (only resample if needed)
    nu = max(len(ps1), len(ps2))
    nv = max(len(le),  len(te))
    if len(ps1) != nu: ps1 = _resample_polyline(ps1, nu)
    if len(ps2) != nu: ps2 = _resample_polyline(ps2, nu)
    if len(le)  != nv: le  = _resample_polyline(le,  nv)
    if len(te)  != nv: te  = _resample_polyline(te,  nv)

    # (Optional but recommended) snap corners to avoid tiny mismatches
    # This guarantees exact boundary interpolation and prevents tiny “pulls”.
    #if snap_corners:
    #    le[0]    = ps1[0]
    #    te[0]    = ps1[-1]
    #    le[-1]   = ps2[0]
    #    te[-1]   = ps2[-1]

    # Coons patch blending on the discrete grid
    p00 = ps1[0]
    p10 = ps1[-1]
    p01 = ps2[0]
    p11 = ps2[-1]

    grid = np.empty((nu, nv, 3), dtype=float)
    for i in range(nu):
        u = i / (nu - 1) if nu > 1 else 0.0
        for j in range(nv):
            v = j / (nv - 1) if nv > 1 else 0.0
            # Blend along u- and v-boundaries
            Cu = (1.0 - v) * ps1[i] + v * ps2[i]     # uses ps1/ps2
            Dv = (1.0 - u) * le[j]  + u * te[j]      # uses le/te
            # Bilinear corner term
            B  = ((1.0 - u) * (1.0 - v) * p00 +
                  u          * (1.0 - v) * p10 +
                  (1.0 - u)  * v         * p01 +
                  u          * v         * p11)
            grid[i, j] = Cu + Dv - B

    return grid.tolist()


class Component:
    def __init__(self):
        self.infos = {'name': 'component',
                      'creation_date': '',
                      'modification_date': ''}
        
        self.params = {
            'origin_X': 0,
            'origin_Y': 0,
            'origin_Z': 0,
        }

        self.wings = []

    def move_component(self, cmp_X:float, cmp_Y:float, cmp_Z:float):

        print(f"WNGWB > Moving component geometry by X:{cmp_X}, Y:{cmp_Y}, Z:{cmp_Z}...")

        tmp_X = self.params['origin_X'] + cmp_X
        tmp_Y = self.params['origin_Y'] + cmp_Y
        tmp_Z = self.params['origin_Z'] + cmp_Z

        return tmp_X, tmp_Y, tmp_Z
    
    def restore_component(self):
        print("Restoring component params...")
        self.params['origin_X'] = 0
        self.params['origin_Y'] = 0
        self.params['origin_Z'] = 0

    def transform_component(self, grandparent_index):

        self.restore_component()

        cmp_X = globals.PROJECT.project_components[grandparent_index].origin_X
        cmp_Y = globals.PROJECT.project_components[grandparent_index].origin_Y
        cmp_Z = globals.PROJECT.project_components[grandparent_index].origin_Z

        print("Transforming component...")
        print(".")
        self.params['origin_X'], self.params['origin_Y'], self.params['origin_Z'] = self.move_component(cmp_X, cmp_Y, cmp_Z)
        print(".")
        print("Done!")
