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

import src.utils.dxf as dxf
import src.arfdes.tools_airfoil as tools_airfoil
from src.arfdes.tools_airfoil import Reference_load
from src.obj.objects2D import Airfoil
from src.arfdes.widget_tree import add_airfoil_to_tree

from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout,
    QPushButton, QLineEdit, QHeaderView
)
from datetime import date
import src.arfdes.fit_2_reference as fit_2_reference  # Import the fitting module
import src.globals as globals  # Import from globals.py
import src.arfdes.widget_tree as widget_tree

class MenuBar(QMenuBar):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, program=None, project=None, parent=None, canvas=None, program_info=None, tree_menu=None):
        super(MenuBar, self).__init__(parent)
        self.DEADALUS = program
        self.PROJECT = project
        self.main_window = parent
        self.canvas = canvas
        self.tree_menu = tree_menu
        self.program_info = globals.Program()  # Store the Program instance
        self.createMenu()

    def createMenu(self):
        """File menu creation"""
        fileMenu = self.addMenu('File')
        
        newAction = QAction('New', self)
        openAction = QAction('Open', self)
        saveAction = QAction('Save', self)
        exitAction = QAction('Exit', self)

        newAction.triggered.connect(self.newFile)
        openAction.triggered.connect(self.openFile)
        saveAction.triggered.connect(self.saveFile)
        exitAction.triggered.connect(self.quitApp)

        fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        

        """Edit menu creation"""
        editMenu = self.addMenu('Edit')

        newAirfoilAction = QAction('Create', self)
        appendAirfoilAction = QAction('Append', self)
        deleteAirfoilAction = QAction('Delete', self)
        saveAirfoilAction = QAction('Save', self)
        exportAirfoilAction = QAction('Export', self)
        flipAirfoilAction = QAction('Flip Airfoil', self)
        renameAirfoilAction = QAction('Rename', self)
        editDescriptionAction = QAction('Edit Description', self)
        fit2refAction = QAction('Fit2Reference', self)

        newAirfoilAction.triggered.connect(self.newAirfoil)
        appendAirfoilAction.triggered.connect(self.appendAirfoil)
        deleteAirfoilAction.triggered.connect(self.deleteAirfoil)  
        saveAirfoilAction.triggered.connect(self.saveAirfoil)
        exportAirfoilAction.triggered.connect(self.exportAirfoil)
        flipAirfoilAction.triggered.connect(self.flipAirfoil)
        renameAirfoilAction.triggered.connect(self.renameAirfoil)
        editDescriptionAction.triggered.connect(self.editDescriptionAirfoil)
        fit2refAction.triggered.connect(self.fit2ref)
        
        editMenu.addAction(newAirfoilAction)
        editMenu.addAction(appendAirfoilAction)
        editMenu.addAction(deleteAirfoilAction)
        editMenu.addAction(saveAirfoilAction)
        editMenu.addAction(exportAirfoilAction)
        editMenu.addAction(flipAirfoilAction)
        editMenu.addSeparator()
        editMenu.addAction(renameAirfoilAction)
        editMenu.addAction(editDescriptionAction)
        if globals.DEADALUS.preferences['general']['beta_features']:
            editMenu.addAction(fit2refAction)

        """View menu creation"""
        viewMenu = self.addMenu('View')

        referenceAction = QAction('Show reference', self)
        referenceAction.setCheckable(True)
        referenceAction.setChecked(False)
        referenceAction.triggered.connect(self.toggleReference)

        viewMenu.addAction(referenceAction)

        """Module menu creation"""
        moduleMenu = self.addMenu('Module')
        WingModule = QAction('Wing Module', self)
        WingModule.triggered.connect(self.open_wing_module)
        moduleMenu.addAction(WingModule)

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
            print("DEADALUS: Creating new project...")
            # Reset the project components
            globals.PROJECT.newProject()
            widget_tree.refresh_tree(self.tree_menu)

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            globals.loadProject(fileName)
            print(f"DEADALUS: opened file '{fileName}'")
            widget_tree.refresh_tree(self.tree_menu)

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            globals.saveProject(fileName)
            print(f"Saved file: {fileName}")
    
    def quitApp(self):
        msg = QMessageBox.question(self, "Exit program", "Do you really want to quit a program?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            print("DEADALUS > exit")
            QApplication.quit()
    
    """Airfoil menu actions"""
    
    def newAirfoil(self):
        print("ARFDES > Creating new airfoil")
        if self.main_window:  # Ensure main_window is set
            #add_airfoil_to_tree(self.main_window.tree_menu, self.main_window.airfoils_list, "Default Airfoil", Airfoil()) is set
            self.main_window.add_airfoil("Airfoil")

    def appendAirfoil(self):
        """load the airfoil data from a JSON format file."""
        print("ARFDES > appendAirfoil > Appending airfoil...")
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Deadalus Airfoil Format (*.arf);;All Files (*)", options=options)

        if fileName:
            airfoil_obj, _ = tools_airfoil.load_airfoil_from_json(fileName)
            # Add the airfoil to the tree menu
            globals.PROJECT.project_airfoils.append(airfoil_obj)
            print(airfoil_obj)
            if airfoil_obj:
                add_airfoil_to_tree(self.tree_menu, airfoil_obj.infos['name'], airfoil_obj)
            else:
                print("ARFDES ERROR: Airfoil import failed!")

    def deleteAirfoil(self):
        print("ARFDES > deleteAirfoil > Deleting selected airfoil...")
        if self.main_window:  # Ensure main_window is set
            selected_item = self.main_window.tree_menu.currentItem()
            if not selected_item:
                print("ARFDES > deleteAirfoil > No airfoil selected for deletion.")
                return

            # Find the index of the selected item
            index = self.main_window.tree_menu.indexOfTopLevelItem(selected_item)
            if index != -1:
                # Remove the item from the tree menu
                self.main_window.tree_menu.takeTopLevelItem(index)
                # Remove the corresponding airfoil from the airfoils_list
                print(self.PROJECT.project_airfoils)
                del self.PROJECT.project_airfoils[index]
                print(f"ARFDES > deleteAirfoil > Deleted airfoil at index {index}.")
                self.canvas.clear_plot()
            else:
                print("ARFDES > deleteAirfoil > Invalid selection.")
            
    def saveAirfoil(self):
        """Save the airfoil data to a JSON format file."""
        print("ARFDES > saveAirfoil > Saving selected airfoil...")
        selected_item = self.main_window.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected
 
        # Find the corresponding airfoil object
        airfoil_index = self.main_window.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        json_object = tools_airfoil.save_airfoil_to_json(airfoil_index)

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "DEADALUS Airfoil Format (*.arf);;All Files (*)", options=options)
        if fileName:
            with open(f"{fileName}", "w") as outfile:
                outfile.write(json_object)
                print(f"ARFDES > saveAirfoil > Saved file: {fileName}")
 
    def exportAirfoil(self):
        """Export the airfoil data to a DXF format file."""
        print("ARFDES > exportAirfoil > Exporting selected airfoil...")
        selected_item = self.main_window.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected
 
        # Find the corresponding airfoil object
        airfoil_index = self.main_window.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection
        
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File to DXF format", "", "DXF Format (*.dxf);;All Files (*)", options=options)
        if fileName:
            dxf.export_airfoil_to_dxf(airfoil_index, fileName)
            print(f"ARFDES > exportAirfoil > Exported file: {fileName}")

    def renameAirfoil(self):
        """Rename currently selected airfoil."""
        print("ARFDES > renameAirfoil > Renaming selected airfoil...")
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
            current_airfoil.infos['modification_date'] = date.today().strftime("%Y-%m-%d")
            
        # Optionally, update the tree menu display
        selected_item.setText(0, f"{current_airfoil.infos['name']}*")
        print("Done")
    
    def flipAirfoil(self):
        """Flip the currently selected airfoil."""
        print("ARFDES > flipAirfoil > Flipping selected airfoil...")
        selected_item = self.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        current_airfoil = self.PROJECT.project_airfoils[airfoil_index]

        flipped_airfoil = tools_airfoil.flip_airfoil_horizontally(current_airfoil)

        if flipped_airfoil:
            self.PROJECT.project_airfoils[airfoil_index] = flipped_airfoil
        print('Done')

    def editDescriptionAirfoil(self):
        """Edit the description of an airfoil."""
        print("ARFDES > editDescriptionAirfoil > Editing selected airfoil description...")
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
        """Fit the currently selected airfoil in tree_menu to the reference_airfoil by optimizing its parameters."""
        print("ARFDES > fit2ref > Opening Fit2Ref window...")
        # Get selected item and corresponding airfoil object
        selected_items = self.tree_menu.selectedItems()
        if not selected_items:
            print("No airfoil selected in the tree menu.")
            return None
        selected_item = selected_items[0]
        airfoil_name = selected_item.text(0)
        # Find airfoil object by name
        current_airfoil = None
        for af in globals.PROJECT.project_airfoils:
            if af.infos.get('name', '') == airfoil_name:
                current_airfoil = af
                break
        if current_airfoil is None:
            print("Selected airfoil object not found.")
            return None
        
        # Open the Fit2RefWindow dialog
        dlg = fit_2_reference.Fit2RefWindow(parent=self.main_window, current_airfoil=current_airfoil, reference_airfoil=self.main_window.reference_airfoil)
        dlg.exec_()

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
        
        for airfoil in globals.PROJECT.project_airfoils:
            airfoil.update()

        from src.wngwb.main_window import MainWindow  # Late import to avoid circular dependency
        self.airfoil_designer_window = MainWindow()  # Pass airfoil_list
        self.airfoil_designer_window.show()

    def showAbout(self):
        dialog = globals.DEADALUS.showAboutDialog(self)
    
    def showManual(self):
        manual = globals.DEADALUS.showUserManual()
