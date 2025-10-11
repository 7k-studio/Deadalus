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
import sys
import numpy as np
import tools_program as tools

#from src.arfdes.tools_airfoil import CreateBSpline
#import src.globals as globals

class LeadingEdge:
    def __init__(self):
        self.params = {
            "thickness": 0.05,
            "offset": 0,
            "angle": 0.02,
            "ps_tan": 0.02,
            "ps_slope": 10,
            "ps_curv": 0.01,
            "ss_tan": 0.02,
            "ss_slope": 10,
            "ss_curv": 0.01,
        }

        self.unit = {
            "thickness": "m",
            "offset":    "m",
            "angle":     "deg",
            "ps_tan":    "m",
            "ps_slope":  "deg",
            "ps_curv":   "m",
            "ss_tan":    "m",
            "ss_slope":  "deg",
            "ss_curv":   "m",
        }

class TrailingEdge:
    def __init__(self):
        self.params = {
            "thickness": 0.05,
            "offset": 0,
            "angle": 0.02,
            "ps_tan": 0.02,
            "ps_slope": 10,
            "ps_curv": 0.01,
            "ss_tan": 0.02,
            "ss_slope": 10,
            "ss_curv": 0.01,
        }

        self.unit = {
            "thickness": "m",
            "offset":    "m",
            "angle":     "deg",
            "ps_tan":    "m",
            "ps_slope":  "deg",
            "ps_curv":   "m",
            "ss_tan":    "m",
            "ss_slope":  "deg",
            "ss_curv":   "m",
        }

