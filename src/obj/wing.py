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
        self.anchor = 'G0' # G1 or G2

        if self.anchor == 'G0':
            self.params = {
                'origin_X': 0,
                'origin_Y': 0,
                'origin_Z': 0,
                'incidence': 0,
                'scale': 1,  
            }

        if self.anchor == 'G1':
            self.params = {
                'origin_X': 0,
                'origin_Y': 0,
                'origin_Z': 0,
                'incidence': 0,
                'scale': 1,
                'tan_accel': 1,  
            }

        if self.anchor == 'G2':
            self.params = {
                'origin_X': 0,
                'origin_Y': 0,
                'origin_Z': 0,
                'incidence': 0,
                'scale': 1,
                'tan_accel': 1,
                'curv_accel': 1,
                'curv_theta': 0   
            }

        self.points = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

        self.geom = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

    def move_airfoil(self, cmp_X:float, cmp_Y:float, wng_X:float, wng_Y:float, seg_X:float, seg_Y:float):

        move_X = cmp_X + wng_X + seg_X
        move_Y = cmp_Y + wng_Y + seg_Y

        print(f"> Moving airfoil geometry by X:{move_X}, Y:{move_Y}...")

        tmp_le = np.vstack([self.geom['le'][0] + move_X, self.geom['le'][1] + move_Y])
        tmp_ss = np.vstack([self.geom['ps'][0] + move_X, self.geom['ps'][1] + move_Y])
        tmp_ps = np.vstack([self.geom['ss'][0] + move_X, self.geom['ss'][1] + move_Y])
        tmp_te = np.vstack([self.geom['te'][0] + move_X, self.geom['te'][1] + move_Y])

        tmp_c_le = np.vstack([self.points['le'][0] + move_X, self.points['le'][1] + move_Y])
        tmp_c_ss = np.vstack([self.points['ps'][0] + move_X, self.points['ps'][1] + move_Y])
        tmp_c_ps = np.vstack([self.points['ss'][0] + move_X, self.points['ss'][1] + move_Y])
        tmp_c_te = np.vstack([self.points['te'][0] + move_X, self.points['te'][1] + move_Y])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def scale_airfoil(self, scale:float):

        print(f"> Scaling airfoil geometry by {scale}...")

        tmp_le = scale * np.array(self.geom['le'])
        tmp_ps = scale * np.array(self.geom['ps'])
        tmp_ss = scale * np.array(self.geom['ss'])
        tmp_te = scale * np.array(self.geom['te'])

        tmp_c_le = scale * np.array(self.points['le'])
        tmp_c_ps = scale * np.array(self.points['ps'])
        tmp_c_ss = scale * np.array(self.points['ss'])
        tmp_c_te = scale * np.array(self.points['te'])

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

        tmp_c_le = np.dot(rotation_matrix, self.points['le'])
        tmp_c_ps = np.dot(rotation_matrix, self.points['ps'])
        tmp_c_ss = np.dot(rotation_matrix, self.points['ss'])
        tmp_c_te = np.dot(rotation_matrix, self.points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te
    
    def update_airfoil(self):
        print("Restoring airfoil geometry...")
        self.geom['le'] = self.airfoil.geom['le']
        self.geom['ps'] = self.airfoil.geom['ps']
        self.geom['ss'] = self.airfoil.geom['ss']
        self.geom['te'] = self.airfoil.geom['te']

        self.points['le'] = self.airfoil.constr['le']
        self.points['ps'] = self.airfoil.constr['ps']
        self.points['ss'] = self.airfoil.constr['ss']
        self.points['te'] = self.airfoil.constr['te']

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
        print(f"> {cmp_X}, {cmp_Y}, {cmp_Z}")
        print(f"> > {wng_X}, {wng_Y}, {wng_Z}")
        print(f"> > > {seg_X}, {seg_Y}, {seg_Z}, {scale}, {incidence}")

        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.points['le'], self.points['ps'], self.points['ss'], self.points['te'] = self.scale_airfoil(scale)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.points['le'], self.points['ps'], self.points['ss'], self.points['te'] = self.move_airfoil(cmp_X, cmp_Y, wng_X, wng_Y, seg_X, seg_Y)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.points['le'], self.points['ps'], self.points['ss'], self.points['te'] = self.rotate_airfoil(incidence)
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

        self.segments = []
    
    def move_wing(self, wng_X:float, wng_Y:float):

        move_X = wng_X
        move_Y = wng_Y

        print(f"> Moving wing geometry by X:{move_X}, Y:{move_Y}...")

        tmp_le = np.vstack([self.geom['le'][0] + move_X, self.geom['le'][1] + move_Y])
        tmp_ss = np.vstack([self.geom['ps'][0] + move_X, self.geom['ps'][1] + move_Y])
        tmp_ps = np.vstack([self.geom['ss'][0] + move_X, self.geom['ss'][1] + move_Y])
        tmp_te = np.vstack([self.geom['te'][0] + move_X, self.geom['te'][1] + move_Y])

        tmp_c_le = np.vstack([self.points['le'][0] + move_X, self.points['le'][1] + move_Y])
        tmp_c_ss = np.vstack([self.points['ps'][0] + move_X, self.points['ps'][1] + move_Y])
        tmp_c_ps = np.vstack([self.points['ss'][0] + move_X, self.points['ss'][1] + move_Y])
        tmp_c_te = np.vstack([self.points['te'][0] + move_X, self.points['te'][1] + move_Y])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te

    def scale_airfoil(self, scale:float):

        print(f"> Scaling airfoil geometry by {scale}...")

        tmp_le = scale * np.array(self.geom['le'])
        tmp_ps = scale * np.array(self.geom['ps'])
        tmp_ss = scale * np.array(self.geom['ss'])
        tmp_te = scale * np.array(self.geom['te'])

        tmp_c_le = scale * np.array(self.points['le'])
        tmp_c_ps = scale * np.array(self.points['ps'])
        tmp_c_ss = scale * np.array(self.points['ss'])
        tmp_c_te = scale * np.array(self.points['te'])

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

        tmp_c_le = np.dot(rotation_matrix, self.points['le'])
        tmp_c_ps = np.dot(rotation_matrix, self.points['ps'])
        tmp_c_ss = np.dot(rotation_matrix, self.points['ss'])
        tmp_c_te = np.dot(rotation_matrix, self.points['te'])

        return tmp_le, tmp_ps, tmp_ss, tmp_te, tmp_c_le, tmp_c_ps, tmp_c_ss, tmp_c_te
    
    def update_airfoil(self):
        print("Restoring airfoil geometry...")
        self.geom['le'] = self.airfoil.geom['le']
        self.geom['ps'] = self.airfoil.geom['ps']
        self.geom['ss'] = self.airfoil.geom['ss']
        self.geom['te'] = self.airfoil.geom['te']

        self.points['le'] = self.airfoil.constr['le']
        self.points['ps'] = self.airfoil.constr['ps']
        self.points['ss'] = self.airfoil.constr['ss']
        self.points['te'] = self.airfoil.constr['te']

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
        print(f"> {cmp_X}, {cmp_Y}, {cmp_Z}")
        print(f"> > {wng_X}, {wng_Y}, {wng_Z}")
        print(f"> > > {seg_X}, {seg_Y}, {seg_Z}, {scale}, {incidence}")

        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.points['le'], self.points['ps'], self.points['ss'], self.points['te'] = self.scale_airfoil(scale)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.points['le'], self.points['ps'], self.points['ss'], self.points['te'] = self.move_airfoil(cmp_X, cmp_Y, wng_X, wng_Y, seg_X, seg_Y)
        print(".")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.points['le'], self.points['ps'], self.points['ss'], self.points['te'] = self.rotate_airfoil(incidence)
        print(".")
        print("Done!")

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

        print(f"> Moving component geometry by X:{cmp_X}, Y:{cmp_Y}, Z:{cmp_Z}...")

        tmp_X = self.params['origin_X'] + cmp_X
        tmp_Y = self.params['origin_Y'] + cmp_Y
        tmp_Z = self.params['origin_Z'] + cmp_Z

        return tmp_X, tmp_Y, tmp_Z
    
    def restore_component(self):
        print("Restoring component params...")
        self.params['origin_X'] = 0
        self.params['origin_Y'] = 0
        self.params['origin_Z'] = 0

    def transform_airfoil(self, grandparent_index, parent_index, item_index):

        self.restore_component()

        cmp_X = globals.PROJECT.project_components[grandparent_index].origin_X
        cmp_Y = globals.PROJECT.project_components[grandparent_index].origin_Y
        cmp_Z = globals.PROJECT.project_components[grandparent_index].origin_Z

        print("Transforming component...")
        print(f"> {cmp_X}, {cmp_Y}, {cmp_Z}")

        print(".")
        self.params['origin_X'], self.params['origin_Y'], self.params['origin_Z'] = self.move_component(cmp_X, cmp_Y, cmp_Z)
        print(".")
        print("Done!")
