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
from datetime import date
import json
import tempfile
import shutil
import tarfile
import struct
import os
import uuid
import datetime
import numpy as np  # Add this import for numpy
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import webbrowser
import src.obj.objects3D as objects3D
import src.obj.objects2D as objects2D

class Program:
    def __init__(self):
        self.program_name = "Deadalus"
        self.program_version = "0.3.1-beta"
        self.logger = logging.getLogger(self.__class__.__name__)

        self.preferences = {
            'general': {
                "units": {
                    "length": "m",
                    "angle":  "rad"
                }, # Options: "meters / radians", (future: "milimeters / degrees", "feet / degrees")
                "performance": 50,  # Options: 10 - 100
                "beta_features": False,  # Enable beta features
            },
            'airfoil_designer': {
                "viewport":{
                    "grid":{
                        "show": True
                    },
                    "ruler": {
                        "show": True
                    },
                },
                "airfoil": {
                    "control_points": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0],
                            'te': [1.0, 0.8, 0.2],
                            'ps': [0.0, 1.0, 0.0],
                            'ss': [1.0, 0.0, 0.0]
                        }
                    },
                    "construction": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0],
                            'te': [1.0, 0.8, 0.2],
                            'ps': [0.0, 1.0, 0.0],
                            'ss': [1.0, 0.0, 0.0]
                        }
                    },
                    "wireframe": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0],
                            'te': [1.0, 0.8, 0.2],
                            'ps': [0.0, 1.0, 0.0],
                            'ss': [1.0, 0.0, 0.0]
                        }
                    }
                }
            },
            'wing_designer': {
                "viewport": {
                    "grid": {
                        "show": True,
                    },
                    "ruller": {
                        "show": True,
                    }
                },
                "wing": {
                    "grid": {
                        "show": True
                    },
                    "wireframe": {
                        "show": True,
                        "color": {
                            'le': [0.0, 0.0, 1.0], 
                            'te': [1.0, 1.0, 0.0], 
                            'ps': [0.0, 1.0, 0.0], 
                            'ss': [1.0, 0.0, 0.0], 
                            'le_ps': [0.0, 1.0, 0.0], 
                            'le_ss': [1.0, 0.0, 0.0], 
                            'te_ps': [0.0, 1.0, 0.0], 
                            'te_ss': [1.0, 0.0, 0.0]},
                    },
                    "solid":{         
                        "show": True},
                }
            }
        }
        self.readPreferences()  # Load preferences from file

    def readPreferences(self):
        """Read preferences from a JSON file."""
        try:
            with open("src/settings", "r") as infile:
                loaded = json.load(infile)
                # Only update keys that exist in the default preferences
                for section in self.preferences:
                    if section in loaded and isinstance(loaded[section], dict):
                        self.preferences[section].update(loaded[section])
                self.logger.info("Preferences loaded successfully.")
        except FileNotFoundError:
            self.logger.warning("Preferences file not found. Using default settings.")
        except json.JSONDecodeError:
            self.logger.error("Decoding preferences file. Using default settings.")

    def showAboutDialog(self, parent=None):
        dialog = QDialog(parent)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(400, 250)

        # Logo
        logo_label = QLabel(dialog)
        #pixmap = QPixmap("src/assets/text_logo.png")
        #logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)

        copyright_label = QLabel('Copyright (C) 2025 Jakub Kamyk')
        copyright_label.setFont(QFont("Arial", 8))
        copyright_label.setAlignment(Qt.AlignCenter)

        version_label = QLabel(f"Version: {self.program_version}")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignCenter)

        # Optional description
        description_label = QLabel("DEADALUS is a program for parametricaly designing airfoils and wings.")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        close_button.setFixedWidth(100)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(logo_label)
        layout.addWidget(copyright_label)
        layout.addWidget(version_label)
        layout.addWidget(description_label)

        bottom_layout = QHBoxLayout()
        bottom_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        bottom_layout.addWidget(close_button)
        bottom_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        layout.addLayout(bottom_layout)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def showUserManual(self):
        file_path = os.path.abspath("src/assets/user_manual.html")
        webbrowser.open(f"file://{file_path}")

class Project:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.project_name = "Project"
        self.project_date = date.today().strftime("%Y-%m-%d")
        self.project_description = "Project description"
        self.project_path = ""  # Path to the project directory
        
        self.project_airfoils = []
        self.airfoils_nominal = []

        self.project_components = []
        self.components_nominal = []

    def newProject(self):
        """Create a new project."""
        self.project_name = "Project"
        self.project_date = date.today().strftime("%Y-%m-%d")
        self.project_description = "New project created"
        self.project_path = ""  # Set the path to the project directory
        self.project_components.clear()
        self.project_airfoils.clear()
    
def new_id():
    return str(uuid.uuid4())

