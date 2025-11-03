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

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout, QVBoxLayout,
    QMenuBar, QAction, QFileDialog, 
    QLineEdit, QTextEdit,
    QTreeWidget, QTreeWidgetItem, 
    QApplication, QLabel, QInputDialog, QDialog, QDialogButtonBox,
    QStackedWidget, QMessageBox, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    )
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

import src.utils.dxf as dxf
import src.arfdes.tools_airfoils as tools_airfoils
from src.arfdes.tools_airfoils import Reference_load
from src.obj.objects2D import Airfoil

from datetime import date
import src.arfdes.fit_2_reference as fit_2_reference  # Import the fitting module
import src.globals as globals  # Import from globals.py
import src.arfdes.widget_airfoils as widget_airfoils
from src.arfdes.widget_description import TextDescription
import src.arfdes.tools_airfoils as tools

class MenuBar(QMenuBar):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, program=None, project=None, parent=None, time=None, program_info=None, airfoils_menu=None):
        super(MenuBar, self).__init__(parent)
        self.DEADALUS = program
        self.PROJECT = project
        self.main_window = parent
        self.time = time
        self.airfoils_menu = airfoils_menu
        self.logger = logging.getLogger(self.__class__.__name__)
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

        """Window menu creation"""
        windowMenu = self.addMenu('Window')

        self.airfoilWidgetAction = QAction('Airfoil Tree', self)
        self.airfoilWidgetAction.setCheckable(True)
        self.airfoilWidgetAction.setChecked(True)
        self.airfoilWidgetAction.triggered.connect(self.toggle_airfoil)

        self.parametersWidgetAction = QAction('Parameters Table', self)
        self.parametersWidgetAction.setCheckable(True)
        self.parametersWidgetAction.setChecked(True)
        self.parametersWidgetAction.triggered.connect(self.toggle_parameters)

        self.referenceWidgetAction = QAction('Reference Tree', self)
        self.referenceWidgetAction.setCheckable(True)
        self.referenceWidgetAction.setChecked(True)
        self.referenceWidgetAction.triggered.connect(self.toggle_reference)

        self.statisticsWidgetAction = QAction('Statistics Table', self)
        self.statisticsWidgetAction.setCheckable(True)
        self.statisticsWidgetAction.setChecked(True)
        self.statisticsWidgetAction.triggered.connect(self.toggle_statistics)

        self.descriptionWidgetAction = QAction('Description Widget', self)
        self.descriptionWidgetAction.setCheckable(True)
        self.descriptionWidgetAction.setChecked(True)
        self.descriptionWidgetAction.triggered.connect(self.toggle_description)

        self.loggerWidgetAction = QAction('Logger Console', self)
        self.loggerWidgetAction.setCheckable(True)
        self.loggerWidgetAction.setChecked(True)
        self.loggerWidgetAction.triggered.connect(self.toggle_logger)

        windowMenu.addAction(self.airfoilWidgetAction)
        windowMenu.addAction(self.parametersWidgetAction)
        windowMenu.addAction(self.referenceWidgetAction)
        windowMenu.addAction(self.statisticsWidgetAction)
        windowMenu.addAction(self.descriptionWidgetAction)
        windowMenu.addAction(self.loggerWidgetAction)

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
            self.logger.info("Creating new project...")
            # Reset the project components
            globals.PROJECT.newProject()
            widget_airfoils.refresh_tree(self.airfoils_menu)

    def openFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            globals.loadProject(fileName)
            self.logger.debug(f"Opened file '{fileName}'")
            widget_airfoils.refresh_tree(self.airfoils_menu)

    def saveFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            globals.saveProject(fileName)
            self.logger.debug(f"Saved file: {fileName}")
    
    def quitApp(self):
        msg = QMessageBox.question(self, "Exit program", "Do you really want to quit a program?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.logger.info("Exit")
            QApplication.quit()
    
    """Airfoil menu actions"""
    
    def newAirfoil(self):
        self.logger.info("Creating new airfoil")
        if self.main_window:  # Ensure main_window is set     
            self.airfoils_menu.add_airfoil('Airfoil', self.time, 'Airfoil created from scratch')

    def appendAirfoil(self):
        """load the airfoil data from a JSON format file."""
        self.logger.info("Appending airfoil...")
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Deadalus Airfoil Format (*.arf);;All Files (*)", options=options)

        if fileName:
            try:
                airfoil_obj, _ = tools_airfoils.load_airfoil_from_json(fileName)
                globals.PROJECT.project_airfoils.append(airfoil_obj)
                if airfoil_obj:
                    self.logger.debug(airfoil_obj)
                    self.airfoils_menu.add_airfoil_to_tree(airfoil_obj.infos['name'], airfoil_obj)
                    self.logger.info("Appending an airfoil was sucessful!")
            except TypeError:
                self.logger.error("Failed to append airfoil")

    def deleteAirfoil(self):
        self.logger.info("Deleting selected airfoil...")
        if self.airfoils_menu:  # Ensure main_window is set
            status, name = self.airfoils_menu.delete()
            if status == True and name:
                self.logger.info(f"Successfully deleted airfoil: {name}")
            else:
                self.logger.error("Failed to delete!")
            
    def saveAirfoil(self):
        """Save the airfoil data to a JSON format file."""
        self.logger.info("Saving selected airfoil...")
        selected_item = self.main_window.airfoils_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected
 
        # Find the corresponding airfoil object
        airfoil_index = self.main_window.airfoils_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        json_object = tools_airfoils.save_airfoil_to_json(airfoil_index)

        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "DEADALUS Airfoil Format (*.arf);;All Files (*)", options=options)
        if fileName:
            with open(f"{fileName}", "w") as outfile:
                outfile.write(json_object)
                self.logger.info(f"Saved file: {fileName}")
 
    def exportAirfoil(self):
        """Export the airfoil data to a DXF format file."""
        self.logger.info("Exporting selected airfoil...")
        selected_item = self.main_window.airfoils_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected
 
        # Find the corresponding airfoil object
        airfoil_index = self.main_window.airfoils_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection
        
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export File to DXF format", "", "DXF Format (*.dxf);;All Files (*)", options=options)
        if fileName:
            dxf.export_airfoil_to_dxf(airfoil_index, fileName)
            self.logger.info(f"Exported file: {fileName}")

    def renameAirfoil(self):
        """Rename currently selected airfoil."""
        self.logger.info("Renaming selected airfoil...")
        self.le = QLabel(self)
        selected_item = self.airfoils_menu.currentItem()
        if not selected_item:
            self.logger.warning("First select an airfoil")
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.airfoils_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            self.logger.error("No connection between selected airfoil and project airfoil")
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
        self.logger.info("Airfoil renamed")
    
    def flipAirfoil(self):
        """Flip the currently selected airfoil."""
        self.logger.info("Flipping selected airfoil...")
        selected_item = self.airfoils_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.airfoils_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        current_airfoil = self.PROJECT.project_airfoils[airfoil_index]

        flipped_airfoil = tools_airfoils.flip_airfoil_horizontally(current_airfoil)

        if flipped_airfoil:
            self.PROJECT.project_airfoils[airfoil_index] = flipped_airfoil
            self.logger.info(f"Airfoil {flipped_airfoil.infos['name']} flipped...")

    def editDescriptionAirfoil(self):
        """Edit the description of an airfoil."""
        self.logger.info("Editing selected airfoil description...")
        selected_item = self.airfoils_menu.currentItem()
        if not selected_item:
            self.logger.warning("First select an airfoil")
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.airfoils_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            self.logger.error("No connection between selected airfoil and project airfoil")
            return  # Invalid selection

        current_airfoil = self.PROJECT.project_airfoils[airfoil_index]

        dialog = TextDescription(self.main_window, current_airfoil)
        if dialog.exec_() == QDialog.Accepted:
            # Optionally, update the tree menu display
            selected_item.setText(0, f"{current_airfoil.infos['name']}*")
            self.logger.info("Airfoil description updated.")

        # Optionally, update the tree menu display
        selected_item.setText(0, f"{current_airfoil.infos['name']}*")

    def fit2ref(self):
        """Fit the currently selected airfoil in airfoils_menu to the reference_airfoil by optimizing its parameters."""
        self.logger.info("Opening Fit2Ref window...")
        # Get selected item and corresponding airfoil object
        selected_items = self.airfoils_menu.selectedItems()
        if not selected_items:
            self.logger.warning("No airfoil selected in the tree menu.")
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
            self.logger.warning("Selected airfoil object not found.")
            return None
        
        # Open the Fit2RefWindow dialog
        dlg = fit_2_reference.Fit2RefWindow(parent=self.main_window, current_airfoil=current_airfoil, reference_airfoil=self.main_window.reference_airfoil)
        dlg.exec_()

    def preferencesWindow(self):        
        """Open the preferences dialog."""
        self.logger.info("Open preferences window")
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
                self.logger.info("Show reference")
                options = QFileDialog.Options()
                fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
                if fileName:
                    self.logger.info(f"Opened file: {fileName}")
                    #AirfoilCoord, UP_points, DW_points, name = DataBase_load(fileName, os.getcwd())
                    referenceState = True
                    self.referenceStatus.emit(referenceState, fileName)
            else:
                self.logger.info("Hide reference")
                referenceState = False
                self.referenceStatus.emit(referenceState, None)

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
    
    def update_action_state(self, action, dock_widget):
        """Update the state of the given action based on the dock widget's visibility."""
        action.setChecked(dock_widget.isVisible())

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
