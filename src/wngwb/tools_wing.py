import math
import sys
import src.obj.aero as aero
import json
import os
import numpy as np
from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d
from scipy.optimize import minimize, root_scalar
from scipy import interpolate
from PyQt5.QtWidgets import QTreeWidgetItem

#import tools.DXFmodule
import random
from tqdm import tqdm
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QTableWidget, QTableWidgetItem, QMainWindow, QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import src.globals as globals


#import sympy as sym
def DataBase_info(default_loc):
    default_loc = default_loc
    os.chdir('data')
    #storage = [f for f in os.listdir() if os.path.isfile(f)]
    storage = os.listdir()
    os.chdir(default_loc)
    return storage

def DataBase_load(file, default_loc):
    AirfoilCoord = []
    UP_points = []
    DW_points = []
    print("Loading airfoil from database...")
    os.chdir('data')
    print(os.getcwd())
    try:
        with open(file) as file:
            for line in file:
                print(line)
                if line.startswith("Name:"):
                    airfoil_name = line.replace("Name:", '', 1)
                try:
                    x, y = map(float, line.split()) # split X and Y values into 
                    AirfoilCoord.append([x,y])
                except ValueError: # skip lines that dont contain numeric data
                    continue
    except FileNotFoundError:
        print("No file found!")
        quit()
    os.chdir(default_loc)
            
    np.array(AirfoilCoord)
    print("Chosen airfoils data read sucessfully!")
    print("{} Coordinates".format(file))
    #print(AirfoilCoord)
    
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
    
    return AirfoilCoord, UP_points, DW_points, airfoil_name

def Save(program_info, component, airfoil_count, arf_lst):

    desiged_component = {
            "component name": component,
            "element count": airfoil_count
        }
    
    for i in range(0, airfoil_count):
        desiged_component[f"airfoil_{i}"] = {
                    "position": i,
                    "name": arf_lst[i].name,
                    "origin": arf_lst[i].origin,
                    "length": arf_lst[i].scale,
                    "incidence": arf_lst[i].incidence,
                    "full curve": np.array(arf_lst[i].full_curve).T.tolist(),
                    "top curve": np.array(arf_lst[i].top_curve).tolist(),
                    "dwn curve": np.array(arf_lst[i].dwn_curve).tolist(),
                    "le org": np.array(arf_lst[i].le_org).tolist(),
                    "ps org": np.array(arf_lst[i].ps_org).tolist(),
                    "ss org": np.array(arf_lst[i].ss_org).tolist(),
                    "te org": np.array(arf_lst[i].te_org).tolist(),
                    "le type": arf_lst[i].le_type,
                    "le value":arf_lst[i].le_value,
                    "te type": arf_lst[i].te_type,
                    "te value": arf_lst[i].le_value
                }

    data = {
        "program name": program_info.name,
        "program version": program_info.version,
        "file name": program_info.file_name,
        "designed component": desiged_component
    }

    json_object = json.dumps(data, indent=1)

    with open(f"{program_info.file_name}.paf", "w") as outfile:
        outfile.write(json_object)

    print("File write: Success!")

def SaveAs(program_info, component, airfoil_count, arf_lst):

    save_as = input("Save file as: ")

    desiged_component = {
            "component name": component,
            "element count": airfoil_count
        }
    
    for i in range(0, airfoil_count):
        desiged_component[f"airfoil_{i}"] = {
                    "position": i,
                    "name": arf_lst[i].name,
                    "origin": arf_lst[i].origin,
                    "length": arf_lst[i].scale,
                    "incidence": arf_lst[i].incidence,
                    "full curve": np.array(arf_lst[i].full_curve).T.tolist(),
                    "top curve": np.array(arf_lst[i].top_curve).tolist(),
                    "dwn curve": np.array(arf_lst[i].dwn_curve).tolist(),
                    "le org": np.array(arf_lst[i].le_org).tolist(),
                    "ps org": np.array(arf_lst[i].ps_org).tolist(),
                    "ss org": np.array(arf_lst[i].ss_org).tolist(),
                    "te org": np.array(arf_lst[i].te_org).tolist(),
                    "le type": arf_lst[i].le_type,
                    "le value":arf_lst[i].le_value,
                    "te type": arf_lst[i].te_type,
                    "te value": arf_lst[i].le_value
                }

    data = {
        "program name": program_info.name,
        "program version": program_info.version,
        "file name": save_as,
        "designed component": desiged_component
    }

    json_object = json.dumps(data, indent=1)

    with open(f"{save_as}.paf", "w") as outfile:
        outfile.write(json_object)

    print("File write: Success!")

    return save_as