def saveProject(fileName):
    from src.arfdes.tools_airfoil import save_airfoil_to_json
    from src.utils.tools_program import convert_ndarray_to_list

    designed_components = []

    # Collect all airfoils in one list with IDs
    airfoil_entries = []
    for idx, _ in enumerate(PROJECT.project_airfoils):
        airfoil_data = save_airfoil_to_json(idx)  # serialized JSON string
        airfoil_json = json.loads(airfoil_data)   # parse to dict
        PROJECT.project_airfoils[idx].id = f"airfoil_{idx}"
        airfoil_entries.append({
            "id": f"airfoil_{idx}",
            "data": airfoil_json
        })

    # Build components → wings → segments
    for component in PROJECT.project_components:
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
        "file name": os.path.basename(fileName),
    }

    Project = {
        "project name": PROJECT.project_name,
        "creation date": PROJECT.project_date,
        "modification date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project description": PROJECT.project_description,
        "project path": fileName,
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
    with open(fileName, "w") as f:
        json.dump(data, f, indent=2)

    PROJECT.logger.info("Project archive successfully saved")

def loadProject(fileName):
    from src.arfdes.tools_airfoil import load_airfoil_from_json
    from src.utils.tools_program import convert_list_to_ndarray
    from src.obj.objects3D import Component, Wing, Segment  # Import the templates
    base_name = os.path.basename(fileName)
    warning_count = 0

    PROJECT.logger.info(f"Open archive project: {fileName}")
    # Open the JSON file directly (as saved by saveProject)
    with open(fileName, "r") as f:
        data = json.load(f)

    # Convert lists back to numpy arrays if needed
    data = convert_list_to_ndarray(data)

    if "Program" in data:
        if data["Program"].get("program version", DEADALUS.program_version):
            file_version = data["Program"].get("program version", DEADALUS.program_version)
            file_version = file_version.split("-")[0].split(".")
            program_version = DEADALUS.program_version
            program_version = program_version.split("-")[0].split(".")
            if program_version[1] != file_version[1] or program_version[0] != file_version[0]:
                PROJECT.logger.warning("Current program version is different from the saved version. Some features may not work as expected. \nMissing parameters will take default values.")
                warning_count += 1

    # Restore PROJECT info
    if "Project" in data:
        proj = data["Project"]
        PROJECT.project_name = proj.get("project name", PROJECT.project_name)
        PROJECT.project_date = proj.get("creation date", PROJECT.project_date)
        PROJECT.project_description = proj.get("project description", PROJECT.project_description)
        PROJECT.project_path = proj.get("project path", PROJECT.project_path)
        PROJECT.project_components.clear()
        PROJECT.project_airfoils.clear()

        # Load airfoils from in-memory JSON (not from files)
        airfoil_entries = proj.get("project airfoils", [])
        for idx, airfoil_entry in enumerate(airfoil_entries):
            # airfoil_entry: {"id": ..., "data": {...}}
            airfoil_data = airfoil_entry.get("data", {})
            airfoil_json = airfoil_data.get("airfoil", {})

            airfoil_obj = objects2D.Airfoil()
            airfoil_obj.id = airfoil_entry.get("id", 'Unknown')
            airfoil_obj.infos = airfoil_json.get("infos", {})
            airfoil_obj.params = airfoil_json.get("params", {})
            PROJECT.project_airfoils.append(airfoil_obj)

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
                            segment.airfoil = PROJECT.project_airfoils[airfoil_index]
                        except Exception:
                            segment.airfoil = PROJECT.project_airfoils[0]
                    wing.segments.append(segment)
                component.wings.append(wing)
            PROJECT.project_components.append(component)

    airf_no = 0
    comp_no = 0
    wing_no = 0
    segm_no = 0
    objects_updated = 0

    for airfoil in PROJECT.project_airfoils:
        airf_no += 1
    for component in PROJECT.project_components:
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

    PROJECT.logger.info(f"Rebuilidng geometries...")

    for airfoil in PROJECT.project_airfoils:
        airfoil.update()
        objects_updated += 1
        PROJECT.logger.debug(f"{objects_updated} / {objects_to_update}")
    for c in range(len(PROJECT.project_components)):
        component = PROJECT.project_components[c]
        for w in range(len(component.wings)):
            wing = component.wings[w]
            for s in range(len(wing.segments)):
                segment = wing.segments[s]
                segment.airfoil.update()
                segment.update(c, w, s)
                objects_updated += 1
                PROJECT.logger.debug(f"{objects_updated} / {objects_to_update}")
            wing.update(c, w, s)
            objects_updated += 1
            PROJECT.logger.debug(f"{objects_updated} / {objects_to_update}")
        component.update(c, w, s)
        objects_updated += 1
        PROJECT.logger.debug(f"{objects_updated} / {objects_to_update}")
    PROJECT.logger.debug("Update finished!")

    if warning_count == 0:
        report.insert(0, (f"Project archive '{base_name}' successfully loaded")) 
    else: 
        report.insert(0, (f"Project archive '{base_name}' loaded with ({warning_count}) warnings, check might be necessary!"))
        
    PROJECT.logger.info("\n".join(report))

    return True

DEADALUS = Program()  # Create a global instance of Program
PROJECT = Project()  # Create a global instance of Project