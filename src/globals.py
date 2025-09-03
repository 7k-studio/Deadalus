'''

Copyright (C) 2025 Jakub Kamyk

This file is part of AirFLOW.

AirFLOW is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

AirFLOW is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AirFLOW.  If not, see <http://www.gnu.org/licenses/>.

'''

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
        self.program_name = "AirFLOW"
        self.program_version = "0.2.0-beta"

        self.preferences = {
            'general': {
                "units": "meters / degrees", # Options: "meters / radians", (future: "milimeters / degrees", "feet / degrees")
                "performance": "normal",  # Options: "normal", "fast", "good"
                "beta_features": False,  # Enable beta features
            },
            'airfoil_designer': {
                "show_grid": True,
                "show_control_points": True,
                "show_construction": True,
                "wireframe_color": {'le': [0.0, 0.0, 1.0], 'te': [1.0, 1.0, 0.0], 'ps': [0.0, 1.0, 0.0], 'ss': [1.0, 0.0, 0.0]}
            },
            'wing_designer': {
                "show_grid": True,
                "show_ruler": True,
                "show_control_points": True,
                "show_construction": True,
                "show_wireframe": True,
                "show_solid": True,
                "wireframe_color": {'le': [0.0, 0.0, 1.0], 'te': [1.0, 1.0, 0.0], 'ps': [0.0, 1.0, 0.0], 'ss': [1.0, 0.0, 0.0], 'le_ps': [0.0, 1.0, 0.0], 'le_ss': [1.0, 0.0, 0.0], 'te_ps': [0.0, 1.0, 0.0], 'te_ss': [1.0, 0.0, 0.0]}
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
                #print("Preferences loaded successfully.")
        except FileNotFoundError:
            print("AIRFLOW > Preferences file not found. Using default settings.")
        except json.JSONDecodeError:
            print("ERROR: decoding preferences file. Using default settings.")

    def showAboutDialog(self, parent=None):
        dialog = QDialog(parent)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(400, 250)

        # Logo
        logo_label = QLabel(dialog)
        pixmap = QPixmap("src/assets/text_logo.png")
        logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)

        copyright_label = QLabel('Copyright (C) 2025 Jakub Kamyk')
        copyright_label.setFont(QFont("Arial", 8))
        copyright_label.setAlignment(Qt.AlignCenter)

        version_label = QLabel(f"Version: {self.program_version}")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignCenter)

        # Optional description
        description_label = QLabel("AirFLOW is a program for parametricaly designing airfoils and wings.")
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
        self.project_name = "Project"
        self.project_date = date.today().strftime("%Y-%m-%d")
        self.project_description = "Project description"
        self.project_path = ""  # Path to the project directory
        self.project_components = []
        self.project_airfoils = []

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

def write_chunk(f, chunk_type: str, data: dict):
    """Write one chunk with type (4 chars), size (uint32), and JSON payload."""
    payload = json.dumps(data).encode("utf-8")
    f.write(chunk_type.encode("ascii"))
    f.write(struct.pack("<I", len(payload)))
    f.write(payload)

