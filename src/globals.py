from datetime import date
import json
import tempfile
import tarfile
import os
import datetime
import numpy as np  # Add this import for numpy

class Program:
    def __init__(self):
        self.program_name = "AirFLOW"
        self.program_version = "0.2.4-beta"

        self.preferences = {
            'general': {
                "units": "meters / degrees", # Options: "meters / radians", (future: "milimeters / degrees", "feet / degrees")
                "performance": "normal",  # Options: "normal", "fast", "slow"
                "beta_features": False,  # Enable beta features
            },
            'airfoil_designer': {
                "show_grid": True,
                "show_control_points": True,
                "show_construction": True,
            },
            'wing_designer': {
                "show_grid": True,
                "show_ruler": True,
                "show_control_points": True,
                "show_construction": True,
                "show_wireframe": True,
                "show_solid": True
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
                print("Preferences loaded successfully.")
        except FileNotFoundError:
            print("Preferences file not found. Using default settings.")
        except json.JSONDecodeError:
            print("Error decoding preferences file. Using default settings.")

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
    
def saveProject(fileName):
    from src.arfdes.tools_airfoil import save_airfoil_to_json
    from src.utils.tools_program import convert_ndarray_to_list

    # Create a temporary directory to store files before archiving
    with tempfile.TemporaryDirectory() as tmpdir:

        airfoil_filenames = []

        # Save each airfoil as a separate JSON file
        for idx, airfoil in enumerate(PROJECT.project_airfoils):
            airfoil_data = save_airfoil_to_json(idx)
            airfoil_filename = f"airfoil_{idx}.arf"
            airfoil_path = os.path.join(tmpdir, airfoil_filename)
            with open(airfoil_path, "w") as outfile:
                outfile.write(airfoil_data)
            airfoil_filenames.append(airfoil_filename)

        designed_components = []

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
                        "tan_accel": segment.params.get('tan_accel', 0.1)
                    }
                    control_points = {
                        'le': segment.control_points.get('le', []),
                        'ps': segment.control_points.get('ps', []),
                        'ss': segment.control_points.get('ss', []),
                        'te': segment.control_points.get('te', []),
                        'le_ps': segment.control_points.get('le_ps', []),
                        'te_ps': segment.control_points.get('te_ps', []),
                        'le_ss': segment.control_points.get('le_ss', []),
                        'te_ss': segment.control_points.get('te_ss', [])
                    }
                    geom = {
                        'le': segment.geom.get('le', []),
                        'ps': segment.geom.get('ps', []),
                        'ss': segment.geom.get('ss', []),
                        'te': segment.geom.get('te', [])
                    }
                    segments = {
                        "infos": infos,
                        "airfoil": f"airfoil_{getattr(segment, 'airfoil_index', 0)}.json",  # reference to airfoil file
                        "anchor": segment.anchor,
                        "params": params,
                        "control_points": control_points,
                        "geom": geom
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
                geom = {
                    'le': wing.geom.get('le', []),
                    'ps': wing.geom.get('ps', []),
                    'ss': wing.geom.get('ss', []),
                    'te': wing.geom.get('te', [])
                }
                wings = {
                    "infos": infos,
                    "params": params,
                    "segments": designed_segments,
                    "geom": geom
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
        
        AirFLOW = {
            "program name": AIRFLOW.program_name,
            "program version": AIRFLOW.program_version,
            "file name": os.path.basename(fileName),
        }
        Project = {
            "project name": PROJECT.project_name,
            "creation date": PROJECT.project_date,
            "modification date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project description": PROJECT.project_description,
            "project path": fileName,
            "project components": designed_components,
            "project airfoils": airfoil_filenames
        }
        data = {
            "Program": AirFLOW,
            "Project": Project
        }

        # Convert all numpy arrays to lists before saving
        data = convert_ndarray_to_list(data)

        # Save project.airflow
        project_json_path = os.path.join(tmpdir, "project.airflow")
        with open(project_json_path, "w") as f:
            json.dump(data, f, indent=1)

        # Create .tgz archive
        tgz_path = fileName if fileName.endswith('.tgz') else fileName + ".tgz"

        with tarfile.open(tgz_path, "w:gz") as tar:
            tar.add(project_json_path, arcname="project.airflow")
            for airfoil_filename in airfoil_filenames:
                tar.add(os.path.join(tmpdir, airfoil_filename), arcname=airfoil_filename)

        print("AIRFLOW > Project archive successfully saved:", tgz_path)
        return tgz_path

def loadProject(fileName):

    from src.arfdes.tools_airfoil import load_airfoil_from_json
    from src.utils.tools_program import convert_list_to_ndarray
    from src.obj.wing import Component, Wing, Segment  # Import the templates

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

        # Restore AIRFLOW info (optional, usually not needed)
        if "Program" in data:
            if AIRFLOW.program_version != data["Program"].get("program version", AIRFLOW.program_version):
                print("AirFLOW > WARNING: Current program version is different from the saved version. Some features may not work as expected. \nMissing parameters will take default values.")

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
                airfoil_obj = load_airfoil_from_json(airfoil_path)
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

    print("AIRFLOW > Project archive successfully loaded:", fileName)
    return True

AIRFLOW = Program()  # Create a global instance of Program
PROJECT = Project()  # Create a global instance of Project