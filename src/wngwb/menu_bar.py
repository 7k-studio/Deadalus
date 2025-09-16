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

from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QApplication
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout, QLabel, QMenuBar, QAction, QFileDialog, QTreeWidget, QTreeWidgetItem, QTextEdit, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt
import numpy as np
import math
import os
from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d
from scipy.optimize import minimize, root_scalar
from scipy import interpolate
import random
from tqdm import tqdm
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QPushButton
)

import src.obj.objects3D
from OpenGL.GL import *  # Import OpenGL functions
from OpenGL.GLU import *  # Import GLU functions (e.g., gluPerspective)
from src.arfdes.airfoil_designer import AirfoilDesigner
import src.globals as globals

from src.wngwb import tools_wing  # Import add_component_to_tree
from src.wngwb import widget_tree

from datetime import date
import src.obj

class MenuBar(QMenuBar):
    def __init__(self, parent=None, viewport=None):
        super(MenuBar, self).__init__(parent)
        self.main_window = parent
        self.open_gl = viewport
        self.createMenu()

    def createMenu(self):
        fileMenu = self.addMenu('File')
        
        newAction    = QAction('New', self)
        openAction   = QAction('Open', self)
        saveAction   = QAction('Save', self)
        exportAction = QAction('Export', self)
        exitAction   = QAction('Exit', self)

        newAction.triggered.connect(self.newFile)
        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        exportAction.triggered.connect(self.exportFile)
        exitAction.triggered.connect(self.quitApp)

        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exportAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        editMenu = self.addMenu('Edit')

        addComponentAction    = QAction('Add Component', self)
        appendComponentAction = QAction('Append Component', self)
        copyComponentAction   = QAction('Copy Component', self)
        renameComponentAction = QAction('Rename Component', self)
        deleteComponentAction = QAction('Delete Component', self)
        addWingAction         = QAction('Add Wing', self)
        appendWingAction      = QAction('Append Wing', self)
        copyWingAction        = QAction('Copy Wing', self)
        renameWingAction      = QAction('Rename Wing', self)
        deleteWingAction      = QAction('Delete Wing', self)
        addSegmentAction      = QAction('Add Segment', self)
        appendSegmentAction   = QAction('Append Segment', self)
        copySegmentAction     = QAction('Copy Segment', self)
        renameSegmentAction   = QAction('Rename Segment', self)
        deleteSegmentAction   = QAction('Delete Segment', self)

        addComponentAction.triggered.connect(self.addComponent)
        deleteComponentAction.triggered.connect(self.deleteComponent)

        addWingAction.triggered.connect(self.addWing)
        deleteWingAction.triggered.connect(self.deleteWing)

        addSegmentAction.triggered.connect(self.addSegment)
        deleteSegmentAction.triggered.connect(self.deleteSegment)


        editMenu.addAction(addComponentAction)
        editMenu.addAction(deleteComponentAction)
        editMenu.addSeparator()
        editMenu.addAction(addWingAction)
        editMenu.addAction(deleteWingAction)
        editMenu.addSeparator()
        editMenu.addAction(addSegmentAction)
        editMenu.addAction(deleteSegmentAction)

        viewMenu = self.addMenu('View')

        #perspectiveAction = QAction('Change Perspective', self)
        viewXupAction = QAction('X +', self)
        viewYupAction = QAction('Y +', self)
        viewZupAction = QAction('Z +', self)
        viewXdownAction = QAction('X -', self)
        viewYdownAction = QAction('Y -', self)
        viewZdownAction = QAction('Z -', self)

        #perspectiveAction.triggered.connect(self.chgPersp)
        viewXupAction.triggered.connect(self.view_X_up)
        viewYupAction.triggered.connect(self.view_Y_up)
        viewZupAction.triggered.connect(self.view_Z_up)
        viewXdownAction.triggered.connect(self.view_X_down)
        viewYdownAction.triggered.connect(self.view_Y_down)
        viewZdownAction.triggered.connect(self.view_Z_down)

        #viewMenu.addAction(perspectiveAction)
        viewMenu.addAction(viewXupAction)
        viewMenu.addAction(viewYupAction)
        viewMenu.addAction(viewZupAction)
        viewMenu.addAction(viewXdownAction)
        viewMenu.addAction(viewYdownAction)
        viewMenu.addAction(viewZdownAction)

        moduleMenu = self.addMenu('Module')

        #WingModule = QAction('Wing Module', self)
        AirfoilModule = QAction('Airfoil Module', self)

        AirfoilModule.triggered.connect(self.AirfoilModule)

        moduleMenu.addAction(AirfoilModule)

        """Program menu creation"""
        programMenu = self.addMenu('Program')

        manualAction = QAction('User Manual', self)
        aboutAction = QAction('About', self)
        preferencesAction = QAction('Preferences', self)

        manualAction.triggered.connect(self.showManual)
        aboutAction.triggered.connect(self.showAbout)
        preferencesAction.triggered.connect(self.preferencesWindow)

        programMenu.addAction(manualAction)
        programMenu.addAction(aboutAction)
        programMenu.addSeparator()
        programMenu.addAction(preferencesAction)

    def newFile(self):
        msg = QMessageBox.question(self, "New Project", "Do you want to create a new project?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            print("Creating new project...")
            # Reset the project components
            globals.PROJECT.newProject()
            self.main_window.tree_menu.init_tree()

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            globals.loadProject(fileName)
            self.main_window.tree_menu.init_tree()
            print(f"Opened file: {fileName}")

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            globals.saveProject(fileName)
            print(f"Saved file: {fileName}")

    def exportFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File", "", "STEP AP203 (*.step;*.stp);", options=options)
        if fileName:
            import src.utils.step as step
            #step.export_only_control_points(fileName)
            base_name = os.path.basename(fileName)
            step.export_3d_segment_wing(fileName, base_name)
            print(f"Exported file: {fileName}")

    def quitApp(self):
        msg = QMessageBox.question(self, "Exit program", "Do you really want to quit a program?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            print("DEADALUS > exit")
            QApplication.quit()

    def chgPersp(self):
        self.open_gl.toggle_projection()

    def view_X_up(self):
        self.open_gl.position_view(90.0,0.0)
    
    def view_Y_up(self):
        self.open_gl.position_view(0,90)
    
    def view_Z_up(self):
        self.open_gl.position_view(0.0,0.0)
    
    def view_X_down(self):
        self.open_gl.position_view(-90.0,0.0)
    
    def view_Y_down(self):
        self.open_gl.position_view(0,-90)
    
    def view_Z_down(self):
        self.open_gl.position_view(0.0,180.0)

    def placeholder(self):
        print("Placeholder action triggered")

    def addComponent(self):
        """Add a new component to the tree menu."""
        component_obj = src.obj.objects3D.Component()
        component_obj.infos['name'] = f'Component {len(globals.PROJECT.project_components)+1}'  # Ensure the name is set in infos
        component_obj.infos['creation_date'] = date.today().strftime("%Y-%m-%d")
        component_obj.infos['modification_date'] = date.today().strftime("%Y-%m-%d")
        tools_wing.add_component_to_tree(self.main_window.tree_menu, component_obj)
        self.open_gl.update()

    def deleteComponent(self):
        """Add a new wing to the selected component."""
        # Ensure main_window is set
        if self.main_window:
            selected_item = self.main_window.tree_menu.currentItem()
            if selected_item:

                # Find the index of the selected item
                index = self.main_window.tree_menu.indexOfTopLevelItem(selected_item)
                if index != -1:

                    # Remove the item from the tree menu
                    self.main_window.tree_menu.takeTopLevelItem(index)
                    del globals.PROJECT.project_components[index]
                    print(f"ARFDES > delete component > Deleted component at index {index}.")
                    self.main_window.tree_menu.init_tree()
                    self.open_gl.update()

                else:
                    print("ARFDES > deleteAirfoil > Invalid selection.")
            else:
                print("Component NOT selected!")

    def addWing(self):
        """Add a new wing to the selected component."""
        wing_obj = src.obj.objects3D.Wing()
        wing_obj.infos['creation_date'] = date.today().strftime("%Y-%m-%d")
        wing_obj.infos['modification_date'] = date.today().strftime("%Y-%m-%d")

        # Ensure main_window is set
        if self.main_window:
            selected_item = self.main_window.tree_menu.currentItem()
            if selected_item:

                # Add the wing to the component's wings list
                # Find the index of the selected item
                index = self.main_window.tree_menu.indexOfTopLevelItem(selected_item)
                if index != -1:

                    # Add the wing as a child of the selected component
                    wing_name = f'Wing {selected_item.childCount()+1}'
                    wing_obj.infos['name'] = wing_name  # Ensure the name is set in infos
                    wing_item = QTreeWidgetItem([wing_name])
                    selected_item.addChild(wing_item)

                    # Expand the parent item to show the new child
                    selected_item.setExpanded(True)

                    selected_item = globals.PROJECT.project_components[index]
                    #print(f"Found component at index {index}.")
                    tools_wing.add_wing_to_tree(selected_item, wing_name, wing_obj, selected_item)
                    self.open_gl.update()
                    print(f"WNGWB > Added '{wing_name}' as a part of '{selected_item.infos['name']}'.")
                else:
                    print("Cannot set wing to selected item!")
            else:
                print("Component NOT selected!")
        
        #self.airfoil_list.append({"name": name, "data": airfoil_obj.to_dict()})  # Update shared list

    def deleteWing(self):
        """Delete selected wing"""

        # Ensure main_window is set
        if self.main_window:
            selected_item = self.main_window.tree_menu.currentItem()
            if selected_item:

                #Find parent item
                parent_item = selected_item.parent()
                if parent_item:

                    # Find the index of the selected item
                    wing_index = parent_item.indexOfChild(selected_item)
                    component_index = self.main_window.tree_menu.indexOfTopLevelItem(parent_item)

                    if wing_index != -1 and component_index != -1:
                        globals.PROJECT.project_components[component_index].wings[wing_index]
                        # Add the segment as a child of the selected component
                        del globals.PROJECT.project_components[component_index].wings[wing_index]
                        print(f"ARFDES > delete wing > Deleted wing at index {component_index}:{wing_index}.")
                        self.main_window.tree_menu.init_tree()
                        self.open_gl.update()

                    else:
                        print("Cannot set segment to selected item!")
                else:
                    print("Wing NOT selected!")
            else:
                print("Component NOT found!")

    def addSegment(self):
        """Add a new Segment to the selected wing."""
        segment_obj = src.obj.objects3D.Segment()
        segment_obj.airfoil = globals.PROJECT.project_airfoils[0]  # Ensure the name is set in infos
        segment_obj.infos['creation_date'] = date.today().strftime("%Y-%m-%d")
        segment_obj.infos['modification_date'] = date.today().strftime("%Y-%m-%d")

        # Ensure main_window is set
        if self.main_window:
            selected_item = self.main_window.tree_menu.currentItem()
            if selected_item:

                # Add the segment to the wing's segment list
                #Find parent item
                parent_item = selected_item.parent()
                if parent_item:

                    # Find the index of the selected item
                    wing_index = parent_item.indexOfChild(selected_item)
                    component_index = self.main_window.tree_menu.indexOfTopLevelItem(parent_item)

                    #print(wing_index, component_index)

                    if wing_index != -1 and component_index != -1:

                        # Add the segment as a child of the selected component
                        segment_name = f'Segment {selected_item.childCount()+1}'
                        segment_index = selected_item.childCount()
                        #print(segment_name)
                        segment_obj.infos['name'] = segment_name  # Ensure the name is set in infos
                        if selected_item.childCount() > 0:
                            segment_obj.params['origin_Z'] = globals.PROJECT.project_components[component_index].wings[wing_index].segments[selected_item.childCount()-1].params['origin_Z']+0.2
                        
                        segment_item = QTreeWidgetItem([segment_name])
                        selected_item.addChild(segment_item)

                        # Expand the parent item to show the new child
                        selected_item.setExpanded(True)

                        selected_item = globals.PROJECT.project_components[component_index].wings[wing_index]
                        #print(f"Found component at index {component_index} {wing_index}.")
                        tools_wing.add_segment_to_tree(self.main_window.tree_menu, segment_name, segment_obj, component_index, wing_index)
                        segment_obj.update(component_index, wing_index, segment_index)
                        if segment_index > 0:
                            wing_obj = globals.PROJECT.project_components[component_index].wings[wing_index]
                            wing_obj.update(component_index, wing_index, segment_index)
                        #for wing in component_item.wings:
                        #    if wing.infos['name'] == parent_item.text(0):
                        #        wing.segments.append(segment_obj)
                        #        print(f"Added {segment_name} under {wing.infos['name']}.")
                        #        break

                        #tools_wing.add_segment_to_tree(component_item, segment_name, segment_obj, selected_item)
                        self.open_gl.update()

                    else:
                        print("Cannot set segment to selected item!")
                else:
                    print("Wing NOT selected!")
            else:
                print("Component NOT found!")

        #print(len(globals.PROJECT.project_components[component_index].wings[wing_index].segments))
        #if len(globals.PROJECT.project_components[component_index].wings[wing_index].segments) > 1:
        #    globals.PROJECT.project_components[component_index].wings[wing_index].build_connection()
        #    test = globals.PROJECT.project_components[component_index].wings[wing_index].segments[0]
        #    print(test)
            
    
    def deleteSegment(self):
        """Delete selected segment"""

        # Ensure main_window is set
        if self.main_window:
            selected_item = self.main_window.tree_menu.currentItem()
            if selected_item:

                #Find parent item
                parent_item = selected_item.parent()
                if parent_item:

                    try:
                        grandparent_item = parent_item.parent()
                    except:
                        print("ERROR: Segment is not part of the component!")

                    if grandparent_item:

                        # Find the index of the selected item
                        segment_index = parent_item.indexOfChild(selected_item)
                        wing_index = grandparent_item.indexOfChild(parent_item)
                        component_index = self.main_window.tree_menu.indexOfTopLevelItem(grandparent_item)

                        del globals.PROJECT.project_components[component_index].wings[wing_index].segments[segment_index]
                        print(f"ARFDES > delete segment > Deleted segment at index {component_index}:{wing_index}:{segment_index}.")
                        self.main_window.tree_menu.init_tree()
                        self.open_gl.update()

                    else:
                        print("Cannot set segment to selected item!")
                else:
                    print("Wing NOT selected!")
            else:
                print("Component NOT found!")

    def WingModule(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Wing Module")
        msg.setText("Wing Module functionality is under development.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        #self.airfoil_designer_window = AirfoilDesigner(airfoil_list=globals.airfoil_list)  # Pass airfoil_list
        self.airfoil_designer_window = AirfoilDesigner()  # Pass airfoil_list
        self.airfoil_designer_window.show()

    def AirfoilModule(self):
        self.airfoil_designer_window = AirfoilDesigner()  
        self.airfoil_designer_window.show()

    def preferencesWindow(self):        
        """Open the preferences dialog."""
        print("DEADALUS > Preferences")
        from src.preferences import PreferencesWindow
        self.preferences_dialog = PreferencesWindow(self)
        self.preferences_dialog.show()
        msg = QMessageBox(self)
        msg.setWindowTitle("WARNING!")
        msg.setText(f"If you changed the preferences, you need to restart the application for the changes to take effect.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def showAbout(self):
        dialog = globals.DEADALUS.showAboutDialog(self)

    def showManual(self):
        manual = globals.DEADALUS.showUserManual()