def Load(arf_lst):

    file_name = input("Input file name: ")

    try:
        with open(f"{file_name}.paf", "r") as file:
            data = json.load(file)
            print("File load: Success!")
    except FileNotFoundError:
        print("File not found!")
    except json.JSONDecodeError:
        print("Error decoding JSON!")

    file_name = data["program name"]
    component = data["designed component"]["component name"]
    airfoil_count = data["designed component"]["element count"]

    for i in range (0, airfoil_count):

        arf_dt = data["designed component"][f"airfoil_{i}"]

        arf_lst[i].full_curve = arf_dt["full curve"]
        arf_lst[i].top_curve =  arf_dt["top curve"]
        arf_lst[i].dwn_curve =  arf_dt["dwn curve"]
        arf_lst[i].le_org = arf_dt["le org"]
        arf_lst[i].ps_org = arf_dt["ps org"]
        arf_lst[i].ss_org = arf_dt["ss org"]
        arf_lst[i].te_org = arf_dt["te org"]
        arf_lst[i].name = arf_dt["name"]
        arf_lst[i].origin = arf_dt["origin"]
        arf_lst[i].scale = arf_dt["length"]
        arf_lst[i].incidence = arf_dt["incidence"]
        arf_lst[i].le_type = arf_dt["le type"]
        arf_lst[i].le_value = arf_dt["le value"]
        arf_lst[i].te_type = arf_dt["te type"]
        arf_lst[i].te_value = arf_dt["te type"]

    return file_name, component, airfoil_count, arf_lst

