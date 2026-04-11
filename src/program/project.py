'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.

'''

# Library imports
import re
import logging
import json
import tempfile
import shutil
import tarfile
import struct
import os
import numpy as np

# PyQt imports
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QTextEdit
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

# In-Program imports
# import src.obj.objects3D as objects3D
from src.utils.tools_program import new_id

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

import src.arfdes.tools_airfoils as tools_airfoils
from src.arfdes.tools_airfoils import Reference_load

import datetime
import src.arfdes.fit_2_reference as fit_2_reference  # Import the fitting module
import src.arfdes.widget_airfoils as widget_airfoils
from src.arfdes.widget_description import TextDescription
import src.arfdes.tools_airfoils as tools

class Project:
    def __init__(self, program=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.name = None
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.description = "Project description"
        self.path = None  # Path to the project directory
        
        self.airfoils = []
        self.nominal_airfoils = []
        self.reference_airfoils = []

        self.components = []
        self.nominal_components = []

    def new(self):
        """Create a new project."""
        msg = QMessageBox.question(None, "New Project", "Do you want to create a new project?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.logger.info("Creating new project...")
            # Reset the project components
            
            self.name = None
            self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.description = "New project created"
            self.path = None  # Set the path to the project directory
            self.project_components.clear()
            self.project_airfoils.clear()

    def save(self):
        if self.name != None and self.path != None:

            self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txt = self._prep_json_data(self, self.DAEDALUS.name, self.DAEDALUS.version)
            self.logger.debug(txt)

            self.logger.info(f"Saved file: {self.path}")
        else:
            self.save_as()

    def save_as(self):
        options = QFileDialog.Options()
        default_name = f"{self.name}.ddls" if self.name else f"Untitled.ddls"
        filePath, _ = QFileDialog.getSaveFileName(None, "Save File", default_name, "Daedalus Database Files (*.ddls);; All Files (*)", options=options)
        print('filepath', filePath)
        print('_', _)
        if filePath:
            self.name = os.path.basename(filePath).split('.')[0]
            self.path = filePath

            self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txt = self._prep_json_data()
            self.logger.debug(txt)

        self.logger.info(f"Saved file as: {self.name} to location: {self.path}")

    def open(self):
        from src.arfdes.tools_airfoils import load_airfoil_from_json
        from src.utils.tools_program import convert_list_to_ndarray
        from src.obj.class_airfoil import Airfoil
        from src.obj.objects3D import Component, Wing, Segment  # Import the templates
        
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Daedalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            warning_count = 0

            self.logger.info(f"Open archive project: {fileName}")
            # Open the JSON file directly (as saved by saveProject)
            with open(fileName, "r") as f:
                data = json.load(f)

            # Convert lists back to numpy arrays if needed
            data = convert_list_to_ndarray(data)

            if "Program" in data:
                if data["Program"].get("program version", self.DAEDALUS.version):
                    file_version = data["Program"].get("program version", self.DAEDALUS.version)
                    file_version = file_version.split("-")[0].split(".")
                    program_version = self.DAEDALUS.version
                    program_version = program_version.split("-")[0].split(".")
                    if program_version[1] != file_version[1] or program_version[0] != file_version[0]:
                        self.logger.warning("Current program version is different from the saved version. Some features may not work as expected. \nMissing parameters will take default values.")
                        warning_count += 1

            # Restore PROJECT info
            if "Project" in data:
                self.logger.debug("Loading data")
                proj = data["Project"]
                self.name = proj.get("project name", self.name)
                self.creation_date = proj.get("creation date", self.creation_date)
                self.description = proj.get("project description", self.description)
                self.path = proj.get("project path", self.path)
                self.project_components.clear()
                self.project_airfoils.clear()

                # Load airfoils from in-memory JSON (not from files)
                self.logger.debug("Loading airfoil entires...")
                airfoil_entries = proj.get("project airfoils", [])
                for airfoil_entry in airfoil_entries:
                    airfoil_data = airfoil_entry["data"]
                    arf_obj = load_airfoil_from_json(airfoil_data)
                    self._ensure_unique_name(arf_obj)  # Ensure unique name in case of conflicts
                    self.project_airfoils.append(arf_obj)
                    self.logger.debug(f"Found airfoil: {arf_obj.name}")

                # Load components using templates
                self.logger.debug("Loading components entires...")
                for comp_data in proj.get("project components", []):
                    component = Component()
                    # Merge infos and params with defaults
                    component.infos = {**Component().infos, **comp_data.get("infos", {})}
                    component.params = {**Component().params, **comp_data.get("params", {})}
                    component.wings = []
                    for wing_data in comp_data.get("wings", []):
                        wing = Wing()
                        wing.infos = {**Wing().infos, **wing_data.get("infos", {})}
                        wing.params = {**Wing().params, **wing_data.get("params", {})}
                        wing.segments = []
                        for seg_data in wing_data.get("segments", []):
                            segment = Segment()
                            segment.infos = {**Segment().infos, **seg_data.get("infos", {})}
                            segment.anchor = seg_data.get("anchor", Segment().anchor)
                            segment.params = {**Segment().params, **seg_data.get("params", {})}

                            # Set airfoil based on airfoil name
                            airfoil_ref = seg_data.get("airfoil", "")
                            segment.airfoil = next((a for a in self.project_airfoils if a.name == airfoil_ref), self.project_airfoils[0] if self.project_airfoils else None)
                            wing.segments.append(segment)
                        component.wings.append(wing)
                    self.project_components.append(component)

            airf_no = 0
            comp_no = 0
            wing_no = 0
            segm_no = 0
            objects_updated = 0

            for airfoil in self.project_airfoils:
                airf_no += 1
            for component in self.project_components:
                for wing in component.wings:
                    for segment in wing.segments:
                        segm_no += 1
                    wing_no += 1
                comp_no += 1

            objects_to_update = comp_no + wing_no + segm_no + airf_no
            report = [
            ("Objects found inside saved file:\n"),
            (f"----------------------"),
            (f"|   LOADED OBJECTS   |"),
            (f"----------------------"),
            (f"|   Components:   {comp_no}  |"),
            (f"|   Wings:        {wing_no}  |"),
            (f"|   Segments:     {segm_no}  |"),
            (f"|   Airfoils:     {airf_no}  |"),
            (f"----------------------"),
            (f"|  ALL OBJECTS:   {objects_to_update}  |"),
            (f"----------------------")]

            self.logger.info(f"Rebuilidng geometries...")

            for airfoil in self.project_airfoils:
                airfoil.update()
                objects_updated += 1
                self.logger.debug(f"{objects_updated} / {objects_to_update}")
            for c in range(len(self.project_components)):
                component = self.project_components[c]
                for w in range(len(component.wings)):
                    wing = component.wings[w]
                    for s in range(len(wing.segments)):
                        segment = wing.segments[s]
                        segment.airfoil.update()
                        segment.update(c, w, s)
                        objects_updated += 1
                        self.logger.debug(f"{objects_updated} / {objects_to_update}")
                    wing.update(c, w, s)
                    objects_updated += 1
                    self.logger.debug(f"{objects_updated} / {objects_to_update}")
                component.update(c, w, s)
                objects_updated += 1
                self.logger.debug(f"{objects_updated} / {objects_to_update}")
            self.logger.debug("Update finished!")

            if warning_count == 0:
                report.insert(0, (f"Project archive '{self.name}' successfully loaded")) 
            else: 
                report.insert(0, (f"Project archive '{self.name}' loaded with ({warning_count}) warnings, check might be necessary!"))
                
            self.logger.info("\n".join(report))

            return True

    def edit_description(self):
        """Edit the description of the project. Using pop-up TextArea Widget with two buttons: Save and Cance"""
        self.logger.info("Editing description of the project...")
        
        # Create a dialog with text area
        dialog = QDialog()
        dialog.setWindowTitle("Edit Project Description")
        dialog.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        # Create text edit widget
        text_edit = QTextEdit()
        text_edit.setText(self.description if hasattr(self, 'description') else "")
        layout.addWidget(text_edit)
        
        # Create buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # Connect buttons
        def on_save():
            self.description = text_edit.toPlainText()
            self.logger.info("Project description updated.")
            dialog.accept()
        
        def on_cancel():
            dialog.reject()
        
        save_button.clicked.connect(on_save)
        cancel_button.clicked.connect(on_cancel)
        
        dialog.exec_()

    def _ensure_unique_name(self, airfoil):
        """Ensure the airfoil has a unique name by appending a number if necessary."""
        base_name = airfoil.name
        counter = 1
        existing_names = [a.name for a in self.airfoils if a is not airfoil]
        while airfoil.name in existing_names:
            airfoil.name = f"{base_name}.{str(counter).zfill(3)}"
            counter += 1
                    
    def _prep_json_data(self):
        from src.arfdes.tools_airfoils import save_airfoil_to_json
        from src.utils.tools_program import convert_ndarray_to_list

        designed_components = []

        # Collect all airfoils in one list with names
        airfoil_entries = []
        for arf_obj in self.airfoils:

            airfoil_data = save_airfoil_to_json(arf_obj, self, self.DAEDALUS)  # serialized JSON string
            airfoil_json = json.loads(airfoil_data)   # parse to dict
            
            airfoil_entries.append({
                "airfoil": airfoil_json
            })

        # Build components → wings → segments
        for component in self.project_components:
            designed_wings = []
            for wing in component.wings:
                designed_segments = []
                for segment in wing.segments:
                    infos = {
                        "name": segment.infos.get('name', 'Unknown'),
                        "creation_date": segment.infos.get('creation_date', 'Unknown'),
                        "modification_date": segment.infos.get('modification_date', 'Unknown'),
                    }
                    params = {
                        "origin_X": segment.params.get('origin_X', 0),
                        "origin_Y": segment.params.get('origin_Y', 0),
                        "origin_Z": segment.params.get('origin_Z', 0),
                        "incidence": segment.params.get('incidence', 0),
                        "scale": segment.params.get('scale', 1.0),
                        "tan_accel": segment.params.get('tan_accel', 0.1),
                    }

                    segments = {
                        "infos": infos,
                        "airfoil": segment.airfoil.name,  # link by name
                        "anchor": segment.anchor,
                        "params": params,
                    }
                    designed_segments.append(segments)

                infos = {
                    "name": wing.infos.get('name', 'Unknown'),
                    "creation_date": wing.infos.get('creation_date', 'Unknown'),
                    "modification_date": wing.infos.get('modification_date', 'Unknown'),
                }
                params = {
                    "origin_X": wing.params.get('origin_X', 0),
                    "origin_Y": wing.params.get('origin_Y', 0),
                    "origin_Z": wing.params.get('origin_Z', 0),
                }

                wings = {
                    "infos": infos,
                    "params": params,
                    "segments": designed_segments,
                }
                designed_wings.append(wings)

            infos = {
                "name": component.infos.get('name', 'Unknown'),
                "creation_date": component.infos.get('creation_date', 'Unknown'),
                "modification_date": component.infos.get('modification_date', 'Unknown'),
            }
            params = {
                "origin_X": component.params.get('origin_X', 0),
                "origin_Y": component.params.get('origin_Y', 0),
                "origin_Z": component.params.get('origin_Z', 0),
            }

            components = {
                "infos": infos,
                "params": params,
                "wings": designed_wings
            }
            designed_components.append(components)

        Daedalus = {
            "program name": self.DAEDALUS.name,
            "program version": self.DAEDALUS.version,
        }

        Project = {
            "name": self.name,
            "creation date": self.creation_date,
            "modification date": self.modification_date,
            "description": self.description,
            "path": self.path,
            "components": designed_components,
            "airfoils": airfoil_entries
        }

        data = {
            "Program": Daedalus,
            "Project": Project
        }

        # Convert numpy arrays to lists before saving
        data = convert_ndarray_to_list(data)

        # Save into one .ddls file
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

        return 'Project archive successfully saved'