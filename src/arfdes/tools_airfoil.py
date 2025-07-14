from PyQt5.QtWidgets import QTreeWidgetItem
import numpy as np
import math
import os
from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d
from scipy.optimize import minimize, root_scalar
from scipy import interpolate
from tqdm import tqdm
import json
import src.obj as obj
import src.globals as globals  # Import from globals.py

def add_airfoil_to_tree(tree_menu=None, name="Unknown", airfoil_obj=None):
    """Add an airfoil to the list and tree menu."""
    modification_date = airfoil_obj.infos.get('modification_date', 'Unknown')
    creation_date = airfoil_obj.infos.get('creation_date', 'Unknown')
    description = airfoil_obj.infos.get('description', 'No description')
    tree_item = QTreeWidgetItem([name, str(modification_date), str(creation_date), description])
    tree_menu.addTopLevelItem(tree_item)
    print(f"Airfoil '{name}' added to the tree menu.")

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
    print("{} Coordinates".format(file))
    
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

    print(UP_points)
    print(DW_points)
    
    airfoil = obj.aero.Airfoil_selig_format()
    #airfoil.full_curve = np.vstack([UP_points, DW_points])
    airfoil.top_curve = UP_points
    airfoil.dwn_curve = DW_points
    airfoil.infos['name'] = airfoil_name
    
    return airfoil

def CreateBSpline(const_points):

    l=len(const_points[0])

    t=np.linspace(0,1,l-2,endpoint=True)
    t=np.append([0,0,0],t)
    t=np.append(t,[1,1,1])

    tck=[t,[const_points[0],const_points[1]],3]
    if globals.AIRFLOW.preferences['general']['performance'] == 'fast':
        # Use a faster method for performance
        u3=np.linspace(0,1,(max(l*1,25)),endpoint=True)
    if globals.AIRFLOW.preferences['general']['performance'] == 'normal':
        # Use a faster method for performance
        u3=np.linspace(0,1,(max(l*2,50)),endpoint=True)
    if globals.AIRFLOW.preferences['general']['performance'] == 'good':
        # Use a faster method for performance
        u3=np.linspace(0,1,(max(l*3,75)),endpoint=True)

    spline = splev(u3, tck)

    return spline

# Interpolate reference points to match the number of spline points
def interpolate_reference(reference, spline_points):
    ref_length = len(reference[0])
    ref_spline_length = len(spline_points[0])
    interpolator_x = interp1d(np.linspace(0, 1, ref_length), reference[0], kind='linear')
    interpolator_y = interp1d(np.linspace(0, 1, ref_length), reference[1], kind='linear')
    new_x = interpolator_x(np.linspace(0, 1, ref_spline_length))
    new_y = interpolator_y(np.linspace(0, 1, ref_spline_length))
    return np.array([new_x, new_y])

# Define the function to calculate error
def calculate_error(params, top_ref, dwn_ref):
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

def load_airfoil_from_json(self, fileName):
    """load the airfoil data from a JSON format file."""
    import src.obj.aero as aero
    Airfoil = aero.Airfoil()

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
            program_version = data["program version"]
            airfoil = data["airfoil"]
        except KeyError as e:
            print(f"ERROR: Missing key in ARF data - {e}")
            print("File may not load properly or is not compatible with AirFLOW")
            return None

        if program_version != globals.AIRFLOW.program_version:
            print("WARNING: Program version mismatch. Import may not be compatible.")

        try:
            # Set parameters in Airfoil.params dictionary
            Airfoil.params = {
                "chord": airfoil["chord"],
                "origin_X": airfoil["origin_X"],
                "origin_Y": airfoil["origin_Y"],
                "le_thickness": airfoil["le_thickness"],
                "le_depth": airfoil["le_depth"],
                "le_offset": airfoil["le_offset"],
                "le_angle": airfoil["le_angle"],
                "te_thickness": airfoil["te_thickness"],
                "te_depth": airfoil["te_depth"],
                "te_offset": airfoil["te_offset"],
                "te_angle": airfoil["te_angle"],
                "ps_fwd_angle": airfoil["ps_fwd_angle"],
                "ps_rwd_angle": airfoil["ps_rwd_angle"],
                "ps_fwd_accel": airfoil["ps_fwd_accel"],
                "ps_rwd_accel": airfoil["ps_rwd_accel"],
                "ss_fwd_angle": airfoil["ss_fwd_angle"],
                "ss_rwd_angle": airfoil["ss_rwd_angle"],
                "ss_fwd_accel": airfoil["ss_fwd_accel"],
                "ss_rwd_accel": airfoil["ss_rwd_accel"]
            }
            Airfoil.infos = {
                "name": airfoil["infos"]["name"],
                "creation_date": airfoil["infos"]["creation_date"],
                "modification_date": airfoil["infos"]["modification_date"],
                "description": airfoil["infos"]["description"]
            }
        except KeyError as e:
            print(f"ERROR: Missing key in ARF data - {e}")
            return None
        
        print("Append Airfoil: Success!")

        return Airfoil

def save_airfoil_to_json(self, airfoil_idx=None):
    """Save the airfoil data to a JSON format file."""
 
    current_airfoil = globals.PROJECT.project_airfoils[airfoil_idx]

    data = {
        "program name": globals.AIRFLOW.program_name,
        "program version": globals.AIRFLOW.program_version,
        "airfoil": {
            "infos": {
                **current_airfoil.infos,
                "name": str(current_airfoil.infos.get("name", "")),
                "creation_date": str(current_airfoil.infos.get("creation_date", "")),
                "modification_date": str(current_airfoil.infos.get("modification_date", "")),
                "description": str(current_airfoil.infos.get("description", ""))
            },
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
 
    json_object = json.dumps(data, indent=1)

    return json_object

def flip_airfoil_horizontally(airfoil):
    """Flip the airfoil horizontally."""
    flipped_airfoil = obj.aero.Airfoil()
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