def Convert(le_depth, te_depth, UP_points, DW_points):
    airfoil_chord = DW_points[0][len(DW_points[0])-1]

    le_perc = le_depth
    te_perc = te_depth

    LE_points = []
    TE_points = []
    PS_points = []
    SS_points = []

    le_chord = airfoil_chord * le_perc
    te_chord = airfoil_chord - airfoil_chord * te_perc

    print('Cieciwa aerodynamiczna: ', airfoil_chord)
    print('Glebokosc krawedzi natarcia: ', le_chord)
    print('Glebokosc krawedzi splywu: ', te_chord)

    # Utworzenie splajnu przy uzyciu funkcji splprep (k=3 dla splajnu kubicznego)
    #full, u = splprep([FullAirfoil[0], FullAirfoil[1]], s=0, k=3, per=True)
    dwn, u = splprep([DW_points[0], DW_points[1]], s=0)
    top, u = splprep([UP_points[0], UP_points[1]], s=0)

    for i in range(len(DW_points[0])):
        #print('Position ', DW_points[0][i])
        #print(LE_points)
        #print('DW ', DW_points[1][i])
        #print('UP ', UP_points[1][i])
        if le_chord < DW_points[0][i]:
            break
        LE_points.append([DW_points[0][i],DW_points[1][i]])
        LE_points.insert(0,[UP_points[0][i],UP_points[1][i]])

        
    top_le_p = np.array([[le_chord], [float(splev(le_chord, top)[1])]])
    dwn_le_p = np.array([[le_chord], [float(splev(le_chord, dwn)[1])]])

    LE_points = np.array(LE_points).T
    LE_points = np.hstack([top_le_p, LE_points, dwn_le_p])

    for i in range(len(DW_points[0]) -1, -1, -1):
        if te_chord > DW_points[0][i]:
            break
        TE_points.append([DW_points[0][i],DW_points[1][i]])
        TE_points.insert(0,[UP_points[0][i],UP_points[1][i]])
        
    top_te_p = np.array([[te_chord], [float(splev(te_chord, top)[1])]])
    dwn_te_p = np.array([[te_chord], [float(splev(te_chord, dwn)[1])]])

    TE_points = np.array(TE_points).T
    TE_points = np.hstack([top_te_p, TE_points, dwn_te_p])

    spl_refin_fac = 1

    top_u = np.linspace(0, 1, 2 * len(u) - 1)  # Dwukrotna liczba punktow w rownych odstepach
    dwn_u = np.linspace(0, 1, 2 * len(u) - 1)  # Dwukrotna liczba punktow w rownych odstepach
    PS_points = splev(top_u, top)  # Obliczenie nowych punktow na splajnie
    SS_points = splev(dwn_u, dwn)

    top_le = splev(np.linspace(0, le_chord, spl_refin_fac * len(u) - 1), top)
    dwn_le = splev(np.linspace(0, le_chord, spl_refin_fac * len(u) - 1), dwn)
    top_le = np.array([row[1:] for row in top_le])
    top_le = np.array([row[::-1] for row in top_le])
    le = np.hstack([top_le, dwn_le])

    ps = np.array(splev(np.linspace(le_chord, te_chord, spl_refin_fac * len(u) -1), top))
    ss = np.array(splev(np.linspace(le_chord, te_chord, spl_refin_fac * len(u) -1), dwn))

    top_te = splev(np.linspace(te_chord, 1, spl_refin_fac * len(u) -1), top)
    dwn_te = splev(np.linspace(te_chord, 1, spl_refin_fac * len(u) -1), dwn)
    dwn_te = np.array([row[::-1] for row in dwn_te])
    dwn_te = np.array([row[1:] for row in dwn_te])
    te = np.hstack([top_te, dwn_te]) 

    #new_u = np.linspace(0, 1, 2 * len(u) - 1)  # Dwukrotna liczba punktów w równych odstępach
    #new_points = splev(new_u, top)  # Obliczenie nowych punktów na splajnie
    
    print('le: ', le.dtype, ' ps: ', ps.dtype, ' ss: ', ss.dtype, ' te: ', te.dtype)
       
    return le, ps, ss, te

def Convert_FS_Standard(UP_points, DW_points):
    LE_points = []
    TE_points = []

    # Creates to spline and down spline
    dwn, u = splprep([DW_points[0], DW_points[1]], s=0)
    top, u = splprep([UP_points[0], UP_points[1]], s=0)

def AddAirfoil(Current_Airfoil, airfoils_list, default_loc):
    input_file = 'E474.txt'
    Current_Airfoil.full_curve, Current_Airfoil.top_curve, Current_Airfoil.dwn_curve, Current_Airfoil.name = DataBase_load(input_file, default_loc)
    Current_Airfoil.le_org, Current_Airfoil.ps_org, Current_Airfoil.ss_org, Current_Airfoil.te_org = Convert(0.08, 0.01, Current_Airfoil.top_curve, Current_Airfoil.dwn_curve)
    Current_Airfoil = EditAirfoil(Current_Airfoil, airfoils_list)
    return Current_Airfoil

