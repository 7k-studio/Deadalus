import math
import numpy as np

from src.arfdes.tools_airfoil import CreateBSpline
import src.globals as globals

class Airfoil_selig_format:
    def __init__(self):
        self.infos = {'name': 'N/A'}
        self.top_curve = []
        self.dwn_curve = []

class Airfoil:
    def __init__(self):

        #Active parameters
        self.infos = {
            'name': 'Airfoil',
            'creation_date': '',
            'modification_date': '',
            'description': ''}

        self.params = {
            "chord": 1,
            "origin_X": 0,
            "origin_Y": 0,
            "le_thickness": 0.05,
            "le_depth": 0.04,
            "le_offset": 0,
            "le_angle": 0.02,
            "te_thickness": 0.01,
            "te_depth": 0.01,
            "te_offset": 0,
            "te_angle": 0.05,
            "ps_fwd_angle": 22,
            "ps_rwd_angle": -15,
            "ps_fwd_accel": 0.20,
            "ps_rwd_accel": 0.10,
            "ss_fwd_angle": -11,
            "ss_rwd_angle": -3,
            "ss_fwd_accel": 0.16,
            "ss_rwd_accel": 0.40
        }

        self.geom = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

        self.constr = {
            'le': [],
            'ps': [],
            'ss': [],
            'te': []
        }

    def construct_airfoil(self):
        # Leading Edge calculations
        p_le_start = [self.params['origin_X'], self.params['origin_Y']+self.params['le_offset']]
        p_le_end = [p_le_start[0]+self.params['le_depth']*math.cos(np.radians(self.params['le_angle'])),p_le_start[1]+(self.params['le_depth']*math.sin(np.radians(self.params['le_angle'])))]

        a0 = math.tan(np.radians(90+self.params['le_angle'])) # Directional param of the leading edge straight and the pararel one
        a1 = math.tan(np.radians(self.params['ps_fwd_angle']+self.params['le_angle'])) # Directional param of the pressure side forward slope
        a2 = math.tan(np.radians(self.params['ss_fwd_angle']+self.params['le_angle'])) # Directional param of the suction side forward slope

        b0 = p_le_start[1]-a0*p_le_start[0] # Positional parameter of the leading edge straight 'Origin Point'
        b0p = p_le_end[1]-a0*p_le_end[0]
        b1 = p_le_end[1]+(self.params['le_thickness']/2*math.cos(np.radians(self.params['le_angle'])))-a1*(p_le_end[0]-self.params['le_thickness']/2*math.sin(np.radians(self.params['le_angle'])))
        b2 = p_le_end[1]-(self.params['le_thickness']/2*math.cos(np.radians(self.params['le_angle'])))-a2*(p_le_end[0]+self.params['le_thickness']/2*math.sin(np.radians(self.params['le_angle'])))

        p_le_t = [(b1-b0)/(a0-a1),a0*((b1-b0)/(a0-a1))+b0] # G1 upper point
        p_le_d = [(b2-b0)/(a0-a2),a0*((b2-b0)/(a0-a2))+b0] # G1 lower point
        p_le_ps = [(b1-b0p)/(a0-a1),a0*((b1-b0p)/(a0-a1))+b0p] # G0 with with the pressure side
        p_le_ss = [(b2-b0p)/(a0-a2),a0*((b2-b0p)/(a0-a2))+b0p] # G0 with with the suction side

        le_constr = np.vstack([p_le_ss, p_le_d, p_le_t, p_le_ps]).T

        p_te_start = [self.params['origin_X']+self.params['chord'], self.params['origin_Y']+self.params['te_offset']]
        p_te_end = [p_te_start[0]-self.params['te_depth']*math.cos(np.radians(self.params['te_angle'])), p_te_start[1]-(self.params['te_depth']*math.sin(np.radians(self.params['te_angle'])))]
        a3 = math.tan(np.radians(90+self.params['te_angle']))
        a4 = math.tan(np.radians(self.params['ps_rwd_angle']+self.params['te_angle']))
        a5 = math.tan(np.radians(self.params['ss_rwd_angle']+self.params['te_angle']))
        b3 = p_te_start[1]-a3*p_te_start[0]
        b3p = p_te_end[1]-a3*p_te_end[0]
        b4 = p_te_end[1]+(self.params['te_thickness']/2*math.cos(np.radians(self.params['te_angle'])))-a4*(p_te_end[0]-self.params['te_thickness']/2*math.sin(np.radians(self.params['te_angle'])))
        b5 = p_te_end[1]-(self.params['te_thickness']/2*math.cos(np.radians(self.params['te_angle'])))-a5*(p_te_end[0]+self.params['te_thickness']/2*math.sin(np.radians(self.params['te_angle'])))

        p_te_t = [(b4-b3)/(a3-a4),a3*((b4-b3)/(a3-a4))+b3] # G1 upper point
        p_te_d = [(b5-b3)/(a3-a5),a3*((b5-b3)/(a3-a5))+b3] # G1 lower point
        p_te_ps = [(b4-b3p)/(a3-a4),a3*((b4-b3p)/(a3-a4))+b3p] # G0 with with the pressure side
        p_te_ss = [(b5-b3p)/(a3-a5),a3*((b5-b3p)/(a3-a5))+b3p] # G0 with with the suction side

        te_constr = np.vstack([p_te_ss, p_te_d, p_te_t, p_te_ps]).T

        p_ps_le = p_le_ps
        p_ps_te = p_te_ps
        p_ps_1 = [self.params['origin_X']+self.params['ps_fwd_accel'], a1*(self.params['origin_X']+self.params['ps_fwd_accel'])+b1]
        p_ps_2 = [p_ps_te[0]-self.params['ps_rwd_accel'], a4*(p_ps_te[0]-self.params['ps_rwd_accel'])+b4]   
        ps_constr = np.vstack([p_ps_le, p_ps_1, p_ps_2, p_ps_te]).T
        p_ss_le = p_le_ss
        p_ss_te = p_te_ss
        p_ss_1 = [self.params['origin_X']+self.params['ss_fwd_accel'], a2*(self.params['origin_X']+self.params['ss_fwd_accel'])+b2]
        p_ss_2 = [p_ss_te[0]-self.params['ss_rwd_accel'], a5*(p_ss_te[0]-self.params['ss_rwd_accel'])+b5]   
        ss_constr = np.vstack([p_ss_le, p_ss_1, p_ss_2, p_ss_te]).T

        # Generate Splines
        le_spline = CreateBSpline(le_constr)
        te_spline = CreateBSpline(te_constr)
        ps_spline = CreateBSpline(ps_constr)
        ss_spline = CreateBSpline(ss_constr)

        return le_spline, ps_spline, ss_spline, te_spline, le_constr, ps_constr, ss_constr, te_constr

    def update_airfoil(self):
        print("Recalculating airfoil geometry...")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.constr['le'], self.constr['ps'], self.constr['ss'], self.constr['te']= self.construct_airfoil()

class Segment:
    def __init__(self):
        self.infos = {'name': 'segment',
                      'creation_date': '',
                      'modification_date': ''}
        
        self.airfoil = Airfoil()
        self.anchor = 'G0' # G1 or G2

        self.params = {
            'origin_X': 0,
            'origin_Y': 0,
            'origin_Z': 0,
            'incidence': 0,
            'scale': 1,
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
