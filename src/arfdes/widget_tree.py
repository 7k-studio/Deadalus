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

def add_airfoil_to_tree(tree_menu=None, name="Unknown", airfoil_obj=None):
    """Add an airfoil to the list and tree menu."""
    modification_date = airfoil_obj.infos.get('modification_date', 'Unknown')
    creation_date = airfoil_obj.infos.get('creation_date', 'Unknown')
    description = airfoil_obj.infos.get('description', 'No description')
    tree_item = QTreeWidgetItem([name, str(modification_date), str(creation_date), description])
    tree_menu.addTopLevelItem(tree_item)
    print(f"ARFDES > Airfoil '{name}' added to the tree")

def refresh_tree(tree_menu=None):
    tree_menu.clear()  # Clear existing items
    for airfoil in globals.PROJECT.project_airfoils:
        add_airfoil_to_tree(tree_menu, airfoil.infos['name'], airfoil)
    print("ARFDES > tree is refreshed")