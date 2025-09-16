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

from PyQt5.QtWidgets import QTreeWidgetItem
import numpy as np
import math
import os
from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d
from scipy.optimize import minimize, root_scalar
from scipy import interpolate
from tqdm import tqdm
import json
import src.obj
import src.globals as globals  # Import from globals.py

def Reference_load(file):
    """Load airfoil coordinates from a file and return upper and lower points."""
    AirfoilCoord = []
    UP_points = []
    DW_points = []
    print("Loading airfoil from database...")
    try:
        with open(file) as file:
            for line in file:
                if line.startswith("Name:"):
                    airfoil_name = line.replace("Name:", '', 1)
                try:
                    x, y = map(float, line.split()) # split X and Y values into 
                    AirfoilCoord.append([x,y])
                except ValueError: # skip lines that dont contain numeric data
                    continue
    except FileNotFoundError:
        print("No file found!")
        pass
            
    np.array(AirfoilCoord)
    print("Chosen airfoils data read sucessfully!")
    
    i=0
    while AirfoilCoord[i][1] >= 0:
        UP_points.append(AirfoilCoord[i])
        i=i+1

    i=len(UP_points)-1
    while i < len(AirfoilCoord):
        DW_points.append(AirfoilCoord[i])
        i=i+1
    
    UP_points = np.array(UP_points)
    UP_points = UP_points[::-1, :]
    UP_points = UP_points.T
    
    DW_points = np.array(DW_points).T

    #print(UP_points)
    #print(DW_points)
    
    airfoil = src.obj.objects2D.Airfoil_selig_format()
    #airfoil.full_curve = np.vstack([UP_points, DW_points])
    airfoil.top_curve = UP_points
    airfoil.dwn_curve = DW_points
    airfoil.infos['name'] = airfoil_name
    print(f"Finished loading {airfoil.name} in selig format")
    
    return airfoil

def CreateBSpline(const_points, f=int(globals.DEADALUS.preferences['general']['performance'])):

    l=len(const_points[0])

    t=np.linspace(0,1,l-2,endpoint=True)
    t=np.append([0,0,0],t)
    t=np.append(t,[1,1,1])

    tck=[t,[const_points[0],const_points[1]],3]
    
    #f = int(globals.DEADALUS.preferences['general']['performance'])

    u3=np.linspace(0,1,(max(l*f/100,f)),endpoint=True)

    spline = splev(u3, tck)

    return spline

def interpolate_reference(reference, spline_points):
    """Interpolate reference points to match the number of spline points"""
    ref_length = len(reference[0])
    ref_spline_length = len(spline_points[0])
    interpolator_x = interp1d(np.linspace(0, 1, ref_length), reference[0], kind='linear')
    interpolator_y = interp1d(np.linspace(0, 1, ref_length), reference[1], kind='linear')
    new_x = interpolator_x(np.linspace(0, 1, ref_spline_length))
    new_y = interpolator_y(np.linspace(0, 1, ref_spline_length))
    return np.array([new_x, new_y])

