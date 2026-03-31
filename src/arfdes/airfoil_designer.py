'''

Copyright (C) 2026 Jakub Kamyk

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
import os
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
    QTableWidget, QTableWidgetItem, QPushButton, QDockWidget,
    QWidget,
    QHBoxLayout, QVBoxLayout,
    QMenuBar, QAction, QFileDialog, 
    QLineEdit, QTextEdit,
    QTreeWidget, QTreeWidgetItem, 
    QApplication, QLabel, QInputDialog, QDialog, QDialogButtonBox,
    QStackedWidget, QMessageBox, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    )

from PyQt5.QtGui import QIcon

#Self imports
import src.obj as obj
import src.wngdes.tools_wing
import src.utils.dxf as dxf

from src.arfdes.menu_bar import MenuBar
from .tool_bar import ToolBar
from src.obj.class_airfoil import Airfoil
from src.arfdes.tools_airfoils import Reference_load
import src.arfdes.tools_airfoils as tools_airfoils

from src.arfdes.widget_airfoils import TreeAirfoil
from src.arfdes.widget_reference import TreeRererence
from src.arfdes.widget_parameters import TableParameters
from src.arfdes.widget_statistics import TableStatistics
from src.arfdes.widget_description import TextDescription
from src.widgets.widget_log import LogViewer
import src.arfdes.tools_airfoils as tools

from src.opengl.viewport2d import ViewportOpenGL


class AirfoilDesigner(QMainWindow):
    ''' Main window for the Airfoil Designer application. '''

    def __init__(self, program=None, project=None):
        super().__init__()
        self.name = "Airfoil Designer"
        self.time = date.today().strftime("%Y-%m-%d")
        self.logger = logging.getLogger(self.__class__.__name__)

        self.DEADALUS = program
        self.PROJECT = project

        self._build_ui()
    
    def _build_ui(self):

        self.setWindowIcon(QIcon('src/assets/logo.png'))
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)
        
        # Initial Parameters
        self.params = {}

        # Main splitter to hold the viewport and dockable widgets
        self.MAIN_SPLITTER = QSplitter(self)
        self.MAIN_SPLITTER.setOrientation(Qt.Horizontal)

        # Add the OpenGL viewport to the splitter
        self.VIEWPORT = QWidget()
        self.OPEN_GL = ViewportOpenGL(program=self.DEADALUS, project=self.PROJECT, parent=self.VIEWPORT)
        self.MAIN_SPLITTER.addWidget(self.OPEN_GL)

        # Create top toolbar and register it with the QMainWindow so it sits below the menu bar
        self.TOOL_BAR = ToolBar(program=self.DEADALUS, project=self.PROJECT, parent=self)

        # Add the toolbar to the main window top area (under the menu bar)
        self.addToolBar(Qt.TopToolBarArea, self.TOOL_BAR)

        # Create a central container that hosts only the main splitter (toolbars/docks are managed by QMainWindow)
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(self.MAIN_SPLITTER)
        self.setCentralWidget(central_widget)

        # central_widget = QWidget(self)
        # main_layout = QVBoxLayout(central_widget)  # Vertical layout for toolbar and content

        # Canvas and Table Layout
        # content_layout = QHBoxLayout()  # Horizontal layout for canvas and table/tree

        # Widgets for INPUT container
        # Left side tree airfoil
        self.TREE_AIRFOIL = TreeAirfoil(program=self.DEADALUS, project=self.PROJECT, parent=self)
        self.dock_airfoil = QDockWidget("Airfoil Tree", self)
        self.dock_airfoil.setWidget(self.TREE_AIRFOIL)
        self.dock_airfoil.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_airfoil)

        # Left side tree reference
        self.TREE_REFERENCE = TreeRererence(program=self.DEADALUS, project=self.PROJECT, parent=self)
        self.dock_reference = QDockWidget("Reference Tree", self)
        self.dock_reference.setWidget(self.TREE_REFERENCE)
        self.dock_reference.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_reference)

        # Left side parameters table
        self.TABLE_PARAMETERS = TableParameters(self, open_gl=self.OPEN_GL, airfoils_menu=self.TREE_AIRFOIL, project=self.PROJECT)
        self.dock_parameters = QDockWidget("Parameters Table", self)
        self.dock_parameters.setWidget(self.TABLE_PARAMETERS)
        self.dock_parameters.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_parameters)

        # Right side description textarea
        self.TEXT_DESCRIPTION = TextDescription(program=self.DEADALUS, project=self.PROJECT, parent=self)
        self.TEXT_DESCRIPTION.set_description("Please select an airfoil to see its description")
        self.dock_description = QDockWidget("Description TextArea", self)
        self.dock_description.setWidget(self.TEXT_DESCRIPTION)
        self.dock_description.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_description)

        # Right side statistics table
        self.TABLE_STATISTICS = TableStatistics(self, open_gl=self.OPEN_GL, airfoils_menu=self.TREE_AIRFOIL, project=self.PROJECT)
        self.dock_statistics = QDockWidget("Statistics Table", self)
        self.dock_statistics.setWidget(self.TABLE_STATISTICS)
        self.dock_statistics.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_statistics)

        # Refresh statistics table whenever parameters are changed in the parameters table
        self.TABLE_PARAMETERS.parametersChanged.connect(self.TABLE_STATISTICS.update)

        # Log Viewer Widget
        self.LOG_VIEWER = LogViewer(log_file="toolout.log", parent=self, program=self.DEADALUS)
        self.dock_logger = QDockWidget("Logger Console", self)
        self.dock_logger.setWidget(self.LOG_VIEWER)
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
        self.MENU_BAR = MenuBar(program=self.DEADALUS, project=self.PROJECT, parent=self, time=self.time)  # Use the MenuBar class
        self.setMenuBar(self.MENU_BAR)

        # Connect visibilityChanged signals to the menu bar's update_action_state method
        self.dock_airfoil.visibilityChanged.connect(
            lambda visible: self.MENU_BAR.update_action_state(self.MENU_BAR.airfoilWidgetAction, self.dock_airfoil)
        )
        self.dock_reference.visibilityChanged.connect(
            lambda visible: self.MENU_BAR.update_action_state(self.MENU_BAR.referenceWidgetAction, self.dock_reference)
        )
        self.dock_parameters.visibilityChanged.connect(
            lambda visible: self.MENU_BAR.update_action_state(self.MENU_BAR.parametersWidgetAction, self.dock_parameters)
        )
        self.dock_description.visibilityChanged.connect(
            lambda visible: self.MENU_BAR.update_action_state(self.MENU_BAR.descriptionWidgetAction, self.dock_description)
        )
        self.dock_statistics.visibilityChanged.connect(
            lambda visible: self.MENU_BAR.update_action_state(self.MENU_BAR.statisticsWidgetAction, self.dock_statistics)
        )
        self.dock_logger.visibilityChanged.connect(
            lambda visible: self.MENU_BAR.update_action_state(self.MENU_BAR.loggerWidgetAction, self.dock_logger)
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
        self.MENU_BAR.referenceStatus.connect(self.handleReferenceToggle)
        self.TREE_AIRFOIL.itemClicked.connect(self.TABLE_PARAMETERS.display_selected_airfoil)
        self.TREE_AIRFOIL.itemClicked.connect(self.TABLE_STATISTICS.display_selected_airfoil)
        self.TREE_AIRFOIL.itemClicked.connect(self.TEXT_DESCRIPTION.display_selected_airfoil)

        if self.PROJECT and not self.PROJECT.airfoils:
            # Initialize with a default airfoil
            self.TREE_AIRFOIL.add("Airfoil", self.time, "New projects: Initialized because of no other airfoil was available")
        self.logger.info("Initialization completed")
    
    def _update_header(self):
        self.setWindowTitle(f"{self.DEADALUS.name}: {self.name} - Untitled" if self.PROJECT.name is None else f"{self.DEADALUS.name}: {self.name} - {self.PROJECT.name}")

    def _populate_ui(self):
        self._update_header()

        # assign into both styleses if code expects either attribute
        self.OPEN_GL.PROJECT = self.OPEN_GL.project = self.PROJECT
        self.TOOL_BAR.PROJECT = self.TOOL_BAR.project = self.PROJECT
        self.TREE_AIRFOIL.PROJECT = self.TREE_AIRFOIL.project = self.PROJECT
        self.TREE_REFERENCE.PROJECT = self.TREE_REFERENCE.project = self.PROJECT
        self.TABLE_PARAMETERS.PROJECT = self.TABLE_PARAMETERS.project = self.PROJECT
        self.TEXT_DESCRIPTION.PROJECT = self.TEXT_DESCRIPTION.project = self.PROJECT
        self.TABLE_STATISTICS.PROJECT = self.TABLE_STATISTICS.project = self.PROJECT
        self.MENU_BAR.PROJECT = self.MENU_BAR.project = self.PROJECT

        if not self.PROJECT.airfoils:
            # Initialize with a default airfoil
            self.TREE_AIRFOIL.add("Airfoil", self.time, "New projects: Initialized because of no other airfoil was available")

    def set_project(self, project):
        self.PROJECT = project
        self._populate_ui()
        self.refresh()

    def refresh(self):
        self.TREE_AIRFOIL.update()
        self.TREE_REFERENCE.update()
        self.TABLE_PARAMETERS.update()
        self.TABLE_STATISTICS.update()
        self.TEXT_DESCRIPTION.clear()
        self.OPEN_GL.clear()

    def handleReferenceToggle(self, state, filename):
        selected_item = self.TREE_AIRFOIL.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.TREE_AIRFOIL.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        if state:
            reference_airfoil = Reference_load(filename)
            if reference_airfoil != None:
                self.logger.info(f"Reference enabled with file: '{filename}'")
                self.OPEN_GL.set_reference_to_display(reference_airfoil)
            else:
                self.logger.error('Failed to load refrence!')

            #self.table.set_reference_points(self.reference_airfoil.top_curve, self.reference_airfoil.dwn_curve)  # Pass reference points to the table

        else:
            self.logger.info("Reference disabled")
            #self.table.set_reference_points(None, None)  # Clear reference points in the table
            self.OPEN_GL.set_reference_to_display(None)
    
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
            self.MENU_BAR.update_action_state(self.MENU_BAR.airfoilWidgetAction, self.dock_airfoil)
        elif dock_widget == self.dock_reference:
            self.MENU_BAR.update_action_state(self.MENU_BAR.referenceWidgetAction, self.dock_reference)
        elif dock_widget == self.dock_parameters:
            self.MENU_BAR.update_action_state(self.MENU_BAR.parametersWidgetAction, self.dock_parameters)
        elif dock_widget == self.dock_description:
            self.MENU_BAR.update_action_state(self.MENU_BAR.descriptionWidgetAction, self.dock_description)
        elif dock_widget == self.dock_statistics:
            self.MENU_BAR.update_action_state(self.MENU_BAR.statisticsWidgetAction, self.dock_statistics)
        elif dock_widget == self.dock_logger:
            self.MENU_BAR.update_action_state(self.MENU_BAR.loggerWidgetAction, self.dock_logger)
    
    def newAirfoil(self):
        self.logger.info("Creating new airfoil")
        self.TREE_AIRFOIL.add('Airfoil', self.time, 'Airfoil created from scratch')

    def appendAirfoil(self):
        """load the airfoil data from a JSON format file."""
        self.logger.info("Appending airfoil...")
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Deadalus Airfoil Format (*.arf);;All Files (*)", options=options)

        if fileName:
            # try:
            airfoil_obj = tools_airfoils.load_airfoil_from_json(fileName, self.DEADALUS.version)                
            self.PROJECT._ensure_unique_name(airfoil_obj)  # Ensure unique name             
            self.PROJECT.project_airfoils.append(airfoil_obj)
            if airfoil_obj:
                self.logger.debug(airfoil_obj)
                self.TREE_AIRFOIL.add_airfoil_to_tree(airfoil_obj, airfoil_obj.name)
                self.logger.info("Appending an airfoil was sucessful!")
            # except TypeError:
            #     self.logger.error("Failed to append airfoil")

    def deleteAirfoil(self):
        self.logger.info("Deleting selected airfoil...")
        if self.TREE_AIRFOIL:  # Ensure main_window is set
            status, name = self.TREE_AIRFOIL.delete()
            if status == True and name:
                self.logger.info(f"Successfully deleted airfoil: {name}")
                self.refresh()
            else:
                self.logger.error("Failed to delete!")
            
    def saveAirfoil(self):
        """Save the airfoil data to a JSON format file."""
        self.logger.info("Saving selected airfoil...")
        airfoil = self.TREE_AIRFOIL.selected_airfoil
        if not airfoil:
            self.logger.error("No valid airfoil selected!")

        options = QFileDialog.Options()
        default_name = f"{airfoil.name}.arf" if airfoil.name else f"Untitled.arf"
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", default_name, "DEADALUS Airfoil Format (*.arf);;All Files (*)", options=options)
        if filePath:
            airfoil.name = os.path.basename(filePath).split('.')[0]
            airfoil.path = filePath
            
            json_object = tools_airfoils.save_airfoil_to_json(airfoil, self.PROJECT, self.DEADALUS)
        
            with open(f"{filePath}", "w") as outfile:
                outfile.write(json_object)
                self.logger.info(f"Saved file: {filePath}")

            self.PROJECT._ensure_unique_name(airfoil)  # Ensure unique name
            self.refresh()
 
    def exportAirfoil(self):
        """Export the airfoil data to a DXF format file."""
        self.logger.info("Exporting selected airfoil...")

        airfoil = self.TREE_AIRFOIL.selected_airfoil
        if not airfoil:
            self.logger.error("No valid airfoil selected!")
        
        options = QFileDialog.Options()
        default_name = f"{airfoil.name}.dxf" if airfoil.name else "Untitled.dxf"
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File to DXF format", default_name, "DXF Format (*.dxf);;All Files (*)", options=options)
        if fileName:
            dxf.export_airfoil_to_dxf(airfoil, fileName)
            self.logger.info(f"Exported file: {fileName}")
    
    def renameAirfoil(self):
        """Rename currently selected airfoil."""
        self.logger.info("Renaming selected airfoil...")
        self.le = QLabel(self)
        
        try:
            selected_airfoil = self.TREE_AIRFOIL.selected_airfoil

            text, ok = QInputDialog.getText(self, 'Change Airfoils Name', 'Enter airfoil\'s new name:', text=selected_airfoil.info["name"])
            if ok:
                self.le.setText(str(text))
            if text:
                selected_airfoil.info['name'] = text
                selected_airfoil.name = text  # Sync name
                self.PROJECT._ensure_unique_name(selected_airfoil)  # Ensure unique name
                selected_airfoil.info['name'] = selected_airfoil.name  # Sync back
                selected_airfoil.info['modification_date'] = date.today().strftime("%Y-%m-%d")
                
            # Optionally, update the tree menu display
            self.refresh()
            self.logger.info("Airfoil renamed")
        
        except AttributeError:
            self.logger.error("No valid airfoil selected!")
    
    def flipAirfoil(self):
        """Flip the currently selected airfoil."""

        airfoil_idx = self.TREE_AIRFOIL.selected_airfoil_index

        current_airfoil = self.PROJECT.project_airfoils[airfoil_idx]

        flipped_airfoil = tools_airfoils.flip_airfoil_horizontally(current_airfoil)

        if flipped_airfoil:
            self.PROJECT.project_airfoils[airfoil_idx] = flipped_airfoil
            self.logger.info(f"Airfoil '{flipped_airfoil.name}' flipped...")
            self.OPEN_GL.set_airfoil_to_display(self.PROJECT.project_airfoils[airfoil_idx])
            self.OPEN_GL.update()
            self.TABLE_PARAMETERS.update()
            self.TABLE_STATISTICS.update()
        else:
            self.logger.error("Something went wrong, airfoil not flipped!")

    def editDescriptionAirfoil(self):
        """Edit the description of an airfoil from the presentation widget."""
        self.logger.info("Editing selected airfoil description...")

        # Ensure the description widget has the selected airfoil loaded
        self.TEXT_DESCRIPTION.display_selected_airfoil()

        # Open the same edit dialog used by the description panel
        self.TEXT_DESCRIPTION.edit_dialog()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = AirfoilDesigner()
    viewer.show()
    sys.exit(app.exec_())