def saveProject(fileName):
    from src.arfdes.tools_airfoil import save_airfoil_to_json
    from src.utils.tools_program import convert_ndarray_to_list

    base_path = fileName if fileName.endswith(".afdb") else fileName + ".afdb"
    if os.path.exists(base_path):
        os.remove(base_path)

    with open(base_path, "wb") as f:
        # --- Save airfoils ---
        airfoil_ids = []
        for idx, airfoil in enumerate(PROJECT.project_airfoils):
            airfoil_id = new_id()
            airfoil_data = {
                "id": airfoil_id,
                "infos": airfoil.infos,
                "params": airfoil.params,
            }
            write_chunk(f, "AIFO", convert_ndarray_to_list(airfoil_data))
            airfoil_ids.append(airfoil_id)

        # --- Save components / wings / segments ---
        for comp_idx, component in enumerate(PROJECT.project_components):
            comp_id = new_id()
            comp_data = {
                "id": comp_id,
                "infos": component.infos,
                "params": component.params,
            }
            write_chunk(f, "COMP", convert_ndarray_to_list(comp_data))

            for wing_idx, wing in enumerate(component.wings):
                wing_id = new_id()
                wing_data = {
                    "id": wing_id,
                    "parent_id": comp_id,
                    "infos": wing.infos,
                    "params": wing.params,
                }
                write_chunk(f, "WING", convert_ndarray_to_list(wing_data))

                for seg_idx, segment in enumerate(wing.segments):
                    seg_id = new_id()
                    seg_data = {
                        "id": seg_id,
                        "parent_id": wing_id,
                        "infos": segment.infos,
                        "params": segment.params,
                        "anchor": segment.anchor,
                        "airfoil_ref": airfoil_ids[getattr(segment, "airfoil_index", 0)]
                    }
                    write_chunk(f, "SEGM", convert_ndarray_to_list(seg_data))

        # --- Save global project metadata ---
        AirFLOW_meta = {
            "program name": AIRFLOW.program_name,
            "program version": AIRFLOW.program_version,
            "file name": os.path.basename(fileName),
        }
        Project_meta = {
            "project name": PROJECT.project_name,
            "creation date": PROJECT.project_date,
            "modification date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project description": PROJECT.project_description,
        }
        meta = {"Program": AirFLOW_meta, "Project": Project_meta}
        write_chunk(f, "PROJ", convert_ndarray_to_list(meta))

    print("AIRFLOW > Project database successfully saved:", base_path)
    return base_path

def loadProjectold(fileName):

    from src.arfdes.tools_airfoil import load_airfoil_from_json
    from src.utils.tools_program import convert_list_to_ndarray
    from obj.objects3D import Component, Wing, Segment  # Import the templates
    base_name = os.path.basename(fileName)
    warning_count = 0

    print(f"AIRFLOW > open archive project: {base_name}")
    # Extract archive to a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        with tarfile.open(fileName, "r:gz") as tar:
            tar.extractall(path=tmpdir)

        # Load project.airflow
        project_json_path = os.path.join(tmpdir, "project.airflow")
        with open(project_json_path, "r") as f:
            data = json.load(f)

        # Convert lists back to numpy arrays if needed
        data = convert_list_to_ndarray(data)

        if "Program" in data:
            if data["Program"].get("program version", AIRFLOW.program_version):
                file_version = data["Program"].get("program version", AIRFLOW.program_version)
                file_version = file_version.split("-")[0].split(".")
                program_version = AIRFLOW.program_version
                program_version = program_version.split("-")[0].split(".")
                if program_version[1] != file_version[1] or program_version[0] != file_version[0]:
                    print("WARNING: Current program version is different from the saved version. Some features may not work as expected. \nMissing parameters will take default values.")
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

            # Load airfoils
            airfoil_filenames = proj.get("project airfoils", [])
            for idx, airfoil_filename in enumerate(airfoil_filenames):
                airfoil_path = os.path.join(tmpdir, airfoil_filename)
                airfoil_obj, warning = load_airfoil_from_json(airfoil_path)
                warning_count += warning
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
                    wing.geom = {**Wing().geom, **wing_data.get("geom", {})}
                    wing.segments = []
                    for seg_data in wing_data.get("segments", []):
                        segment = Segment()
                        segment.infos = {**Segment().infos, **seg_data.get("infos", {})}
                        segment.anchor = seg_data.get("anchor", Segment().anchor)
                        segment.params = {**Segment().params, **seg_data.get("params", {})}
                        segment.control_points = {**Segment().control_points, **seg_data.get("control_points", {})}
                        segment.geom = {**Segment().geom, **seg_data.get("geom", {})} if "geom" in seg_data else dict(Segment().geom)
                        # Optionally, set airfoil_index if needed
                        airfoil_ref = seg_data.get("airfoil", "")
                        if airfoil_ref.startswith("airfoil_") and airfoil_ref.endswith(".arf"):
                            try:
                                segment.airfoil_index = int(airfoil_ref.split("_")[1].split(".")[0])
                            except Exception:
                                segment.airfoil_index = 0
                        wing.segments.append(segment)
                    component.wings.append(wing)
                PROJECT.project_components.append(component)

    if warning_count == 0:
        print(f"AIRFLOW > Project archive '{base_name}' successfully loaded")
    else: 
        print(f"AIRFLOW > Project archive '{base_name}' loaded with ({warning_count}) warnings, check might be necessary!")
    return True

