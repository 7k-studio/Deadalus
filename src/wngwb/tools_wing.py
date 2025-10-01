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
import src.obj.objects2D as objects2D
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

import datetime

logger = logging.getLogger(__name__)

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
    logger.info("Loading airfoil from database...")
    os.chdir('data')
    logger.debug(os.getcwd())
    try:
        with open(file) as file:
            for line in file:
                logger.debug(line)
                if line.startswith("Name:"):
                    airfoil_name = line.replace("Name:", '', 1)
                try:
                    x, y = map(float, line.split()) # split X and Y values into 
                    AirfoilCoord.append([x,y])
                except ValueError: # skip lines that dont contain numeric data
                    continue
    except FileNotFoundError:
        logger.error("No file found!")
        quit()
    os.chdir(default_loc)
            
    np.array(AirfoilCoord)
    logger.info("Chosen airfoils data read sucessfully!")
    logger.info("{} Coordinates".format(file))
    #logger.debug(AirfoilCoord)
    
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

    logger.info(f'Cieciwa aerodynamiczna: {airfoil_chord}')
    logger.info(f'Glebokosc krawedzi natarcia: {le_chord}')
    logger.info(f'Glebokosc krawedzi splywu: {te_chord}')

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
    
    logger.debug('le: ', le.dtype, ' ps: ', ps.dtype, ' ss: ', ss.dtype, ' te: ', te.dtype)
       
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
        
        logger.info('Current size {} [mm]'.format(Current_Airfoil.scale))
        value = input("/Transform/Scale [mm] -> ")
        #value = 110
        
        try:
            Current_Airfoil.scale, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te = scale_airfoil(value, Current_Airfoil.le_org, Current_Airfoil.ps_org, Current_Airfoil.ss_org, Current_Airfoil.te_org, Current_Airfoil.scale)
            #Preview(False, [Current_Airfoil], airfoil_count)
        except ValueError:
            logger.error('Must be a number (float)!')

        logger.info('Current incidence {} [mm]'.format(Current_Airfoil.incidence))
        value = input("/Transform/Rotation ccw [deg] -> ")
        #value = -5

        try:
            Current_Airfoil.incidence, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te = rotate_airfoil(value, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te, Current_Airfoil.incidence)
            #Preview(False, [Current_Airfoil], airfoil_count)
        except ValueError:
            logger.error('Must be a number (float)!')
        
        logger.info('Current position {} [mm]'.format(Current_Airfoil.origin))
        value = input("/Transform/Move [insert values seperated by space x y ] -> ")
        #value = "-1500 100"
        value = value.split()
        origin = [float(num) for num in value]
        
        try:
            Current_Airfoil.origin, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te = move_airfoil(origin, Current_Airfoil.le, Current_Airfoil.ps, Current_Airfoil.ss, Current_Airfoil.te, Current_Airfoil.origin)
            #Preview(True, airfoils_list, airfoil_count)
        except ValueError:
            logger.error('Must be a number (float)!')    
            
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

def add_component_to_tree(tree_menu, component_obj):
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