def calculate_error(params, top_ref, dwn_ref):
    """Define the function to calculate error"""
    # Extract parameters
    chord, origin_X, origin_Y, le_thickness, le_depth, le_offset, le_angle, te_thickness, te_depth, te_offset, te_angle, \
        ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel, ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel = params

    le_angle = math.radians(le_angle)
    te_angle = math.radians(te_angle)
    ps_fwd_angle = math.radians(ps_fwd_angle)
    ps_rwd_angle = math.radians(ps_rwd_angle)
    ss_fwd_angle = math.radians(ss_fwd_angle)
    ss_rwd_angle = math.radians(ss_rwd_angle)

    # Leading edge control points
    p_le_start = [origin_X, origin_Y]
    a0 = math.tan(le_angle)
    a1 = math.tan(ps_fwd_angle)
    a2 = math.tan(ss_fwd_angle)
    b0 = p_le_start[1] - a0 * p_le_start[0]
    b1 = p_le_start[1] + le_thickness / 2 - a1 * (p_le_start[0] + le_depth)
    b2 = p_le_start[1] - le_thickness / 2 - a2 * (p_le_start[0] + le_depth)
    p_le_t = [(b1 - b0) / (a0 - a1), a0 * ((b1 - b0) / (a0 - a1)) + b0]
    p_le_d = [(b2 - b0) / (a0 - a2), a0 * ((b2 - b0) / (a0 - a2)) + b0]
    le_constr = np.vstack([p_le_d, p_le_start, p_le_t]).T

    # Trailing edge control points
    p_te_start = [origin_X + chord, origin_Y]
    a3 = math.tan(te_angle)
    a4 = math.tan(ps_rwd_angle)
    a5 = math.tan(ss_rwd_angle)
    b3 = p_te_start[1] - a3 * p_te_start[0]
    b4 = p_te_start[1] + te_thickness / 2 - a4 * (p_te_start[0] - te_depth)
    b5 = p_te_start[1] - te_thickness / 2 - a5 * (p_te_start[0] - te_depth)
    p_te_t = [(b4 - b3) / (a3 - a4), a3 * ((b4 - b3) / (a3 - a4)) + b3]
    p_te_d = [(b5 - b3) / (a3 - a5), a3 * ((b5 - b3) / (a3 - a5)) + b3]
    te_constr = np.vstack([p_te_d, p_te_start, p_te_t]).T

    # Create splines
    le_spline = CreateBSpline(le_constr)
    te_spline = CreateBSpline(te_constr)

    # Interpolate reference points to match spline length
    top_ref_interp = interpolate_reference(top_ref, le_spline)
    dwn_ref_interp = interpolate_reference(dwn_ref, te_spline)

    # Calculate error between splines and reference
    top_error = np.sum((le_spline[1] - top_ref_interp[1])**2 + (le_spline[0] - top_ref_interp[0])**2)
    bottom_error = np.sum((te_spline[1] - dwn_ref_interp[1])**2 + (te_spline[0] - dwn_ref_interp[0])**2)

    return top_error + bottom_error

def find_t_for_x(desired_x, tck):
    def equation(t):
        return splev(t, tck)[0] - desired_x  # x(t) - desired_x = 0

    result = root_scalar(equation, bracket=[0, 1], method='brentq')  # Solve for t
    if not result.converged:
        raise ValueError(f"Could not find t for X = {desired_x}")
    return result.root