def EditAirfoil(Current_Airfoil, airfoils_list):
    while True:
        
        print('Current size {} [mm]'.format(Current_Airfoil.scale))
        value = input("/Transform/Scale [mm] -> ")
        #value = 110
        
        try:
            Current_Airfoil.scale, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te = scale_airfoil(value, Current_Airfoil.le_org, Current_Airfoil.ps_org, Current_Airfoil.ss_org, Current_Airfoil.te_org, Current_Airfoil.scale)
            #Preview(False, [Current_Airfoil], airfoil_count)
        except ValueError:
            print('Must be a number (float)!')

        print('Current incidence {} [mm]'.format(Current_Airfoil.incidence))
        value = input("/Transform/Rotation ccw [deg] -> ")
        #value = -5

        try:
            Current_Airfoil.incidence, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te = rotate_airfoil(value, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te, Current_Airfoil.incidence)
            #Preview(False, [Current_Airfoil], airfoil_count)
        except ValueError:
            print('Must be a number (float)!')
        
        print('Current position {} [mm]'.format(Current_Airfoil.origin))
        value = input("/Transform/Move [insert values seperated by space x y ] -> ")
        #value = "-1500 100"
        value = value.split()
        origin = [float(num) for num in value]
        
        try:
            Current_Airfoil.origin, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te = move_airfoil(origin, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te, Current_Airfoil.origin)
            #Preview(True, airfoils_list, airfoil_count)
        except ValueError:
            print('Must be a number (float)!')    
            
        #satisfied = input("Are you satisfied with transformations? ")
        satisfied = "y"
        if satisfied.lower() in ['yes', 'y', 'true']:
            break
    return Current_Airfoil

def move_airfoil(move: list, tmp_le, tmp_ps, tmp_ss, tmp_te, origin):
    
    if not move:
        move = origin
    # move in X
    
    tmp_X_le = move[0] + tmp_le[0]
    tmp_X_ps = move[0] + tmp_ps[0]
    tmp_X_ss = move[0] + tmp_ss[0]
    tmp_X_te = move[0] + tmp_te[0]
    
    # move in Y
    tmp_Y_le = move[1] + tmp_le[1]
    tmp_Y_ps = move[1] + tmp_ps[1]
    tmp_Y_ss = move[1] + tmp_ss[1]
    tmp_Y_te = move[1] + tmp_te[1]
    
    tmp_le = np.vstack([tmp_X_le, tmp_Y_le])
    tmp_ss = np.vstack([tmp_X_ss, tmp_Y_ss])
    tmp_ps = np.vstack([tmp_X_ps, tmp_Y_ps])
    tmp_te = np.vstack([tmp_X_te, tmp_Y_te])
         
    return move, tmp_le, tmp_ps, tmp_ss, tmp_te

def scale_airfoil(scale: float, tmp_le: list, tmp_ps: list, tmp_ss: list, tmp_te: list, length):
    
    if scale == '':
        scale = length
        
    scale = float(scale)
    tmp_le = scale * np.array(tmp_le)
    tmp_ps = scale * np.array(tmp_ps)
    tmp_ss = scale * np.array(tmp_ss)
    tmp_te = scale * np.array(tmp_te)

    return scale, tmp_le, tmp_ps, tmp_ss, tmp_te

def rotate_airfoil(angle, tmp_le, tmp_ps, tmp_ss, tmp_te, incidence):
    if angle == '':
        angle = incidence
    theta = np.radians(float(angle))
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                            [np.sin(theta), np.cos(theta)]])

    tmp_le = np.dot(rotation_matrix, tmp_le)
    tmp_ps = np.dot(rotation_matrix, tmp_ps)
    tmp_ss = np.dot(rotation_matrix, tmp_ss)
    tmp_te = np.dot(rotation_matrix, tmp_te)
    
    
    return angle, tmp_le, tmp_ps, tmp_ss, tmp_te

def add_component_to_tree(tree_menu, name, component_obj):
    """Add an airfoil to the list and tree menu."""
    globals.PROJECT.project_components.append(component_obj)
    name = component_obj.infos.get('name', 'Unknown')
    modification_date = component_obj.infos.get('modification_date', 'Unknown')
    creation_date = component_obj.infos.get('creation_date', 'Unknown')
    tree_item = QTreeWidgetItem([str(name), str(modification_date), str(creation_date)])
    tree_menu.addTopLevelItem(tree_item)

def add_wing_to_tree(item, name, wing_obj, component_obj):
    """Add an airfoil to the list and tree menu."""     
    component_obj.wings.append(wing_obj)

def add_segment_to_tree(tree_menu, name, segment_obj, component_index, wing_index):
    """Add an airfoil to the list and tree menu."""
    globals.PROJECT.project_components[component_index].wings[wing_index].segments.append(segment_obj)

