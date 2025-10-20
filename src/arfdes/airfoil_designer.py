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

#Self imports
import src.obj as obj
import src.wngwb.tools_wing
import src.utils.dxf

from .menu_bar import MenuBar
from src.obj.class_airfoil import Airfoil
from src.arfdes.tools_airfoils import Reference_load

import src.globals as globals
from src.arfdes.widget_airfoils import TreeAirfoil
from src.arfdes.widget_reference import TreeRererence
from src.arfdes.widget_parameters import TableParameters
from src.arfdes.widget_statistics import TableStatistics
from src.opengl.widget_console import LogViewer
import src.arfdes.tools_airfoils as tools

from src.opengl.viewport2d import ViewportOpenGL

Airfoil_0 = src.obj.objects2D.Airfoil()


class AirfoilDesigner(QMainWindow):

    ''' Main window for the Airfoil Designer application. '''

    def __init__(self, program=None, project=None):
        super().__init__()
        self.program = program
        self.project = project
        self.time = date.today().strftime("%Y-%m-%d")
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
        input_container_layout = QVBoxLayout()  # Vertical layout for tree and table
        output_container_layout = QVBoxLayout()

        # Widgets for input container
        self.airfoil_tree = TreeAirfoil()
        self.reference_tree = TreeRererence(self)
        self.parameters = TableParameters(self, open_gl=self.open_gl, airfoils_menu=self.airfoil_tree, project=self.project)

        # Create the menu bar
        self.menu_bar = MenuBar(self, project=self.project, parent=self, time=self.time, airfoils_menu=self.airfoil_tree)  # Use the MenuBar class
        self.setMenuBar(self.menu_bar)

        # Add all INPUT widgets to container
        input_container_layout.addWidget(self.airfoil_tree)
        input_container_layout.addWidget(self.parameters)
        
        # Widgets for output container
        self.statistics = TableStatistics(self)

        # Log Viewer Widget
        self.log_viewer = LogViewer(log_file="toolout.log", parent=self)

        # Add all OUTPUT widgets to container
        output_container_layout.addWidget(self.reference_tree)
        output_container_layout.addWidget(self.statistics)

        # Canvas and Log Viewer Layout
        middle_container_layout = QVBoxLayout()  # Vertical layout for OpenGL viewport and log viewer
        middle_container_layout.addWidget(self.open_gl, 4)  # OpenGL viewport
        middle_container_layout.addWidget(self.log_viewer, 1)  # Log viewer below OpenGL viewport

        # Add layouts to the horizontal layout
        content_layout.addLayout(input_container_layout)
        content_layout.addLayout(middle_container_layout, 2)  # Middle container with OpenGL and log viewer
        content_layout.addLayout(output_container_layout)

        # Add toolbar and content layout to the main layout
        main_layout.addLayout(content_layout)

        self.setCentralWidget(central_widget)

        # Connect tree widget selection to display function
        self.menu_bar.referenceStatus.connect(self.handleReferenceToggle)
        self.airfoil_tree.itemClicked.connect(self.parameters.display_selected_airfoil)

        if not globals.PROJECT.project_airfoils:
            # Initialize with a default airfoil
            self.airfoil_tree.new("Airfoil", self.time, "New projects: Initialized because of no other airfoil was available")
        self.logger.info("Initialization completed")

    def handleReferenceToggle(self, state, filename):
        selected_item = self.airfoil_tree.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.airfoil_tree.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        #current_airfoil = globals.PROJECT.project_airfoils[airfoil_index]

        if state:
            self.logger.info(f"Reference enabled with file: '{filename}'")
            reference_airfoil = Reference_load(filename)
            self.open_gl.set_reference_to_display(reference_airfoil)

            #self.table.set_reference_points(self.reference_airfoil.top_curve, self.reference_airfoil.dwn_curve)  # Pass reference points to the table

        else:
            self.logger.info("Reference disabled")
            #self.table.set_reference_points(None, None)  # Clear reference points in the table
            self.open_gl.set_reference_to_display(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = AirfoilDesigner()
    viewer.show()
    sys.exit(app.exec_())
