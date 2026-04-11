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
import ezdxf
import ezdxf.layouts
from ezdxf.math import ConstructionArc, Vec3, BSpline
import numpy as np
import math

logger = logging.getLogger(__name__)

def calculate_length(points):
    length = 0
    for i in range(1, len(points)):
        length += Vec3(points[i]).distance(Vec3(points[i-1]))
    return length

def find_point_at_length(points, target_length):
    length = 0
    for i in range(1, len(points)):
        segment_length = Vec3(points[i]).distance(Vec3(points[i-1]))
        if length + segment_length >= target_length:
            ratio = (target_length - length) / segment_length
            return Vec3(points[i-1]) + (Vec3(points[i]) - Vec3(points[i-1])) * ratio
        length += segment_length
    return Vec3(points[-1])

def export_airfoil_to_dxf(airfoil, file_name=None, ):

    Z = 0
    
    doc = ezdxf.new()
    msp = doc.modelspace()

    #for idx, airfoil in enumerate(export_airfoil):

    if airfoil is not None and hasattr(airfoil, 'constr') and airfoil.constr['le'] is not None and len(airfoil.constr['le']) > 0:
        logger.info(f"Exporting airfoil {airfoil.name} to DXF...")

        # Sprawdzenie, czy wszystkie tablice mają wystarczającą ilość danych
        if len(airfoil.constr['le'][0]) > 0 and len(airfoil.constr['le'][1]) > 0:
            exp_le = airfoil.constr['le']
        else:
            logger.error(f"Airfoil {airfoil.name} has an empty or insufficient LE array.")

        if len(airfoil.constr['ps'][0]) > 0 and len(airfoil.constr['ps'][1]) > 0:
            exp_ps = airfoil.constr['ps']
        else:
            logger.error(f"Airfoil {airfoil.name} has an empty or insufficient PS array.")

        if len(airfoil.constr['ss'][0]) > 0 and len(airfoil.constr['ss'][1]) > 0:
            exp_ss = airfoil.constr['ss']
        else:
            logger.error(f"Airfoil {airfoil.name} has an empty or insufficient SS array.")

        if len(airfoil.constr['te'][0]) > 0 and len(airfoil.constr['te'][1]) > 0:
            exp_te = airfoil.constr['te']
        else:
            logger.error(f"Airfoil {airfoil.name} has an empty or insufficient TE array.")

    ps_Z_row = np.full((1, exp_ps.shape[1]), Z)
    ps = np.vstack((exp_ps, ps_Z_row)).T
    #ps_spline = msp.add_spline(ps)
    ps_spline = msp.add_open_spline(ps)
    
    ss_Z_row = np.full((1, exp_ss.shape[1]), Z)
    ss = np.vstack((exp_ss, ss_Z_row)).T
    #ss_spline = msp.add_spline(ss)
    ss_spline = msp.add_open_spline(ss)

    le_Z_row = np.full((1, exp_le.shape[1]), Z)
    le = np.vstack((exp_le, le_Z_row)).T
    #le_spline = msp.add_spline(le)
    le_spline = msp.add_open_spline(le)

    te_Z_row = np.full((1, exp_te.shape[1]), Z)
    te = np.vstack((exp_te, te_Z_row)).T
    #te_spline = msp.add_spline(te)
    te_spline = msp.add_open_spline(te)

    doc.saveas("{}".format(file_name))
