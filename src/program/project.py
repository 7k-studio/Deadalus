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
        self.DEADALUS = program
        self.name = None
        self.creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.description = "Project description"
        self.path = None  # Path to the project directory
        
        self.project_airfoils = []
        self.nominal_airfoils = []
        self.reference_airfoils = []

        self.project_components = []
        self.components_nominal = []

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
            txt = prep_json_data(self, self.DEADALUS.name, self.DEADALUS.version)
            self.logger.debug(txt)

            self.logger.info(f"Saved file: {self.path}")
        else:
            self.save_as()

    def save_as(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(None, "Save File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        
        if filePath:
            self.name = os.path.splitext(os.path.basename(filePath)[0])
            self.path = filePath

            self.modification_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txt = prep_json_data(self, self.DEADALUS.name, self.DEADALUS.version)
            self.logger.debug(txt)

        self.logger.info(f"Saved file as: {self.name} to location: {self.path}")

    def open(self):
        from src.arfdes.tools_airfoils import load_airfoil_from_json
        from src.utils.tools_program import convert_list_to_ndarray
        from src.obj.class_airfoil import Airfoil
        from src.obj.objects3D import Component, Wing, Segment  # Import the templates
        
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Deadalus Database Files (*.ddls);; All Files (*)", options=options)
        if fileName:
            warning_count = 0

            self.logger.info(f"Open archive project: {fileName}")
            # Open the JSON file directly (as saved by saveProject)
            with open(fileName, "r") as f:
                data = json.load(f)

            # Convert lists back to numpy arrays if needed
            data = convert_list_to_ndarray(data)

            if "Program" in data:
                if data["Program"].get("program version", self.DEADALUS.program_version):
                    file_version = data["Program"].get("program version", self.DEADALUS.program_version)
                    file_version = file_version.split("-")[0].split(".")
                    program_version = self.DEADALUS.program_version
                    program_version = program_version.split("-")[0].split(".")
                    if program_version[1] != file_version[1] or program_version[0] != file_version[0]:
                        self.logger.warning("Current program version is different from the saved version. Some features may not work as expected. \nMissing parameters will take default values.")
                        warning_count += 1

            # Restore PROJECT info
            if "Project" in data:
                proj = data["Project"]
                self.project_name = proj.get("project name", self.project_name)
                self.project_date = proj.get("creation date", self.project_date)
                self.project_description = proj.get("project description", self.project_description)
                self.project_path = proj.get("project path", self.project_path)
                self.project_components.clear()
                self.project_airfoils.clear()

                # Load airfoils from in-memory JSON (not from files)
                airfoil_entries = proj.get("project airfoils", [])
                for idx, airfoil_entry in enumerate(airfoil_entries):
                    # airfoil_entry: {"id": ..., "data": {...}}
                    airfoil_data = airfoil_entry.get("data", {})
                    airfoil_json = airfoil_data.get("airfoil", {})

                    airfoil_obj = Airfoil()
                    airfoil_obj.id = airfoil_entry.get("id", 'Unknown')
                    airfoil_obj.infos = airfoil_json.get("infos", {})
                    airfoil_obj.params = airfoil_json.get("params", {})
                    self.project_airfoils.append(airfoil_obj)

                # Load components using templates
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

                            # Set airfoil_index based on airfoil ID string
                            airfoil_ref = seg_data.get("airfoil", "")
                            if airfoil_ref.startswith("airfoil_"):
                                try:
                                    airfoil_index = int(airfoil_ref.split("_")[1])
                                    segment.airfoil = self.project_airfoils[airfoil_index]
                                except Exception:
                                    segment.airfoil = self.project_airfoils[0]
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
                report.insert(0, (f"Project archive '{base_name}' successfully loaded")) 
            else: 
                report.insert(0, (f"Project archive '{base_name}' loaded with ({warning_count}) warnings, check might be necessary!"))
                
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

PROJECT = Project()  # Create a global instance of Project

def prep_json_data(project, Program_name, Program_version):
    from src.arfdes.tools_airfoils import save_airfoil_to_json
    from src.utils.tools_program import convert_ndarray_to_list

    designed_components = []

    # Collect all airfoils in one list with IDs
    airfoil_entries = []
    for idx, arf_obj in enumerate(project.project_airfoils):

        airfoil_data = save_airfoil_to_json(arf_obj)  # serialized JSON string
        airfoil_json = json.loads(airfoil_data)   # parse to dict
        
        arf_obj.id = f"airfoil_{idx}"
        airfoil_entries.append({
            "id": f"airfoil_{idx}",
            "data": airfoil_json
        })

    # Build components → wings → segments
    for component in project.project_components:
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
                    "airfoil": segment.airfoil.id,  # link by ID
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

    Deadalus = {
        "program name": DEADALUS.program_name,
        "program version": DEADALUS.program_version,
    }

    Project = {
        "project name": project.name,
        "creation date": project.creation_date,
        "modification date": project.modification_date,
        "project description": project.project_description,
        "project path": project.path,
        "project components": designed_components,
        "project airfoils": airfoil_entries
    }

    data = {
        "Program": Deadalus,
        "Project": Project
    }

    # Convert numpy arrays to lists before saving
    data = convert_ndarray_to_list(data)

    # Save into one .ddls file
    with open(project.path, "w") as f:
        json.dump(data, f, indent=2)

    return 'Project archive successfully saved'