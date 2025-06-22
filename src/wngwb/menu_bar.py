from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QApplication
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout, QLabel, QMenuBar, QAction, QFileDialog, QTreeWidget, QTreeWidgetItem, QTextEdit, QStackedWidget, QMessageBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
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

from opengl.viewport import ViewportOpenGL
from OpenGL.GL import *  # Import OpenGL functions
from OpenGL.GLU import *  # Import GLU functions (e.g., gluPerspective)
from arfdes.airfoil_designer import AirfoilDesigner
import globals  # Import from globals.py

from utils import tools_wing  # Import add_component_to_tree

from datetime import date

import obj

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super(MenuBar, self).__init__(parent)
        self.main_window = parent
        self.viewport = ViewportOpenGL()
        self.createMenu()

    def createMenu(self):
        fileMenu = self.addMenu('File')
        
        newAction = QAction('New', self)
        openAction = QAction('Open', self)
        saveAction = QAction('Save', self)
        exportAction = QAction('Export', self)

        newAction.triggered.connect(self.newFile)
        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        exportAction.triggered.connect(self.exportFile)

        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exportAction)

        editMenu = self.addMenu('Edit')

        addComponentAction = QAction('Add Component', self)
        appendComponentAction = QAction('Append Component', self)
        copyComponentAction = QAction('Copy Component', self)
        renameComponentAction = QAction('Rename Component', self)
        deleteComponentAction = QAction('Delete Component', self)
        addWingAction = QAction('Add Wing', self)
        appendWingAction = QAction('Append Wing', self)
        copyWingAction = QAction('Copy Wing', self)
        renameWingAction = QAction('Rename Wing', self)
        deleteWingAction = QAction('Delete Wing', self)
        addSectionAction = QAction('Add Section', self)
        appendSectionAction = QAction('Append Section', self)
        copySectionAction = QAction('Copy Section', self)
        renameSectionAction = QAction('Rename Section', self)
        deleteSectionAction = QAction('Delete Section', self)
        preferencesAction = QAction('Preferences', self)

        addComponentAction.triggered.connect(self.addComponent)
        addWingAction.triggered.connect(self.addWing)
        addSectionAction.triggered.connect(self.addSection)
        preferencesAction.triggered.connect(self.preferencesWindow)

        editMenu.addAction(addComponentAction)
        editMenu.addAction(addWingAction)
        editMenu.addAction(addSectionAction)
        editMenu.addAction(preferencesAction)

        viewMenu = self.addMenu('View')

        perspectiveAction = QAction('Change Perspective', self)

        perspectiveAction.triggered.connect(self.chgPersp)

        viewMenu.addAction(perspectiveAction)

        moduleMenu = self.addMenu('Module')

        #WingModule = QAction('Wing Module', self)
        AirfoilModule = QAction('Airfoil Module', self)

        AirfoilModule.triggered.connect(self.AirfoilModule)

        moduleMenu.addAction(AirfoilModule)

    def newFile(self):
        msg = QMessageBox.question(self, "New Project", "Do you want to create a new project?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            print("Creating new project...")
            # Reset the project components
            globals.PROJECT.newProject()

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(f"Opened file: {fileName}")

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(f"Saved file: {fileName}")

    def exportFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File", "", "STEP AP203 (*.step;*.stp);", options=options)
        if fileName:
            import utils.step as step
            step.export_simple_wing(fileName)
            print(f"Exported file: {fileName}")


    def quitApp(self):
        QApplication.quit()

    def chgPersp(self):
        self.viewport.toggle_projection()

    def placeholder(self):
        print("Placeholder action triggered")

    def addComponent(self, name='Component'):
        """Add a new component to the tree menu."""
        component_obj = obj.aero.Component()
        component_obj.infos['name'] = name  # Ensure the name is set in infos
        component_obj.infos['creation_date'] = date.today()
        component_obj.infos['modification_date'] = date.today()
        tools_wing.add_component_to_tree(self.main_window.tree_menu, name, component_obj)
        
    def addWing(self):
        """Add a new wing to the selected component."""
        wing_obj = obj.aero.Wing()
        #wing_obj.infos['creation_date'] = date.today()
        #wing_obj.infos['modification_date'] = date.today()

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
                    print(f"Added {wing_name} under {selected_item}.")
                else:
                    print("Cannot set wing to selected item!")
            else:
                print("Component NOT selected!")
        
        #self.airfoil_list.append({"name": name, "data": airfoil_obj.to_dict()})  # Update shared list

    def addSection(self):
        """Add a new section to the selected wing."""
        segment_obj = obj.aero.Segment()
        segment_obj.airfoil = globals.PROJECT.project_airfoils[0]  # Ensure the name is set in infos
        #wing_obj.infos['creation_date'] = date.today()
        #wing_obj.infos['modification_date'] = date.today()

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

                    print(wing_index, component_index)

                    if wing_index != -1 and component_index != -1:

                        # Add the segment as a child of the selected component
                        segment_name = f'Segment {selected_item.childCount()+1}'
                        segment_obj.infos['name'] = segment_name  # Ensure the name is set in infos
                        segment_item = QTreeWidgetItem([segment_name])
                        selected_item.addChild(segment_item)

                        # Expand the parent item to show the new child
                        selected_item.setExpanded(True)

                        selected_item = globals.PROJECT.project_components[component_index].wings[wing_index]
                        #print(f"Found component at index {component_index} {wing_index}.")
                        tools_wing.add_segment_to_tree(self.main_window.tree_menu, segment_name, segment_obj, component_index, wing_index)
                        #for wing in component_item.wings:
                        #    if wing.infos['name'] == parent_item.text(0):
                        #        wing.segments.append(segment_obj)
                        #        print(f"Added {segment_name} under {wing.infos['name']}.")
                        #        break

                        #tools_wing.add_segment_to_tree(component_item, segment_name, segment_obj, selected_item)

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
        msg = QMessageBox(self)
        msg.setWindowTitle("Airfoil Module")
        msg.setText("Airfoil Module functionality is under development.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        #self.airfoil_designer_window = AirfoilDesigner(airfoil_list=globals.airfoil_list)  # Pass airfoil_list
        self.airfoil_designer_window = AirfoilDesigner()  # Pass airfoil_list
        self.airfoil_designer_window.show()

        # Add a button or menu action to open the AirfoilDesigner
        #self.open_airfoil_designer_action = QAction("Open Airfoil Designer", self)
        #self.open_airfoil_designer_action.triggered.connect(self.open_airfoil_designer)
        #self.menu_bar.addAction(self.open_airfoil_designer_action)

    #def open_airfoil_designer(self):
        """Open the AirfoilDesigner window."""
        #self.airfoil_designer = AirfoilDesigner(airfoil_list)  # Pass airfoil_list
        #self.airfoil_designer.show()

    def preferencesWindow(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Preferences")
        msg.setText("Preferences functionality is under development.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        #self.airfoil_designer_window = AirfoilDesigner()
        #self.airfoil_designer_window.show()