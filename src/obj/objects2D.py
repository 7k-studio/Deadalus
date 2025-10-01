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

from src.arfdes.tools_airfoil import CreateBSpline
import src.globals as globals

class Airfoil_selig_format:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.infos = {'name': 'N/A'}
        self.format = 'selig'
        self.top_curve = []
        self.dwn_curve = []

class Airfoil:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.id = ''
        self.format = 'ddls-parametric'

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

        self.unit = {
            "chord":        "length",
            "origin_X":     "length",
            "origin_Y":     "length",
            "le_thickness": "length",
            "le_depth":     "length",
            "le_offset":    "length",
            "le_angle":     "angle",
            "te_thickness": "length",
            "te_depth":     "length",
            "te_offset":    "length",
            "te_angle":     "angle",
            "ps_fwd_angle": "angle",
            "ps_rwd_angle": "angle",
            "ps_fwd_accel": "length",
            "ps_rwd_accel": "length",
            "ss_fwd_angle": "angle",
            "ss_rwd_angle": "angle",
            "ss_fwd_accel": "length",
            "ss_rwd_accel": "length"
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

    def construct(self):
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

    def update(self):
        self.logger.info("Recalculating airfoil geometry...")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.constr['le'], self.constr['ps'], self.constr['ss'], self.constr['te']= self.construct()