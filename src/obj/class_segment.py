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

from geomdl import NURBS
from geomdl import tessellate
from geomdl import knotvector

class Segment:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
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

        self.uv_grid = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

        self.surfaces = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

        self.surfaces_info = {
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

    def move(self, cmp_X:float, cmp_Y:float, cmp_Z:float, wng_X:float, wng_Y:float, wng_Z:float, seg_X:float, seg_Y:float, seg_Z:float):

        move_X = cmp_X + wng_X + seg_X
        move_Y = cmp_Y + wng_Y + seg_Y
        move_Z = cmp_Z + wng_Z

        self.logger.info(f"Moving SEGMENT geometry by X:{move_X}, Y:{move_Y}, Z:{move_Z}...")

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

        self.logger.info(f"Scaling SEGMENT geometry by {scale}...")

        tmp_le = scale * np.array(self.geom['le'])
        tmp_ps = scale * np.array(self.geom['ps'])
        tmp_ss = scale * np.array(self.geom['ss'])
        tmp_te = scale * np.array(self.geom['te'])

        tmp_c_le = scale * np.array(self.control_points['le'])
        tmp_c_ps = scale * np.array(self.control_points['ps'])
        tmp_c_ss = scale * np.array(self.control_points['ss'])
        tmp_c_te = scale * np.array(self.control_points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def rotate(self, aoa: float, center=(0.0, 0.0)):
        self.logger.info(f"Rotating SEGMENT geometry by {aoa} degrees around {center}...")

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
    
    def update(self, grandparent_index, parent_index, item_index):

        self.logger.info("Updating SEGMENT geometry...")

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

        self.transform(grandparent_index, parent_index, item_index)

        self.logger.debug(self.geom['le'])
        self.logger.debug(self.geom['ps'])
        self.logger.debug(self.geom['ss'])
        self.logger.debug(self.geom['te'])

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

        self.logger.info("Transforming SEGMENT geometry...")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.scale(scale)
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.move(cmp_X, cmp_Y, cmp_Z, wng_X, wng_Y, wng_Z, seg_X, seg_Y, seg_Z)
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.rotate(incidence, (wng_X, wng_Y))
        self.logger.info("Done!")