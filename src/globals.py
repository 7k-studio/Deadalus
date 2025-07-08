from datetime import date
import json

class Program:
    def __init__(self):
        self.program_name = "AirFLOW"
        self.program_version = "0.1.0dev"

        self.preferences = {
            'general': {
                "performance": "normal",  # Options: "normal", "fast", "slow" 
            },
            'airfoil_designer': {
                "show_grid": True,
                "show_control_points": True,
                "show_construction": True,
            },
            'wing_designer': {
                "show_grid": True,
                "show_ruler": True,
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

AIRFLOW = Program()  # Create a global instance of Program
PROJECT = Project()  # Create a global instance of Project