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
    QTableWidget, QTableWidgetItem, QPushButton, QDockWidget
)
from PyQt5.QtGui import QIcon

#Self imports
import src.obj as obj
import src.wngwb.tools_wing
import src.utils.dxf

from .menu_bar import MenuBar
from .tool_bar import ToolBar
from src.obj.class_airfoil import Airfoil
from src.arfdes.tools_airfoils import Reference_load

import src.globals as globals
from src.arfdes.widget_airfoils import TreeAirfoil
from src.arfdes.widget_reference import TreeRererence
from src.arfdes.widget_parameters import TableParameters
from src.arfdes.widget_statistics import TableStatistics
from src.arfdes.widget_description import TextDescription
from src.opengl.widget_console import LogViewer
import src.arfdes.tools_airfoils as tools

from src.opengl.viewport2d import ViewportOpenGL

Airfoil_0 = obj.class_airfoil.Airfoil()


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

        # Main splitter to hold the viewport and dockable widgets
        self.main_splitter = QSplitter(self)
        self.main_splitter.setOrientation(Qt.Horizontal)

        # Add the OpenGL viewport to the splitter
        self.viewport = QWidget()
        self.open_gl = ViewportOpenGL(parent=self.viewport)
        self.main_splitter.addWidget(self.open_gl)

        # Create top toolbar and register it with the QMainWindow so it sits below the menu bar
        self.toolbar = ToolBar(self)

        # Add the toolbar to the main window top area (under the menu bar)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Create a central container that hosts only the main splitter (toolbars/docks are managed by QMainWindow)
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.main_splitter)
        self.setCentralWidget(central_widget)

        # central_widget = QWidget(self)
        # main_layout = QVBoxLayout(central_widget)  # Vertical layout for toolbar and content

        # Canvas and Table Layout
        # content_layout = QHBoxLayout()  # Horizontal layout for canvas and table/tree

        # Widgets for INPUT container
        # Left side tree airfoil
        self.tree_airfoil = TreeAirfoil(open_gl=self.open_gl)
        self.dock_airfoil = QDockWidget("Airfoil Tree", self)
        self.dock_airfoil.setWidget(self.tree_airfoil)
        self.dock_airfoil.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_airfoil)

        # Left side tree reference
        self.tree_reference = TreeRererence(self)
        self.dock_reference = QDockWidget("Reference Tree", self)
        self.dock_reference.setWidget(self.tree_reference)
        self.dock_reference.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_reference)

        # Left side parameters table
        self.table_parameters = TableParameters(self, open_gl=self.open_gl, airfoils_menu=self.tree_airfoil, project=self.project)
        self.dock_parameters = QDockWidget("Parameters Table", self)
        self.dock_parameters.setWidget(self.table_parameters)
        self.dock_parameters.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_parameters)

        # Right side description textarea
        self.text_description = TextDescription(self)
        self.text_description.set_description("Default description")
        self.dock_description = QDockWidget("Description TextArea", self)
        self.dock_description.setWidget(self.text_description)
        self.dock_description.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_description)

        # Right side statistics table
        self.table_statistics = TableStatistics(self, open_gl=self.open_gl, airfoils_menu=self.tree_airfoil, project=self.project)
        self.dock_statistics = QDockWidget("Statistics Table", self)
        self.dock_statistics.setWidget(self.table_statistics)
        self.dock_statistics.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_statistics)

        # Log Viewer Widget
        self.log_viewer = LogViewer(log_file="toolout.log", parent=self)
        self.dock_logger = QDockWidget("Logger Console", self)
        self.dock_logger.setWidget(self.log_viewer)
        self.dock_logger.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_logger)

        # Connect the visibilityChanged signal to update the menu bar state
        self.dock_airfoil.visibilityChanged.connect(self.update_menu_bar_state)
        self.dock_reference.visibilityChanged.connect(self.update_menu_bar_state)
        self.dock_parameters.visibilityChanged.connect(self.update_menu_bar_state)
        self.dock_description.visibilityChanged.connect(self.update_menu_bar_state)
        self.dock_statistics.visibilityChanged.connect(self.update_menu_bar_state)
        self.dock_logger.visibilityChanged.connect(self.update_menu_bar_state)

        # Create the menu bar
        self.menu_bar = MenuBar(self, project=self.project, parent=self, time=self.time, airfoils_menu=self.tree_airfoil)  # Use the MenuBar class
        self.setMenuBar(self.menu_bar)

        # Connect visibilityChanged signals to the menu bar's update_action_state method
        self.dock_airfoil.visibilityChanged.connect(
            lambda visible: self.menu_bar.update_action_state(self.menu_bar.airfoilWidgetAction, self.dock_airfoil)
        )
        self.dock_reference.visibilityChanged.connect(
            lambda visible: self.menu_bar.update_action_state(self.menu_bar.referenceWidgetAction, self.dock_reference)
        )
        self.dock_parameters.visibilityChanged.connect(
            lambda visible: self.menu_bar.update_action_state(self.menu_bar.parametersWidgetAction, self.dock_parameters)
        )
        self.dock_description.visibilityChanged.connect(
            lambda visible: self.menu_bar.update_action_state(self.menu_bar.descriptionWidgetAction, self.dock_description)
        )
        self.dock_statistics.visibilityChanged.connect(
            lambda visible: self.menu_bar.update_action_state(self.menu_bar.statisticsWidgetAction, self.dock_statistics)
        )
        self.dock_logger.visibilityChanged.connect(
            lambda visible: self.menu_bar.update_action_state(self.menu_bar.loggerWidgetAction, self.dock_logger)
        )

        # Canvas and Log Viewer Layout
        # middle_container_layout = QVBoxLayout()  # Vertical layout for OpenGL viewport and log viewer
        # middle_container_layout.addWidget(self.open_gl, 4)  # OpenGL viewport
        # middle_container_layout.addWidget(self.log_viewer, 1)  # Log viewer below OpenGL viewport

        # # Add layouts to the horizontal layout
        # content_layout.addLayout(middle_container_layout, 2)  # Middle container with OpenGL and log viewer

        # # Add toolbar and content layout to the main layout
        # main_layout.addLayout(content_layout)

        # Connect tree widget selection to display function
        self.menu_bar.referenceStatus.connect(self.handleReferenceToggle)
        self.tree_airfoil.itemClicked.connect(self.table_parameters.display_selected_airfoil)
        self.tree_airfoil.itemClicked.connect(self.table_statistics.display_selected_airfoil)

        if not globals.PROJECT.project_airfoils:
            # Initialize with a default airfoil
            self.tree_airfoil.add("Airfoil", self.time, "New projects: Initialized because of no other airfoil was available")
        self.logger.info("Initialization completed")

    def handleReferenceToggle(self, state, filename):
        selected_item = self.tree_airfoil.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.tree_airfoil.indexOfTopLevelItem(selected_item)
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
    
    def toggle_airfoil(self):
        """Toggle the airfoil widget."""
        if self.dock_airfoil.isVisible():
            self.dock_airfoil.close()  # Close the dock widget
        else:
            self.dock_airfoil.show()  # Show the dock widget

    def toggle_parameters(self):
        """Toggle the parameters widget."""
        if self.dock_parameters.isVisible():
            self.dock_parameters.close()  # Close the dock widget
        else:
            self.dock_parameters.show()  # Show the dock widget

    def toggle_reference(self):
        """Toggle the reference widget."""
        if self.dock_reference.isVisible():
            self.dock_reference.close()  # Close the dock widget
        else:
            self.dock_reference.show()  # Show the dock widget

    def toggle_statistics(self):
        """Toggle the statistics widget."""
        if self.dock_statistics.isVisible():
            self.dock_statistics.close()  # Close the dock widget
        else:
            self.dock_statistics.show()  # Show the dock widget
    
    def toggle_description(self):
        """Toggle the description widget."""
        if self.dock_description.isVisible():
            self.dock_description.close()  # Close the dock widget
        else:
            self.dock_description.show()  # Show the dock widget

    def toggle_logger(self):
        """Toggle the logger widget."""
        if self.dock_logger.isVisible():
            self.dock_logger.close()  # Close the dock widget
        else:
            self.dock_logger.show()  # Show the dock widget

    def update_menu_bar_state(self, dock_widget):
        """Update the menu bar state when a dock widget's visibility changes."""
        if dock_widget == self.dock_airfoil:
            self.menu_bar.update_action_state(self.menu_bar.airfoilWidgetAction, self.dock_airfoil)
        elif dock_widget == self.dock_reference:
            self.menu_bar.update_action_state(self.menu_bar.referenceWidgetAction, self.dock_reference)
        elif dock_widget == self.dock_parameters:
            self.menu_bar.update_action_state(self.menu_bar.parametersWidgetAction, self.dock_parameters)
        elif dock_widget == self.dock_description:
            self.menu_bar.update_action_state(self.menu_bar.descriptionWidgetAction, self.dock_description)
        elif dock_widget == self.dock_statistics:
            self.menu_bar.update_action_state(self.menu_bar.statisticsWidgetAction, self.dock_statistics)
        elif dock_widget == self.dock_logger:
            self.menu_bar.update_action_state(self.menu_bar.loggerWidgetAction, self.dock_logger)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = AirfoilDesigner()
    viewer.show()
    sys.exit(app.exec_())
