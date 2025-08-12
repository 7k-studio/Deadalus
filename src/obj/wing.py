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

from src.arfdes.tools_airfoil import CreateBSpline
import src.globals as globals
import src.obj.airfoil

class Segment:
    def __init__(self):
        self.infos = {'name': 'segment',
                      'creation_date': '',
                      'modification_date': ''}
        
        self.airfoil = src.obj.airfoil.Airfoil()
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

    def move_airfoil(self, cmp_X:float, cmp_Y:float, wng_X:float, wng_Y:float, seg_X:float, seg_Y:float):

        move_X = cmp_X + wng_X + seg_X
        move_Y = cmp_Y + wng_Y + seg_Y

        print(f"> Moving airfoil geometry by X:{move_X}, Y:{move_Y}...")

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

        self.update_airfoil()

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
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.move_airfoil(cmp_X, cmp_Y, wng_X, wng_Y, seg_X, seg_Y)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.control_points['le'], self.control_points['ps'], self.control_points['ss'], self.control_points['te'] = self.rotate_airfoil(incidence)
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

        self.update_airfoil()

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
        if len(self.segments) > 1:
            for i in range(len(self.segments)-1):

                parent_le_ps_seg_anchor = np.array(self.segments[i].control_points['ps'])[:,0]
                parent_le_ps_seg_anchor = np.hstack((parent_le_ps_seg_anchor, self.segments[i].params['origin_Z'] ))

                child_le_ps_seg_anchor = np.array(self.segments[i+1].control_points['ps'])[:,0]
                child_le_ps_seg_anchor = np.hstack((child_le_ps_seg_anchor, self.segments[i+1].params['origin_Z'] ))

                parent_te_ps_seg_anchor = np.array(self.segments[i].control_points['ps'])[:,-1]
                parent_te_ps_seg_anchor = np.hstack((parent_te_ps_seg_anchor, self.segments[i].params['origin_Z'] ))

                child_te_ps_seg_anchor = np.array(self.segments[i+1].control_points['ps'])[:,-1]
                child_te_ps_seg_anchor = np.hstack((child_te_ps_seg_anchor, self.segments[i+1].params['origin_Z'] ))

                parent_le_ss_seg_anchor = np.array(self.segments[i].control_points['ss'])[:,0]
                parent_le_ss_seg_anchor = np.hstack((parent_le_ss_seg_anchor, self.segments[i].params['origin_Z'] ))

                child_le_ss_seg_anchor = np.array(self.segments[i+1].control_points['ss'])[:,0]
                child_le_ss_seg_anchor = np.hstack((child_le_ss_seg_anchor, self.segments[i+1].params['origin_Z'] ))

                parent_te_ss_seg_anchor = np.array(self.segments[i].control_points['ss'])[:,-1]
                parent_te_ss_seg_anchor = np.hstack((parent_te_ss_seg_anchor, self.segments[i].params['origin_Z'] ))

                child_te_ss_seg_anchor = np.array(self.segments[i+1].control_points['ss'])[:,-1]
                child_te_ss_seg_anchor = np.hstack((child_te_ss_seg_anchor, self.segments[i+1].params['origin_Z'] ))

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
                    #print("tmp_le_ps:", tmp_le_ps)
                    self.segments[i].control_points['le_ps'] = np.vstack(tmp_le_ps).T

                if tmp_te_ps:
                    #print("tmp_te_ps:", tmp_te_ps)
                    self.segments[i].control_points['te_ps'] = np.vstack(tmp_te_ps).T

                if tmp_le_ss:
                    #print("tmp_le_ss:", tmp_le_ss)
                    self.segments[i].control_points['le_ss'] = np.vstack(tmp_le_ss).T

                if tmp_te_ss:
                    #print("tmp_te_ss:", tmp_te_ss)
                    self.segments[i].control_points['te_ss'] = np.vstack(tmp_te_ss).T

        #print(f'WNGWB > Wing > build_connection > Connection between two segments established')

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
