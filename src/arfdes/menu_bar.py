from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QApplication, QLabel, QInputDialog, QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox
import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMenuBar, QAction, QFileDialog, QTreeWidget, QTreeWidgetItem, QTextEdit, QStackedWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
import numpy as np
import json
import os
from scipy.interpolate import splprep, splev, interpolate, BSpline, interp1d
from scipy.optimize import minimize, root_scalar
from scipy import interpolate
from tqdm import tqdm
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QPushButton
)

from utils.tools_airfoil import Reference_load
from obj.aero import Airfoil
from utils.tools_airfoil import add_airfoil_to_tree

from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout,
    QPushButton, QLineEdit, QHeaderView
)
from datetime import date

import globals  # Import from globals.py

class MenuBar(QMenuBar):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, program=None, project=None, parent=None, canvas=None, program_info=None, tree_menu=None):
        super(MenuBar, self).__init__(parent)
        self.AIRFLOW = program
        self.PROJECT = project
        self.main_window = parent
        self.canvas = canvas
        self.tree_menu = tree_menu
        self.program_info = globals.Program()  # Store the Program instance
        self.createMenu()

    def createMenu(self):
        """File menu creation"""
        fileMenu = self.addMenu('File')
        
        newFileAction = QAction('New', self)
        openFileAction = QAction('Open', self)
        saveFileAction = QAction('Save', self)
        preferencesFileAction = QAction('Preferences', self)
        
        newFileAction.triggered.connect(self.newProject)
        openFileAction.triggered.connect(self.openProject)
        saveFileAction.triggered.connect(self.saveProject)
        preferencesFileAction.triggered.connect(self.preferencesWindow)

        fileMenu.addAction(newFileAction)
        fileMenu.addAction(openFileAction)
        fileMenu.addAction(saveFileAction)
        fileMenu.addSeparator()
        fileMenu.addAction(preferencesFileAction)


        editMenu = self.addMenu('Edit')

        newAction = QAction('Create', self)
        appendAction = QAction('Append', self)
        deleteAction = QAction('Delete', self)
        saveAction = QAction('Save', self)
        exportAction = QAction('Export', self)
        renameArfAction = QAction('Rename', self)
        editDescriptionAction = QAction('Edit Description', self)
        fit2refAction = QAction('Fit2Reference', self)

        newAction.triggered.connect(self.newAirfoil)
        appendAction.triggered.connect(self.appendAirfoil)
        deleteAction.triggered.connect(self.deleteAirfoil)  
        saveAction.triggered.connect(self.saveAirfoil)
        exportAction.triggered.connect(self.exportAirfoil)
        renameArfAction.triggered.connect(self.renameAirfoil)
        editDescriptionAction.triggered.connect(self.editDescriptionAirfoil)
        fit2refAction.triggered.connect(self.fit2ref)
        
        editMenu.addAction(newAction)
        editMenu.addAction(appendAction)
        editMenu.addAction(deleteAction)
        editMenu.addAction(saveAction)
        editMenu.addAction(exportAction)
        editMenu.addSeparator()
        editMenu.addAction(renameArfAction)
        editMenu.addAction(editDescriptionAction)
        editMenu.addAction(fit2refAction)


        viewMenu = self.addMenu('View')

        referenceAction = QAction('Show reference', self)
        referenceAction.setCheckable(True)
        referenceAction.setChecked(False)
        referenceAction.triggered.connect(self.toggleReference)

        viewMenu.addAction(referenceAction)


        moduleMenu = self.addMenu('Module')
        WingModule = QAction('Wing Module', self)
        WingModule.triggered.connect(self.open_wing_module)
        moduleMenu.addAction(WingModule)

        helpMenu = self.addMenu('Help')
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)

    def newProject(self):
        msg = QMessageBox.question(self, "New Project", "Do you want to create a new project?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            print("Creating new project...")
            # Reset the project components
            globals.PROJECT.newProject()

    def openProject(self):
        print("Opening project")
        if self.main_window:
            pass
    
    def saveProject(self):
        print("Saving project")
        if self.main_window:
            pass

    def newAirfoil(self):
        print("Creating new airfoil")
        if self.main_window:  # Ensure main_window is set
            #add_airfoil_to_tree(self.main_window.tree_menu, self.main_window.airfoils_list, "Default Airfoil", Airfoil()) is set
            self.main_window.add_airfoil("Airfoil")

    def appendAirfoil(self):
        """load the airfoil data from a JSON format file."""
        # Use self.program_info to access program details
        if not self.program_info:
            print("Program info not available.")
            return
        
        Airfoil = Airfoil()

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(f"Opened file: {fileName}")

            try:
                with open(f"{fileName}.arf", "r") as file:
                    data = json.load(file)
                    print("File load: Success!")
            except FileNotFoundError:
                print("File not found!")
            except json.JSONDecodeError:
                print("Error decoding JSON!")

        if data:
            program_version = data["program version"]
            airfoil_designer_version = data["airfoil designer version"]
            component = data["component"]


            if airfoil_designer_version != self.program_info.airfoil_designer_verison:
                print("Warning: Airfoil Designer version mismatch.")
                # Handle version mismatch if necessary
            if program_version != self.program_info.program_version:
                print("Warning: Program version mismatch.")
                # Handle version mismatch if necessary

            if airfoil_designer_version == self.program_info.airfoil_designer_verison:
                print("Airfoil Designer version match.")
                # Handle version match if necessary
                Airfoil.chord = component["airfoil"]["chord"]
                Airfoil.origin_X = component["airfoil"]["origin_X"]
                Airfoil.origin_Y = component["airfoil"]["origin_Y"]
                Airfoil.le_thickness = component["airfoil"]["le_thickness"]
                Airfoil.le_depth = component["airfoil"]["le_depth"]
                Airfoil.le_offset = component["airfoil"]["le_offset"]
                Airfoil.le_angle = component["airfoil"]["le_angle"]
                Airfoil.te_thickness = component["airfoil"]["te_thickness"]
                Airfoil.te_depth = component["airfoil"]["te_depth"]
                Airfoil.te_offset = component["airfoil"]["te_offset"]
                Airfoil.te_angle = component["airfoil"]["te_angle"]
                Airfoil.ps_fwd_angle = component["airfoil"]["ps_fwd_angle"]
                Airfoil.ps_rwd_angle = component["airfoil"]["ps_rwd_angle"]
                Airfoil.ps_fwd_accel = component["airfoil"]["ps_fwd_accel"]
                Airfoil.ps_rwd_accel = component["airfoil"]["ps_rwd_accel"]
                Airfoil.ss_fwd_angle = component["airfoil"]["ss_fwd_angle"]
                Airfoil.ss_rwd_angle = component["airfoil"]["ss_rwd_angle"]
                Airfoil.ss_fwd_accel = component["airfoil"]["ss_fwd_accel"]
                Airfoil.ss_rwd_accel = component["airfoil"]["ss_rwd_accel"]
                Airfoil.infos = {
                    "name": component["airfoil"]["infos"]["name"],
                    "creation_date": component["airfoil"]["infos"]["creation_date"],
                    "modification_date": component["airfoil"]["infos"]["modification_date"],
                    "description": component["airfoil"]["infos"]["description"]
                }
                # Add the airfoil to the tree menu
                self.main_window.add_airfoil(Airfoil)

            #Airfoil_0.UP_points, Airfoil_0.DW_points, Airfoil_0.name = Reference_load(fileName)
            #Airfoil_0.le, Airfoil_0.ps, Airfoil_0.ss, Airfoil_0.te = Convert(0.08, 0.08, Airfoil_0.UP_points, Airfoil_0.DW_points)

    def deleteAirfoil(self):
        print("Deleting selected airfoil")
        if self.main_window:  # Ensure main_window is set
            selected_item = self.main_window.tree_menu.currentItem()
            if not selected_item:
                print("No airfoil selected for deletion.")
                return

            # Find the index of the selected item
            index = self.main_window.tree_menu.indexOfTopLevelItem(selected_item)
            if index != -1:
                # Remove the item from the tree menu
                self.main_window.tree_menu.takeTopLevelItem(index)
                # Remove the corresponding airfoil from the airfoils_list
                print(self.PROJECT.project_airfoils)
                del self.PROJECT.project_airfoils[index]
                print(f"Deleted airfoil at index {index}.")
                self.canvas.clear_plot()
            else:
                print("Invalid selection.")
            
    def saveAirfoil(self):
        """Save the airfoil data to a JSON format file."""
        # Use self.program_info to access program details
        if not self.program_info:
            print("Program info not available.")
            return

        selected_item = self.main_window.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected
 
        # Find the corresponding airfoil object
        airfoil_index = self.main_window.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection
 
        current_airfoil = self.PROJECT.project_airfoils[airfoil_index]

        component = {}

        component['airfoil'] = {
            "infos": {
                **current_airfoil.infos,
                "name": str(current_airfoil.infos.get("name", "")),
                "creation_date": str(current_airfoil.infos.get("creation_date", "")),
                "modification_date": str(current_airfoil.infos.get("modification_date", "")),
                "description": str(current_airfoil.infos.get("description", ""))
            },
            "chord": current_airfoil.chord,
            "origin_X": current_airfoil.origin_X,
            "origin_Y": current_airfoil.origin_Y,
            "le_thickness": current_airfoil.le_thickness,
            "le_depth": current_airfoil.le_depth,
            "le_offset": current_airfoil.le_offset,
            "le_angle": current_airfoil.le_angle,
            "te_thickness": current_airfoil.te_thickness,
            "te_depth": current_airfoil.te_depth,
            "te_offset": current_airfoil.te_offset,
            "te_angle": current_airfoil.te_angle,
            "ps_fwd_angle": current_airfoil.ps_fwd_angle,
            "ps_rwd_angle": current_airfoil.ps_rwd_angle,
            "ps_fwd_accel": current_airfoil.ps_fwd_accel,
            "ps_rwd_accel": current_airfoil.ps_rwd_accel,
            "ss_fwd_angle": current_airfoil.ss_fwd_angle,
            "ss_rwd_angle": current_airfoil.ss_rwd_angle,
            "ss_fwd_accel": current_airfoil.ss_fwd_accel,
            "ss_rwd_accel": current_airfoil.ss_rwd_accel
        }
 
        data = {
            "program name": self.program_info.program_name,
            "program version": self.program_info.program_version,
            "airfoil designer version": self.program_info.airfoil_designer_verison,
            "component": component,
        }
 
        json_object = json.dumps(data, indent=1)

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.arf)", options=options)
        if fileName:
            with open(f"{fileName}", "w") as outfile:
                outfile.write(json_object)
                print(f"Saved file: {fileName}")
 
    def exportAirfoil(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            print(f"Exported file: {fileName}")

    #Edit menu actions

    def renameAirfoil(self):
        """Rename currently selected airfoil."""
        self.le = QLabel(self)
        selected_item = self.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        current_airfoil = self.PROJECT.project_airfoils[airfoil_index]

        text, ok = QInputDialog.getText(self, 'Change Airfoils Name', 'Enter airfoil\'s new name:')
        if ok:
            self.le.setText(str(text))
        if text:
            #setattr(current_airfoil, 'name', text)
            # Update the airfoil object with the new name
            current_airfoil.infos['name'] = text
            current_airfoil.infos['modification_date'] = str(date.today())
            
        # Optionally, update the tree menu display
        selected_item.setText(0, f"{current_airfoil.infos['name']}*")

    def editDescriptionAirfoil(self):
        """Edit the description of an airfoil."""
        selected_item = self.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        current_airfoil = self.PROJECT.project_airfoils[airfoil_index]

        # Create a custom dialog with QTextEdit
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Airfoil Description")
        layout = QVBoxLayout(dialog)

        label = QLabel("Edit the description below:", dialog)
        layout.addWidget(label)

        text_edit = QTextEdit(dialog)
        text_edit.setText(current_airfoil.infos.get('description', ''))  # Pre-fill with current description
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layout.addWidget(button_box)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        if dialog.exec_() == QDialog.Accepted:
            new_description = text_edit.toPlainText()
            if new_description:
                # Update the airfoil object with the new description
                current_airfoil.infos['description'] = new_description
                print(f"Updated description for airfoil: {current_airfoil.infos['name']}")

            # Optionally, update the tree menu display
            selected_item.setText(0, f"{current_airfoil.infos['name']}*")

    def fit2ref(self):
        print("Fit2Ref action triggered")

    def preferencesWindow(self):        
        print("Placeholder action triggered")
        msg = QMessageBox(self)
        msg.setWindowTitle("Preferences")
        msg.setText("Preferences functionality is under development.")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        #self.airfoil_designer_window = AirfoilDesigner()dardButtons(QMessageBox.Ok)
        #self.airfoil_designer_window.show()        #self.airfoil_designer_window.show()

    def toggleReference(self):
        sender = self.sender()
        if hasattr(sender, 'isChecked') and callable(sender.isChecked):
            if sender.isChecked():
                print("Show reference")
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
                if fileName:
                    print(f"Opened file: {fileName}")
                    #AirfoilCoord, UP_points, DW_points, name = DataBase_load(fileName, os.getcwd())
                    referenceState = True
                    self.referenceStatus.emit(referenceState, fileName)
            else:
                print("Hide reference")
                referenceState = False
                self.referenceStatus.emit(referenceState, None)

    def open_wing_module(self):
        from wngwb.main_window import MainWindow  # Late import to avoid circular dependency
        #msg = QMessageBox(self)
        #msg.setWindowTitle("Wing Module")
        #msg.setText("Wing Module functionality is under development.")
        #msg.setIcon(QMessageBox.Information)
        #msg.setStandardButtons(QMessageBox.Ok)
        #msg.exec_()
        self.airfoil_designer_window = MainWindow()  # Pass airfoil_list
        self.airfoil_designer_window.show()

    def showAbout(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About")
        msg.setText("Airfoil Designer\nVersion: 1.0\nAuthor: Jakub Kamyk")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        