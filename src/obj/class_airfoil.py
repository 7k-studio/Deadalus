'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.

'''
import logging
import math
import sys
import numpy as np
import src.utils.tools_program as tools
from src.obj.objects2D import BSpline, Line

#from src.arfdes.tools_airfoil import CreateBSpline
#import src.globals as globals

class LeadingEdge:
    def __init__(self, program):
        self.DAEDALUS = program
        self.type = "F"

        self.params = {
            "thickness": 0.1,
            "angle": 0.0,
            "ps_tan": 0.05,
            "ps_slope": -20,
            "ps_curv": 0.05,
            "ss_tan": 0.05,
            "ss_slope": -20,
            "ss_curv": 0.05,
        }

        self.unit = {
            "thickness": "m",
            "ps_tan":    "m",
            "ps_slope":  "deg",
            "ps_curv":   "m",
            "ss_tan":    "m",
            "ss_slope":  "deg",
            "ss_curv":   "m",
        }

        self.spline = BSpline(self.DAEDALUS)

    def calc_position(self):

        index_min = min(range(len(self.spline.geom[0])), key=self.spline.geom[0].__getitem__)
        pos_X = self.spline.geom[0][index_min]
        pos_Y = self.spline.geom[1][index_min]

        return pos_X, pos_Y

        

class TrailingEdge:
    def __init__(self, program):
        self.DAEDALUS = program
        self.type = "F"

        self.params = {
            "thickness": 0.01,
            "angle": 0.0,
            "ps_tan": 0.004,
            "ps_slope": -30,
            "ps_curv": 0.004,
            "ss_tan": 0.004,
            "ss_slope": -30,
            "ss_curv": 0.004,
        }

        self.unit = {
            "thickness": "m",
            "angle":     "deg",
            "ps_tan":    "m",
            "ps_slope":  "deg",
            "ps_curv":   "m",
            "ss_tan":    "m",
            "ss_slope":  "deg",
            "ss_curv":   "m",
        }

        self.spline = BSpline(self.DAEDALUS)
    
    def calc_position(self):

        index_max = max(range(len(self.spline.geom[0])), key=self.spline.geom[0].__getitem__)
        pos_X = self.spline.geom[0][index_max]
        pos_Y = self.spline.geom[1][index_max]

        return pos_X, pos_Y

class PressureSide:
    def __init__(self, program):
        self.DAEDALUS = program

        self.type = "C"

        self.params = {
            "fwd_wedge": 10,
            "fwd_tan":   0.05,
            "fwd_slope": 0,
            "fwd_curv":  0.10,
            "rwd_wedge": 5,
            "rwd_tan":   0.10,
            "rwd_slope": 0,
            "rwd_curv":  0.10,
        }

        self.unit = {
            "fwd_wedge": "deg",
            "fwd_tan":   "m",
            "fwd_slope": "deg",
            "fwd_curv":  "m",
            "rwd_wedge": "deg",
            "rwd_tan":   "m",
            "rwd_slope": "deg",
            "rwd_curv":  "m"
        }

        self.spline = BSpline(self.DAEDALUS)

class SuctionSide:
    def __init__(self, program):
        self.DAEDALUS = program

        self.type = "C"

        self.params = {
            "fwd_wedge": 10,
            "fwd_tan":   0.05,
            "fwd_slope": 0,
            "fwd_curv":  0.10,
            "rwd_wedge": 5,
            "rwd_tan":   0.1,
            "rwd_slope": 0.0,
            "rwd_curv":  0.10,
        }

        self.unit = {
            "fwd_wedge": "deg",
            "fwd_tan":   "m",
            "fwd_slope": "deg",
            "fwd_curv":  "m",
            "rwd_wedge": "deg",
            "rwd_tan":   "m",
            "rwd_slope": "deg",
            "rwd_curv":  "m"
        }

        self.spline = BSpline(self.DAEDALUS)


class ChordLine:
    def __init__(self, parent):
        self.AIRFOIL = parent
        self.line = Line()
    
    def calc_chord(self):

        index_min = min(range(len(self.AIRFOIL.LE.spline.geom[0])), key=self.AIRFOIL.LE.spline.geom[0].__getitem__)
        X_min = self.AIRFOIL.LE.spline.geom[0][index_min]
        Y_min = self.AIRFOIL.LE.spline.geom[1][index_min]

        index_max = max(range(len(self.AIRFOIL.TE.spline.geom[0])), key=self.AIRFOIL.TE.spline.geom[0].__getitem__)
        X_max = self.AIRFOIL.TE.spline.geom[0][index_max]
        Y_max = self.AIRFOIL.TE.spline.geom[1][index_max]

        chord = math.sqrt((X_max-X_min)**2 + (Y_max-Y_min)**2)

        return chord

class CamberLine:
    def __init__(self):
        pass

class Airfoil:
    def __init__(self, program):
        self.DAEDALUS = program

        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = ""
        self.path = ""
        self.format = 'ddls-parametric'
        self.visible = False

        #Active parameters
        self.info = {
            'creation_date': '',
            'modification_date': '',
            'description': ''
            }

        self.params = {
            "origin_X":  0,
            "origin_Y":  0,
            "stretch":   1,
            "incline":   0,
        }

        self.unit = {
            "origin_X":     "m",
            "origin_Y":     "m",
            "stretch":      "m",
            "incline":    "deg",
        }

        self.stats = {
            "Chord": 1,
            "Position LE X": 0,
            "Position LE Y": 0,
            "Position TE X": 0,
            "Position TE Y": 0,
        }

        self.LE = LeadingEdge(self.DAEDALUS)
        self.TE = TrailingEdge(self.DAEDALUS)
        self.PS = PressureSide(self.DAEDALUS)
        self.SS = SuctionSide(self.DAEDALUS)

        self.CHORD = ChordLine(self)

    def construct(self):
        # Creating orignin points
        p_le_org = [self.params['origin_X'], self.params['origin_Y']]
        p_te_org = tools.vec_translate(p_le_org, self.params['stretch'], self.params["incline"])

        # Creating up (u) and down (d) point for Leading Edge PS and SS handle 
        p_le_u = tools.vec_translate(p_le_org, self.LE.params['thickness']/2, 90+self.LE.params["angle"])
        p_le_d = tools.vec_translate(p_le_org, -self.LE.params['thickness']/2, 90+self.LE.params["angle"])

        # Creating up (u) and down (d) point for Trailing Edge PS and SS handle 
        p_te_u = tools.vec_translate(p_te_org, self.TE.params['thickness']/2, 90+self.TE.params["angle"])
        p_te_d = tools.vec_translate(p_te_org, -self.TE.params['thickness']/2, 90+self.TE.params["angle"])

        #===================================
        # Creating handle for Pressure Side
        #===================================
        try:
            # PS (upper-like) forward tangent should move toward chordwards (inward), not further away.
            p_ps_fwd_tan = tools.vec_translate(p_le_u, self.PS.params['fwd_tan']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_le_u

        try:
            p_ps_rwd_tan = tools.vec_translate(p_te_u, -self.PS.params['rwd_tan']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]-self.PS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_te_u

        try:
            p_ps_fwd_crv = tools.vec_translate(p_ps_fwd_tan, self.PS.params['fwd_curv']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]+self.PS.params["fwd_slope"]))
        except ZeroDivisionError:
            p_ps_fwd_crv = p_ps_fwd_tan

        try:
            p_ps_rwd_crv = tools.vec_translate(p_ps_rwd_tan, -self.PS.params['rwd_curv']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]-self.PS.params["rwd_wedge"]-self.PS.params["rwd_slope"]))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_ps_rwd_tan

        #===================================
        # Creating handle for Suction Side
        #===================================
        try:
            # SS (lower-like) forward tangent should move toward chordwards (inward) as well.
            p_ss_fwd_tan = tools.vec_translate(p_le_d, self.SS.params['fwd_tan']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]-self.SS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_le_d

        try:
            p_ss_rwd_tan = tools.vec_translate(p_te_d, -self.SS.params['rwd_tan']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]+self.SS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_te_d

        try:
            p_ss_fwd_crv = tools.vec_translate(p_ss_fwd_tan, self.SS.params['fwd_curv']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]-self.SS.params["fwd_wedge"]-self.SS.params["fwd_slope"]))
        except ZeroDivisionError:
            p_ss_fwd_crv = p_ss_fwd_tan

        try:
            p_ss_rwd_crv = tools.vec_translate(p_ss_rwd_tan, -self.SS.params['rwd_curv']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]+self.SS.params["rwd_wedge"]+self.SS.params["rwd_slope"]))
        except ZeroDivisionError:
            p_ss_rwd_crv = p_ss_rwd_tan

        #===================================
        # Creating handle for Leading Edge
        #===================================
        try:
            p_le_ps_tan = tools.vec_translate(p_le_u, -self.LE.params['ps_tan']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_le_ps_tan = p_le_u

        try:
            p_le_ss_tan = tools.vec_translate(p_le_d, -self.LE.params['ss_tan']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]-self.SS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_le_ss_tan = p_le_d

        try:
            p_le_ps_crv = tools.vec_translate(p_le_ps_tan, -self.LE.params['ps_curv']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]-self.LE.params["ps_slope"]))
        except ZeroDivisionError:
            p_le_ps_crv = p_le_ps_tan

        try:
            p_le_ss_crv = tools.vec_translate(p_le_ss_tan, -self.LE.params['ss_curv']*self.params['stretch'], (self.params["incline"]+self.LE.params["angle"]-self.SS.params["fwd_wedge"]+self.LE.params["ss_slope"]))
        except ZeroDivisionError:
            p_le_ss_tan = p_le_ss_tan

        #===================================
        # Creating handle for Trailing Edge
        #===================================
        try:
            # TE-side tangents also should move inside toward chord (backward), not over-shoot +x.
            p_te_ps_tan = tools.vec_translate(p_te_u, self.TE.params['ps_tan']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]-self.PS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_te_ps_tan = p_te_u

        try:
            p_te_ss_tan = tools.vec_translate(p_te_d, self.TE.params['ss_tan']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]+self.SS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_te_ss_tan = p_te_d

        try:
            p_te_ps_crv = tools.vec_translate(p_te_ps_tan, self.TE.params['ps_curv']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]-self.PS.params["rwd_wedge"]+self.TE.params["ps_slope"]))
        except ZeroDivisionError:
            p_te_ps_crv = p_te_ps_tan

        try:
            p_te_ss_crv = tools.vec_translate(p_te_ss_tan, self.TE.params['ss_curv']*self.params['stretch'], (self.params["incline"]+self.TE.params["angle"]+self.SS.params["rwd_wedge"]-self.TE.params["ss_slope"]))
        except ZeroDivisionError:
            p_te_ss_crv = p_te_ss_tan

        self.LE.spline.control_points = np.vstack([p_le_u, p_le_ps_tan, p_le_ps_crv, p_le_ss_crv, p_le_ss_tan, p_le_d]).T

        self.TE.spline.control_points = np.vstack([p_te_u, p_te_ps_tan, p_te_ps_crv, p_te_ss_crv, p_te_ss_tan, p_te_d]).T

        self.PS.spline.control_points = np.vstack([p_le_u, p_ps_fwd_tan, p_ps_fwd_crv, p_ps_rwd_crv, p_ps_rwd_tan, p_te_u]).T

        self.SS.spline.control_points = np.vstack([p_le_d, p_ss_fwd_tan, p_ss_fwd_crv, p_ss_rwd_crv, p_ss_rwd_tan, p_te_d]).T

        # Generate Splines
        self.LE.spline.create()
        self.TE.spline.create()
        self.PS.spline.create()
        self.SS.spline.create()

        self.logger.debug("LE, TE, PS, SS geometry established")

    def update(self):
        self.logger.info("Recalculating airfoil geometry...")
        self.construct()
        self.logger.info("Recalculating airfoil statistics...")
        self.stats['Chord'] = self.CHORD.calc_chord()
        self.stats['Position LE X'], self.stats['Position LE Y'] = self.LE.calc_position()
        self.stats['Position TE X'], self.stats['Position TE Y'] = self.TE.calc_position()

class SeligAirfoil:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = ""
        self.path = ""
        self.format = 'selig'
        
        self.top_curve = []
        self.dwn_curve = []