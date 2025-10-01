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

#System imports
import sys
from datetime import date
import logging

#PyQt5 imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QVBoxLayout, 
    QWidget, QHBoxLayout, QLineEdit, QFormLayout, QLabel, 
    QMenuBar, QAction, QFileDialog, QTreeWidget, 
    QTreeWidgetItem, QTextEdit, QStackedWidget, QHeaderView,
    QTableWidget, QTableWidgetItem, QPushButton
)
from PyQt5.QtGui import QIcon

#MatPlotLib imports
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backend_bases import FigureCanvasBase
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle

#Math/Physics imports
import numpy as np
import math
from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d
from scipy.optimize import minimize, root_scalar
from scipy import interpolate

#Self imports
import src.obj as obj
import src.wngwb.tools_wing
import src.utils.dxf
from src.arfdes.widget_tabele import Tabele
from .menu_bar import MenuBar
from src.obj.objects2D import Airfoil
from src.arfdes.tools_airfoil import Reference_load
from src.arfdes.tools_airfoil import CreateBSpline
from src.arfdes.widget_tree import add_airfoil_to_tree
import src.globals as globals

from src.opengl.viewport2d import ViewportOpenGL

Airfoil_0 = src.obj.objects2D.Airfoil()

class AirfoilDesigner(QMainWindow):

    ''' Main window for the Airfoil Designer application. '''

    def __init__(self, program=None, project=None):
        super().__init__()
        
        self.program = program
        self.project = project
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("DEADALUS: Airfoil Designer")
        self.setWindowIcon(QIcon('src/assets/logo.png'))
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)
        
        # Initial Parameters
        self.params = {}

        # Main layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)  # Vertical layout for toolbar and content

        # Canvas and Table Layout
        content_layout = QHBoxLayout()  # Horizontal layout for canvas and table/tree

        # Add the OpenGL viewport to the inner splitter
        self.viewport = QWidget()
        self.open_gl = ViewportOpenGL(parent=self.viewport)

        # Tree and Table Layout
        tree_table_layout = QVBoxLayout()  # Vertical layout for tree and table

        # Tree Menu
        self.tree_menu = QTreeWidget()
        self.tree_menu.setHeaderLabel("Project airfoils")
        self.tree_menu.setMinimumHeight(100)  # Set minimum height for the tree menu
        tree_table_layout.addWidget(self.tree_menu)

        # Add tabele
        self.table = Tabele(self, open_gl=self.open_gl, tree_menu=self.tree_menu, project=self.project)
        self.update_tree_menu()

        # Create the menu bar
        self.menu_bar = MenuBar(self, project=self.project, parent=self, tree_menu=self.tree_menu)  # Use the MenuBar class
        self.setMenuBar(self.menu_bar)

        # Add canvas to the horizontal layout
        #content_layout.addWidget(self.canvas, 2)
        content_layout.addWidget(self.open_gl, 2)

        # Add table to the vertical layout
        tree_table_layout.addWidget(self.table)

        # Add tree and table layout to the horizontal layout
        content_layout.addLayout(tree_table_layout, 1)

        # Add toolbar and content layout to the main layout
        main_layout.addLayout(content_layout)

        self.setCentralWidget(central_widget)

        # Connect tree widget selection to display function
        self.menu_bar.referenceStatus.connect(self.handleReferenceToggle)
        self.tree_menu.itemClicked.connect(self.table.display_selected_airfoil)

        if not globals.PROJECT.project_airfoils:
            # Initialize with a default airfoil
            self.add_airfoil( "Airfoil", "New projects: Initialized because of no other airfoil was available")
        
        self.logger.info("Module: Airfoil Designer has been initialized")

    def add_airfoil(self, name, dscr='designed from scratch in airfoil designer'):
        airfoil_obj = src.obj.objects2D.Airfoil()
        airfoil_obj.infos['name'] = name  # Ensure the name is set in infos
        airfoil_obj.infos['creation_date'] = date.today().strftime("%Y-%m-%d")
        airfoil_obj.infos['modification_date'] = date.today().strftime("%Y-%m-%d")
        airfoil_obj.infos['description'] = dscr
        globals.PROJECT.project_airfoils.append(airfoil_obj)
        add_airfoil_to_tree(self.tree_menu, name, airfoil_obj)

    def handleReferenceToggle(self, state, filename):
        selected_item = self.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        #current_airfoil = globals.PROJECT.project_airfoils[airfoil_index]

        if state:
            self.logger.info(f"Reference enabled with file: '{filename}'")
            #self.canvas.ax.clear()  # Clear the plot
            reference_airfoil = Reference_load(filename)
            self.open_gl.set_reference_to_display(reference_airfoil)
            #self.canvas.plot_airfoil(current_airfoil)
            
            #self.table.set_reference_points(self.reference_airfoil.top_curve, self.reference_airfoil.dwn_curve)  # Pass reference points to the table
            #self.canvas.plot_reference(self.reference_airfoil.top_curve, self.reference_airfoil.dwn_curve)
        else:
            self.logger.info("Reference disabled")
            #self.canvas.ax.clear()  # Clear the plot
            #self.table.set_reference_points(None, None)  # Clear reference points in the table
            #self.canvas.plot_airfoil(current_airfoil)  # Re-plot the airfoil
            self.open_gl.set_reference_to_display(None)

    def update_tree_menu(self):
        """Update the tree menu based on the current self.project.project_airfoils."""
        self.tree_menu.clear()  # Clear existing items

        # Set up tree columns
        self.tree_menu.setColumnCount(4)  # Adjust the number of columns
        self.tree_menu.setHeaderLabels(["Name", "Last modification", "Creation Date", "Description"])  # Set column headers

        for airfoil in globals.PROJECT.project_airfoils:
            # Assuming airfoil_list contains objects with 'infos' dictionary
            name = airfoil.infos.get('name', 'Unknown')
            modification_date = airfoil.infos.get('modification_date', 'Unknown')
            creation_date = airfoil.infos.get('creation_date', 'Unknown')
            description = airfoil.infos.get('description', 'No description')

            # Create a tree item with multiple columns
            tree_item = QTreeWidgetItem([name, str(modification_date), str(creation_date), description])
            self.tree_menu.addTopLevelItem(tree_item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = AirfoilDesigner()
    viewer.show()
    sys.exit(app.exec_())