class PressureSide:
    def __init__(self):
        self.params = {
            "fwd_wedge": 0,
            "fwd_tan":   0.20,
            "fwd_slope": 0,
            "fwd_curv":  0.20,
            "rwd_wedge": 0,
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

class SuctionSide:
    def __init__(self):
        self.params = {
            "fwd_wedge": 0,
            "fwd_tan":   0.20,
            "fwd_slope": 0,
            "fwd_curv":  0.20,
            "rwd_wedge": 0,
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
            "origin_X":  0,
            "origin_Y":  0,
            "stretch":   1,
            "incidence": 0,
        }

        self.unit = {
            "origin_X":     "m",
            "origin_Y":     "m",
            "stretch":      "m",
            "incidence":    "deg",
        }

        self.LE = LeadingEdge()
        self.TE = TrailingEdge()
        self.PS = PressureSide()
        self.SS = SuctionSide()

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
        # Creating orignin points
        p_le_org = [self.params['origin_X'], self.params['origin_Y']+self.LE.params['offset']]
        p_te_org = tools.vec_translate(p_le_org, self.params['stretch'], self.params["incidence"])

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
            p_ps_fwd_tan = tools.vec_translate(p_le_u, self.PS.params['fwd_tan']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_le_u

        try:
            p_ps_rwd_tan = tools.vec_translate(p_te_u, -self.PS.params['rwd_tan']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.PS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_te_u

        try:
            p_ps_fwd_crv = tools.vec_translate(p_ps_fwd_tan, self.PS.params['fwd_curv']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]+self.PS.params["fwd_slope"]))
        except ZeroDivisionError:
            p_ps_fwd_crv = p_ps_fwd_tan

        try:
            p_ps_rwd_crv = tools.vec_translate(p_ps_rwd_tan, -self.PS.params['rwd_curv']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.PS.params["rwd_wedge"]+self.PS.params["rwd_slope"]))
        except ZeroDivisionError:
            p_ps_fwd_tan = p_ps_rwd_tan

        #===================================
        # Creating handle for Suction Side
        #===================================
        try:
            p_ss_fwd_tan = tools.vec_translate(p_le_d, self.SS.params['fwd_tan']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.SS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_le_d

        try:
            p_ss_rwd_tan = tools.vec_translate(p_te_d, -self.SS.params['rwd_tan']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.SS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_te_d

        try:
            p_ss_fwd_crv = tools.vec_translate(p_ss_fwd_tan, self.SS.params['fwd_curv']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.SS.params["fwd_wedge"]+self.SS.params["fwd_slope"]))
        except ZeroDivisionError:
            p_ss_fwd_tan = p_ss_fwd_tan

        try:
            p_ss_rwd_crv = tools.vec_translate(p_ss_rwd_tan, -self.SS.params['rwd_curv']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.SS.params["rwd_wedge"]+self.SS.params["rwd_slope"]))
        except ZeroDivisionError:
            p_ss_rwd_crv = p_ss_rwd_tan

        #===================================
        # Creating handle for Leading Edge
        #===================================
        try:
            p_le_ps_tan = tools.vec_translate(p_le_u, -self.LE.params['ps_tan']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_le_ps_tan = p_le_u

        try:
            p_le_ss_tan = tools.vec_translate(p_le_d, -self.LE.params['ss_tan']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.PS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_le_ss_tan = p_le_d

        try:
            p_le_ps_crv = tools.vec_translate(p_le_ps_tan, -self.LE.params['ps_curv']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.PS.params["fwd_wedge"]+self.LE.params["ps_slope"]))
        except ZeroDivisionError:
            p_le_ps_crv = p_le_ps_tan

        try:
            p_le_ss_crv = tools.vec_translate(p_le_ss_tan, -self.LE.params['ss_curv']/self.params['stretch'], (self.params["incidence"]+self.LE.params["angle"]+self.PS.params["rwd_wedge"]+self.LE.params["ss_slope"]))
        except ZeroDivisionError:
            p_le_ss_tan = p_le_ss_tan

        #===================================
        # Creating handle for Trailing Edge
        #===================================
        try:
            p_te_ps_tan = tools.vec_translate(p_te_u, self.TE.params['ps_tan']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.PS.params["fwd_wedge"]))
        except ZeroDivisionError:
            p_te_ps_tan = p_te_u

        try:
            p_te_ss_tan = tools.vec_translate(p_te_d, self.TE.params['ss_tan']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.PS.params["rwd_wedge"]))
        except ZeroDivisionError:
            p_te_ss_tan = p_te_d

        try:
            p_te_ps_crv = tools.vec_translate(p_te_ps_tan, self.TE.params['ps_curv']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.PS.params["fwd_wedge"]+self.TE.params["ps_slope"]))
        except ZeroDivisionError:
            p_te_ps_crv = p_te_ps_tan

        try:
            p_te_ss_crv = tools.vec_translate(p_te_ss_tan, self.TE.params['ss_curv']/self.params['stretch'], (self.params["incidence"]+self.TE.params["angle"]+self.PS.params["rwd_wedge"]+self.TE.params["ss_slope"]))
        except ZeroDivisionError:
            p_te_ss_tan = p_te_ss_tan

        le_constr = np.vstack([p_le_u, p_le_ps_tan, p_le_ps_crv, p_le_ss_crv, p_le_ss_tan, p_le_d]).T

        te_constr = np.vstack([p_te_u, p_te_ps_tan, p_te_ps_crv, p_te_ss_crv, p_te_ss_tan, p_te_d]).T

        ps_constr = np.vstack([p_le_u, p_ps_fwd_tan, p_ps_fwd_crv, p_ss_rwd_crv, p_ss_rwd_tan, p_te_u]).T

        ss_constr = np.vstack([p_le_d, p_ps_fwd_tan, p_ps_fwd_crv, p_ss_rwd_crv, p_ss_rwd_tan, p_te_d]).T

        # Generate Splines
        le_spline = tools.CreateBSpline(le_constr)
        te_spline = tools.CreateBSpline(te_constr)
        ps_spline = tools.CreateBSpline(ps_constr)
        ss_spline = tools.CreateBSpline(ss_constr)

        return le_spline, ps_spline, ss_spline, te_spline, le_constr, ps_constr, ss_constr, te_constr

    def update(self):
        self.logger.info("Recalculating airfoil geometry...")
        self.geom['le'], self.geom['ps'], self.geom['ss'], self.geom['te'], self.constr['le'], self.constr['ps'], self.constr['ss'], self.constr['te']= self.construct()