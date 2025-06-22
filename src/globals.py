from datetime import date

class Program:
    def __init__(self):
        self.program_name = "AirFLOW"
        self.program_version = "0.1.0dev"
        self.general = {
            "performance": "normal",  # Options: "normal", "fast", "slow" 
        }
        self.airfoil_designer = {
            "show_grid": True,
            "show_construction": True,
        }
        self.wing_designer = {
            "show_grid": True,
            "show_ruler": True,
        }

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