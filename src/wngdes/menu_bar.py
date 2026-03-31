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
import logging
import sys
from PyQt5 import QtCore
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
    QMenuBar, QAction, QFileDialog, QApplication,
    QMainWindow, QSplitter, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout, QLabel,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QStackedWidget, QMessageBox,
    QTableWidget, QTableWidgetItem, QPushButton
)

import src.obj.objects3D
from OpenGL.GL import *  # Import OpenGL functions
from OpenGL.GLU import *  # Import GLU functions (e.g., gluPerspective)
from src.arfdes.airfoil_designer import AirfoilDesigner


from datetime import date
import src.obj

class MenuBar(QMenuBar):
    def __init__(self, program=None, project=None, parent=None, viewport=None):
        super(MenuBar, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DEADALUS = program
        self.PROJECT = project
        self.WINGDESIGNER = parent
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

        addComponentAction.triggered.connect(self.WINGDESIGNER.addComponent)
        deleteComponentAction.triggered.connect(self.WINGDESIGNER.deleteComponent)

        addWingAction.triggered.connect(self.WINGDESIGNER.addWing)
        deleteWingAction.triggered.connect(self.WINGDESIGNER.deleteWing)

        addSegmentAction.triggered.connect(self.WINGDESIGNER.addSegment)
        deleteSegmentAction.triggered.connect(self.WINGDESIGNER.deleteSegment)


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

        """Window menu creation"""
        windowMenu = self.addMenu('Window')

        # self.airfoilWidgetAction = QAction('Airfoil Tree', self)
        # self.airfoilWidgetAction.setCheckable(True)
        # self.airfoilWidgetAction.setChecked(True)
        # self.airfoilWidgetAction.triggered.connect(self.toggle_airfoil)

        # self.parametersWidgetAction = QAction('Parameters Table', self)
        # self.parametersWidgetAction.setCheckable(True)
        # self.parametersWidgetAction.setChecked(True)
        # self.parametersWidgetAction.triggered.connect(self.toggle_parameters)

        # self.referenceWidgetAction = QAction('Reference Tree', self)
        # self.referenceWidgetAction.setCheckable(True)
        # self.referenceWidgetAction.setChecked(True)
        # self.referenceWidgetAction.triggered.connect(self.toggle_reference)

        # self.statisticsWidgetAction = QAction('Statistics Table', self)
        # self.statisticsWidgetAction.setCheckable(True)
        # self.statisticsWidgetAction.setChecked(True)
        # self.statisticsWidgetAction.triggered.connect(self.toggle_statistics)

        # self.descriptionWidgetAction = QAction('Description Widget', self)
        # self.descriptionWidgetAction.setCheckable(True)
        # self.descriptionWidgetAction.setChecked(True)
        # self.descriptionWidgetAction.triggered.connect(self.toggle_description)

        self.loggerWidgetAction = QAction('Logger Console', self)
        self.loggerWidgetAction.setCheckable(True)
        self.loggerWidgetAction.setChecked(True)
        self.loggerWidgetAction.triggered.connect(self.toggle_logger)

        # windowMenu.addAction(self.airfoilWidgetAction)
        # windowMenu.addAction(self.parametersWidgetAction)
        # windowMenu.addAction(self.referenceWidgetAction)
        # windowMenu.addAction(self.statisticsWidgetAction)
        # windowMenu.addAction(self.descriptionWidgetAction)
        windowMenu.addAction(self.loggerWidgetAction)

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
            self.logger.info("Creating new project...")
            # Reset the project components
            self.PROJECT.new()
            self.main_window.tree_menu.init_tree()

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            self.PROJECT.load(fileName)
            self.main_window.tree_menu.init_tree()
            self.logger.info(f"Opened file: {fileName}")

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            self.PROJECT.save(fileName)
            self.logger.info(f"Saved file: {fileName}")

    def exportFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File", "", "STEP AP203 (*.step;*.stp);", options=options)
        if fileName:
            import src.utils.step as step
            #step.export_only_control_points(fileName)
            base_name = os.path.basename(fileName)
            step.export_3d_segment_wing(fileName, base_name)
            self.logger.info(f"Exported file: {fileName}")

    def quitApp(self):
        msg = QMessageBox.question(self, "Exit program", "Do you really want to quit a program?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.logger.info("Normal exit :)")
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
        self.logger.info("Placeholder action triggered")

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
        self.logger.info("Preferences")
        from program.preferences import PreferencesWindow
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
    
    def update_action_state(self, action, dock_widget):
        """Update the state of the given action based on the dock widget's visibility."""
        action.setChecked(dock_widget.isVisible())
    
    def toggle_airfoil(self):
        """Toggle the description widget."""
        if self.parent():
            self.parent().toggle_airfoil()  # Call the correct method in AirfoilDesigner

    def toggle_parameters(self):
        """Toggle the description widget."""
        if self.parent():
            self.parent().toggle_parameters()  # Call the correct method in AirfoilDesigner

    def toggle_statistics(self):
        """Toggle the description widget."""
        if self.parent():
            self.parent().toggle_statistics()  # Call the correct method in AirfoilDesigner

    def toggle_reference(self):
        """Toggle the description widget."""
        if self.parent():
            self.parent().toggle_reference()  # Call the correct method in AirfoilDesigner

    def toggle_description(self):
        """Toggle the description widget."""
        if self.parent():
            self.parent().toggle_description()  # Call the correct method in AirfoilDesigner
    
    def toggle_logger(self):
        """Toggle the description widget."""
        if self.parent():
            self.parent().toggle_logger()  # Call the correct method in AirfoilDesigner