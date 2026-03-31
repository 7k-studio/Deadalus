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
import sys
import math
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt

import numpy as np

import src.obj.objects3D
import src.obj.class_component
import src.obj.class_wing
import src.obj.class_segment

import src.wngdes.tools_wing as tools_wing
import src.utils.dxf as dxf
import random

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout, 
    QLabel, QMenuBar, QAction, QFileDialog, QTreeWidget, QTreeWidgetItem, QTextEdit, QStackedWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy, QDockWidget
)
from PyQt5.QtGui import QIcon

from src.opengl.viewport3d import Viewport3D
from OpenGL.GL import *  # Import OpenGL functions
from OpenGL.GLU import *  # Import GLU functions (e.g., gluPerspective)

from src.wngdes.menu_bar import MenuBar
from src.wngdes.widget_objects import TreeObject
from src.wngdes.widget_tabele import Tabele
from src.widgets.widget_log import LogViewer

#from designer.airfoil_designer import AirfoilDesigner  # Import AirfoilDesigner
#from wngwb import tools_wing  # Import add_component_to_tree
from datetime import date

class WingDesigner(QMainWindow):

    def __init__(self, program=None, project=None, flags=Qt.WindowFlags()):
        super(WingDesigner, self).__init__(None, flags)
        self.name = "Wing Designer"
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.DEADALUS = program
        self.PROJECT = project

        self._build_ui()
    
    def _build_ui(self):
        self.setWindowIcon(QIcon('src/assets/logo.png'))
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)

        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)
        content_layout = QVBoxLayout()

        self.setCentralWidget(central_widget)

        # Add the OpenGL viewport to the inner splitter
        self.VIEWPORT = QWidget()
        self.OPEN_GL = Viewport3D(program=self.DEADALUS, parent=self, project=self.PROJECT)
        viewport_layout = QVBoxLayout(self.VIEWPORT)
        viewport_layout.addWidget(self.OPEN_GL)
        #self.viewport.setMinimumWidth(500)

        # Create the menu bar
        self.MENU_BAR = MenuBar(self, viewport = self.OPEN_GL, parent=self)  # Use the MenuBar class
        self.setMenuBar(self.MENU_BAR)

        # Use the TreeMenu class directly
        self.TREE_OBJECT = TreeObject(self)
        self.TREE_OBJECT.setMinimumWidth(200)  # Nie pozwól schować całkowicie
        self.TREE_OBJECT.setMaximumWidth(200)

        left_layout = QHBoxLayout()
        left_layout.addWidget(self.TREE_OBJECT)

        # Add the Tabele module to the inner splitter
        self.TABELE_PARAMETERS = Tabele(self, tree_menu=self.TREE_OBJECT, open_gl=self.OPEN_GL, project=self.PROJECT)
        self.TABELE_PARAMETERS.setMinimumWidth(300)
        self.TABELE_PARAMETERS.setMaximumWidth(300)  # Opcjonalnie: ogranicz maksymalną szerokość
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.TABELE_PARAMETERS)

        #content_layout.addWidget(self.TREE_MENU)
        content_layout.addWidget(self.VIEWPORT, stretch=10)
        #content_layout.addWidget(self.TABELE_PARAMETERS)

        # Log Viewer Widget
        self.LOG_VIEWER = LogViewer(log_file="toolout.log", parent=self, program=self.DEADALUS)
        self.dock_logger = QDockWidget("Logger Console", self)
        self.dock_logger.setWidget(self.LOG_VIEWER)
        self.dock_logger.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_logger)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(right_layout)

        self.dock_logger.visibilityChanged.connect(self.update_menu_bar_state)

        self.dock_logger.visibilityChanged.connect(
            lambda visible: self.MENU_BAR.update_action_state(self.MENU_BAR.loggerWidgetAction, self.dock_logger)
        )

        if self.PROJECT and not self.PROJECT.components:
            # Initialize with a default airfoil
            self.addComponent()

        # Connect tree widget selection to display function
        self.TREE_OBJECT.itemClicked.connect(self.TABELE_PARAMETERS.display_selected_element)
        self.logger.info("Module: Wing Workbench initialized")

    def _update_header(self):
        self.setWindowTitle(f"{self.DEADALUS.name}: {self.name} - Untitled" if self.PROJECT.name is None else f"{self.DEADALUS.name}: {self.name} - {self.PROJECT.name}")

    def _populate_ui(self):
        self._update_header()

        # assign into both styleses if code expects either attribute
        self.OPEN_GL.PROJECT = self.OPEN_GL.project = self.PROJECT
        self.TREE_OBJECT.PROJECT = self.TREE_OBJECT.project = self.PROJECT
        self.TABELE_PARAMETERS.PROJECT = self.TABELE_PARAMETERS.project = self.PROJECT
        # self.TREE_REFERENCE.PROJECT = self.TREE_REFERENCE.project = self.PROJECT
        # self.TABLE_PARAMETERS.PROJECT = self.TABLE_PARAMETERS.project = self.PROJECT
        # self.TEXT_DESCRIPTION.PROJECT = self.TEXT_DESCRIPTION.project = self.PROJECT
        # self.TABLE_STATISTICS.PROJECT = self.TABLE_STATISTICS.project = self.PROJECT
        self.MENU_BAR.PROJECT = self.MENU_BAR.project = self.PROJECT

        if not self.PROJECT.components:
            # Initialize with a default component
            self.addComponent()

    def set_project(self, project):
        self.PROJECT = project
        self._populate_ui()
        self.refresh()

    def refresh(self):
        pass
    
    def addComponent(self):
        """Add a new component to the tree menu."""
        component_obj = src.obj.class_component.Component(self.DEADALUS, self.PROJECT)
        component_obj.name = f'Component {len(self.PROJECT.components)+1}'  # Ensure the name is set in infos
        component_obj.infos['creation_date'] = date.today().strftime("%Y-%m-%d")
        component_obj.infos['modification_date'] = date.today().strftime("%Y-%m-%d")
        self.TREE_OBJECT.add_component_to_tree(component_obj)
        self.OPEN_GL.update()

    def addWing(self):
        """Add a new wing to the selected component."""
        wing_obj = src.obj.class_wing.Wing(self.DEADALUS, self.PROJECT)
        wing_obj.infos['creation_date'] = date.today().strftime("%Y-%m-%d")
        wing_obj.infos['modification_date'] = date.today().strftime("%Y-%m-%d")

        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            # Find the index of the selected item
            index = self.TREE_OBJECT.indexOfTopLevelItem(selected_item)
            if index != -1:
                # Add the wing as a child of the selected component
                wing_name = f'Wing {selected_item.childCount()+1}'
                wing_obj.name = wing_name  # Ensure the name is set in infos
                wing_item = QTreeWidgetItem([wing_name])
                selected_item.addChild(wing_item)

                # Expand the parent item to show the new child
                selected_item.setExpanded(True)

                selected_component = self.PROJECT.components[index]
                self.TREE_OBJECT.add_wing_to_tree(selected_item, wing_name, wing_obj, selected_component)
                self.OPEN_GL.update()
                self.logger.info(f"Added '{wing_name}' as a part of '{selected_component.name}'.")
            else:
                self.logger.error("Cannot set wing to selected item!")
        else:
            self.logger.error("Component NOT selected!")

    def addSegment(self):
        """Add a new Segment to the selected wing."""
        
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            #Find parent item
            parent_item = selected_item.parent()
            if parent_item:
                # Find the index of the selected item
                wing_index = parent_item.indexOfChild(selected_item)
                component_index = self.TREE_OBJECT.indexOfTopLevelItem(parent_item)

                if wing_index != -1 and component_index != -1:
                    segment_name = f'Segment {selected_item.childCount()+1}'
                    segment_index = selected_item.childCount()
                    
                    segment_obj = src.obj.class_segment.Segment(self.DEADALUS, self.PROJECT)
                    segment_obj.airfoil = self.PROJECT.airfoils[0]  # Ensure the name is set in infos
                    segment_obj.name = segment_name  # Ensure the name is set in infos
                    segment_obj.infos['creation_date'] = date.today().strftime("%Y-%m-%d")
                    segment_obj.infos['modification_date'] = date.today().strftime("%Y-%m-%d")
                    
                    if selected_item.childCount() > 0:
                        segment_obj.params['origin_Z'] = self.PROJECT.components[component_index].wings[wing_index].segments[selected_item.childCount()-1].params['origin_Z']+0.2
                    
                    segment_item = QTreeWidgetItem([segment_name])
                    selected_item.addChild(segment_item)

                    # Expand the parent item to show the new child
                    selected_item.setExpanded(True)

                    self.TREE_OBJECT.add_segment_to_tree(self.TREE_OBJECT, segment_name, segment_obj, component_index, wing_index)
                    segment_obj.update(component_index, wing_index, segment_index)
                    if segment_index > 0:
                        wing_obj = self.PROJECT.components[component_index].wings[wing_index]
                        wing_obj.update(component_index, wing_index, segment_index)
                    self.OPEN_GL.update()
                else:
                    self.logger.error("Cannot set segment to selected item!")
            else:
                self.logger.error("Wing NOT selected!")
        else:
            self.logger.error("Component NOT found!")
    
    def deleteComponent(self):
        """Delete the selected component."""
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            index = self.TREE_OBJECT.indexOfTopLevelItem(selected_item)
            if index != -1:
                self.TREE_OBJECT.takeTopLevelItem(index)
                del self.PROJECT.components[index]
                self.logger.info(f"Deleted component at index {index}.")
                self.TREE_OBJECT.update()
                self.OPEN_GL.update()
            else:
                self.logger.error("Invalid selection.")
        else:
            self.logger.error("Component NOT selected!")

    def deleteWing(self):
        """Delete the selected wing."""
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            parent_item = selected_item.parent()
            if parent_item:
                wing_index = parent_item.indexOfChild(selected_item)
                component_index = self.TREE_OBJECT.indexOfTopLevelItem(parent_item)
                if wing_index != -1 and component_index != -1:
                    del self.PROJECT.components[component_index].wings[wing_index]
                    self.logger.info(f"Deleted wing at index {component_index}:{wing_index}.")
                    self.TREE_OBJECT.update()
                    self.OPEN_GL.update()
                else:
                    self.logger.error("Cannot delete selected wing!")
            else:
                self.logger.error("Wing NOT selected!")
        else:
            self.logger.error("Component NOT found!")

    def deleteSegment(self):
        """Delete the selected segment."""
        selected_item = self.TREE_OBJECT.currentItem()
        if selected_item:
            parent_item = selected_item.parent()
            if parent_item:
                grandparent_item = parent_item.parent()
                if grandparent_item:
                    segment_index = parent_item.indexOfChild(selected_item)
                    wing_index = grandparent_item.indexOfChild(parent_item)
                    component_index = self.TREE_OBJECT.indexOfTopLevelItem(grandparent_item)
                    del self.PROJECT.components[component_index].wings[wing_index].segments[segment_index]
                    self.logger.info(f"Deleted segment at index {component_index}:{wing_index}:{segment_index}.")
                    self.TREE_OBJECT.update()
                    self.OPEN_GL.update()
                else:
                    self.logger.error("Cannot delete selected segment!")
            else:
                self.logger.error("Segment NOT selected!")
        else:
            self.logger.error("Component NOT found!")
    
    def toggle_logger(self):
        """Toggle the logger widget."""
        if self.dock_logger.isVisible():
            self.dock_logger.close()  # Close the dock widget
        else:
            self.dock_logger.show()  # Show the dock widget
            
    def update_menu_bar_state(self, dock_widget):
        """Update the menu bar state when a dock widget's visibility changes."""
        # if dock_widget == self.dock_airfoil:
        #     self.MENU_BAR.update_action_state(self.MENU_BAR.airfoilWidgetAction, self.dock_airfoil)
        # elif dock_widget == self.dock_reference:
        #     self.MENU_BAR.update_action_state(self.MENU_BAR.referenceWidgetAction, self.dock_reference)
        # elif dock_widget == self.dock_parameters:
        #     self.MENU_BAR.update_action_state(self.MENU_BAR.parametersWidgetAction, self.dock_parameters)
        # elif dock_widget == self.dock_description:
        #     self.MENU_BAR.update_action_state(self.MENU_BAR.descriptionWidgetAction, self.dock_description)
        # elif dock_widget == self.dock_statistics:
        #     self.MENU_BAR.update_action_state(self.MENU_BAR.statisticsWidgetAction, self.dock_statistics)
        if dock_widget == self.dock_logger:
            self.MENU_BAR.update_action_state(self.MENU_BAR.loggerWidgetAction, self.dock_logger)

    def initializeOpenGL(self):
        """Initialize OpenGL settings."""
        glEnable(GL_DEPTH_TEST)  # Enable depth testing
        glClearColor(0.01, 0.01, 0.01, 1.0)  # Set background color

    def resizeGL(self, w, h):
        """Handle OpenGL viewport resizing."""
        if h == 0:
            h = 1  # Prevent division by zero
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 0.1, 50.0)  # Set perspective projection
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Add rendering logic here