def read_chunks(file_path):
    """Generator: yields (chunk_type, parsed_json_obj)."""
    with open(file_path, "rb") as f:
        while True:
            header = f.read(8)
            if not header:
                break
            chunk_type, length = struct.unpack("<4sI", header)
            data = f.read(length)
            yield chunk_type.decode("ascii"), json.loads(data.decode("utf-8"))

def loadProject(fileName):

    file_path = fileName if fileName.endswith(".afdb") else fileName + ".afdb"
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No project file found: {file_path}")

    # Reset project state
    PROJECT.project_airfoils.clear()
    PROJECT.project_components.clear()

    # Collect objects by ID
    airfoils, segments, wings, components = {}, {}, {}, {}
    project_meta = {}

    for ctype, obj in read_chunks(file_path):
        if ctype == "AIFO":
            airfoils[obj["id"]] = obj
        elif ctype == "SEGM":
            segments[obj["id"]] = obj
        elif ctype == "WING":
            wings[obj["id"]] = obj
        elif ctype == "COMP":
            components[obj["id"]] = obj
        elif ctype == "PROJ":
            project_meta = obj

    # --- Rebuild hierarchy ---
    # Link segments to wings
    for seg in segments.values():
        wing = wings.get(seg["parent_id"])
        if wing:
            wing.setdefault("segments", []).append(seg)

    # Link wings to components
    for wing in wings.values():
        comp = components.get(wing["parent_id"])
        if comp:
            comp.setdefault("wings", []).append(wing)

    # Attach components to PROJECT
    for comp in components.values():
        comp_obj = objects3D.Component()
        comp_obj.infos = comp.get("infos", {})
        comp_obj.params = comp.get("params", {})

        for wing in comp.get("wings", []):
            wing_obj = objects3D.Wing()
            wing_obj.infos = wing.get("infos", {})
            wing_obj.params = wing.get("params", {})
            wing_obj.geom = wing.get("geom", {})

            for seg in wing.get("segments", []):
                seg_obj = objects3D.Segment()
                seg_obj.infos = seg.get("infos", {})
                seg_obj.params = seg.get("params", {})
                seg_obj.anchor = seg.get("anchor", None)
                seg_obj.airfoil_index = list(airfoils.keys()).index(seg.get("airfoil_ref"))
                wing_obj.segments.append(seg_obj)

            comp_obj.wings.append(wing_obj)

        PROJECT.project_components.append(comp_obj)

    # Restore airfoils
    for aifo in airfoils.values():
        arf_obj = objects2D.Airfoil()
        arf_obj.infos = aifo.get("infos", {})
        arf_obj.params = aifo.get("params", {})
        PROJECT.project_airfoils.append(arf_obj)

    # Restore metadata
    if "Program" in project_meta:
        prog = project_meta["Program"]
        AIRFLOW.program_name = prog.get("program name", AIRFLOW.program_name)
        AIRFLOW.program_version = prog.get("program version", AIRFLOW.program_version)

    if "Project" in project_meta:
        proj = project_meta["Project"]
        PROJECT.project_name = proj.get("project name", PROJECT.project_name)
        PROJECT.project_date = proj.get("creation date", PROJECT.project_date)
        PROJECT.project_description = proj.get("project description", PROJECT.project_description)

    print(f"AIRFLOW > Project successfully loaded from {file_path}")
    return PROJECT


AIRFLOW = Program()  # Create a global instance of Program
PROJECT = Project()  # Create a global instance of Project