def load_airfoil_from_json(fileName):
    """load the airfoil data from a JSON format file."""
    is_version_different =  False
    error_count = 0
    import src.obj.objects2D as objects2D
    Airfoil = objects2D.Airfoil()

    if fileName:
        try:
            with open(f"{fileName}", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            print("ERROR: File not found!")
        except json.JSONDecodeError:
            print("ERROR: During decoding JSON!")

    if data:
        try:
            airfoil_version = data["program version"]
            objects2D = data["airfoil"]
        except KeyError as e:
            print(f"ERROR: Missing key in ARF data - {e}")
            print("File may not load properly or is not compatible with DEADALUS")
            return None
        
        if airfoil_version:
            airfoil_version = airfoil_version.split("-")[0].split(".")
            program_version = globals.DEADALUS.program_version
            program_version = program_version.split("-")[0].split(".")

            if program_version[1] != airfoil_version[1] or program_version[0] != airfoil_version[0]:
                print("WARNING: Current program version is different from the saved airfoil version. Import may not be compatible.")
                is_version_different = True

        try:
            # Set parameters in Airfoil.params dictionary
            Airfoil.params = {
                "chord": objects2D["chord"],
                "origin_X": objects2D["origin_X"],
                "origin_Y": objects2D["origin_Y"],
                "le_thickness": objects2D["le_thickness"],
                "le_depth": objects2D["le_depth"],
                "le_offset": objects2D["le_offset"],
                "le_angle": objects2D["le_angle"],
                "te_thickness": objects2D["te_thickness"],
                "te_depth": objects2D["te_depth"],
                "te_offset": objects2D["te_offset"],
                "te_angle": objects2D["te_angle"],
                "ps_fwd_angle": objects2D["ps_fwd_angle"],
                "ps_rwd_angle": objects2D["ps_rwd_angle"],
                "ps_fwd_accel": objects2D["ps_fwd_accel"],
                "ps_rwd_accel": objects2D["ps_rwd_accel"],
                "ss_fwd_angle": objects2D["ss_fwd_angle"],
                "ss_rwd_angle": objects2D["ss_rwd_angle"],
                "ss_fwd_accel": objects2D["ss_fwd_accel"],
                "ss_rwd_accel": objects2D["ss_rwd_accel"]
            }
            Airfoil.infos = {
                "name": objects2D["infos"]["name"],
                "creation_date": objects2D["infos"]["creation_date"],
                "modification_date": objects2D["infos"]["modification_date"],
                "description": objects2D["infos"]["description"]
            }
        except KeyError as e:
            print(f"ERROR: Missing key in ARF data - {e}")
            return None
        
        if is_version_different == True:
            print(f"DEADALUS > Airfoil '{Airfoil.infos['name']}' loaded but should be checked!")
            error_count += 1
        else:
            print(f"DEADALUS > Airfoil '{Airfoil.infos['name']}' loaded successfully!")

        Airfoil.update()

        return Airfoil, error_count

def save_airfoil_to_json(airfoil_idx=None):
    """Save the airfoil data to a JSON format file."""
 
    current_airfoil = globals.PROJECT.project_airfoils[airfoil_idx]

    data = {
        "program name": globals.DEADALUS.program_name,
        "program version": globals.DEADALUS.program_version,
        "airfoil": {
            "infos": {
                **current_airfoil.infos,
                "name": str(current_airfoil.infos.get("name", "")),
                "creation_date": str(current_airfoil.infos.get("creation_date", "")),
                "modification_date": str(current_airfoil.infos.get("modification_date", "")),
                "description": str(current_airfoil.infos.get("description", ""))
            },
            "params": {
                "chord": current_airfoil.params["chord"],
                "origin_X": current_airfoil.params["origin_X"],
                "origin_Y": current_airfoil.params["origin_Y"],
                "le_thickness": current_airfoil.params["le_thickness"],
                "le_depth": current_airfoil.params["le_depth"],
                "le_offset": current_airfoil.params["le_offset"],
                "le_angle": current_airfoil.params["le_angle"],
                "te_thickness": current_airfoil.params["te_thickness"],
                "te_depth": current_airfoil.params["te_depth"],
                "te_offset": current_airfoil.params["te_offset"],
                "te_angle": current_airfoil.params["te_angle"],
                "ps_fwd_angle": current_airfoil.params["ps_fwd_angle"],
                "ps_rwd_angle": current_airfoil.params["ps_rwd_angle"],
                "ps_fwd_accel": current_airfoil.params["ps_fwd_accel"],
                "ps_rwd_accel": current_airfoil.params["ps_rwd_accel"],
                "ss_fwd_angle": current_airfoil.params["ss_fwd_angle"],
                "ss_rwd_angle": current_airfoil.params["ss_rwd_angle"],
                "ss_fwd_accel": current_airfoil.params["ss_fwd_accel"],
                "ss_rwd_accel": current_airfoil.params["ss_rwd_accel"]
            }
        }
    }
 
    json_object = json.dumps(data, indent=1)

    return json_object

def flip_airfoil_horizontally(airfoil):
    """Flip the airfoil horizontally."""
    flipped_airfoil = src.obj.objects2D.Airfoil()
    flipped_airfoil.infos = airfoil.infos.copy()
    flipped_airfoil.params = airfoil.params.copy()

    flipped_airfoil.params['chord'] = airfoil.params['chord']
    flipped_airfoil.params['origin_X'] = airfoil.params['origin_X']
    flipped_airfoil.params['origin_Y'] = airfoil.params['origin_Y']
    flipped_airfoil.params['le_thickness'] = airfoil.params['le_thickness']
    flipped_airfoil.params['le_depth'] = airfoil.params['le_depth']
    flipped_airfoil.params['le_offset'] = -airfoil.params['le_offset']
    flipped_airfoil.params['le_angle'] = -airfoil.params['le_angle']
    flipped_airfoil.params['te_thickness'] = airfoil.params['te_thickness']
    flipped_airfoil.params['te_depth'] = airfoil.params['te_depth']
    flipped_airfoil.params['te_offset'] = -airfoil.params['te_offset']
    flipped_airfoil.params['te_angle'] = -airfoil.params['te_angle']
    flipped_airfoil.params['ps_fwd_angle'] = -airfoil.params['ss_fwd_angle']
    flipped_airfoil.params['ps_rwd_angle'] = -airfoil.params['ss_rwd_angle']
    flipped_airfoil.params['ps_fwd_accel'] = airfoil.params['ss_fwd_accel']
    flipped_airfoil.params['ps_rwd_accel'] = airfoil.params['ss_rwd_accel']
    flipped_airfoil.params['ss_fwd_angle'] = -airfoil.params['ps_fwd_angle']
    flipped_airfoil.params['ss_rwd_angle'] = -airfoil.params['ps_rwd_angle']
    flipped_airfoil.params['ss_fwd_accel'] = airfoil.params['ps_fwd_accel']
    flipped_airfoil.params['ss_rwd_accel'] = airfoil.params['ps_rwd_accel']

    return flipped_airfoil