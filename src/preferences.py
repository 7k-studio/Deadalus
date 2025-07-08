import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QCheckBox, QLabel, QDialog, QPushButton, QHBoxLayout, QComboBox
)
from globals import AIRFLOW
import json

class PreferencesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.resize(300, 200)

        self.tabs = QTabWidget()
        self.general_tab = QWidget()
        self.airfoil_tab = QWidget()
        self.wing_tab = QWidget()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.airfoil_tab, "Airfoil")
        self.tabs.addTab(self.wing_tab, "Wing")

        self.init_general_tab()
        self.init_airfoil_tab()
        self.init_wing_tab()

        btn_box = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Close")
        btn_box.addWidget(self.save_btn)
        btn_box.addWidget(self.cancel_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addLayout(btn_box)
        self.setLayout(layout)

        self.save_btn.clicked.connect(self.save_preferences)
        self.cancel_btn.clicked.connect(self.reject)

    def init_general_tab(self):
        layout = QVBoxLayout()
        perf_layout = QHBoxLayout()

        perf_text = QLabel("General Performance:")
        perf_text.setToolTip("Select the general performance level for the application.")
        self.general_performance = QComboBox()
        self.general_performance.addItems(["fast", "normal", "good"])
        self.general_performance.currentTextChanged.connect(self.on_performance_changed)
        # Fix: Ensure AIRFLOW.preferences['general'] is a dict, not a list
        self.general_performance.setCurrentText(AIRFLOW.preferences['general'].get('performance', 'normal'))

        perf_layout.addWidget(perf_text)
        perf_layout.addWidget(self.general_performance)

        layout.addLayout(perf_layout)
        layout.addStretch()
        self.general_tab.setLayout(layout)

    def on_performance_changed(self, value):
        AIRFLOW.preferences['general']["performance"] = value

    def init_airfoil_tab(self):
        layout = QVBoxLayout()
        self.airfoil_show_grid = QCheckBox("Show Grid")
        self.airfoil_show_grid.setChecked(AIRFLOW.preferences['airfoil_designer']['show_grid'])
        self.airfoil_show_control_points = QCheckBox("Show Control Points")
        self.airfoil_show_control_points.setChecked(AIRFLOW.preferences['airfoil_designer']['show_control_points'])
        self.airfoil_show_construction = QCheckBox("Show Construction")
        self.airfoil_show_construction.setChecked(AIRFLOW.preferences['airfoil_designer']['show_construction'])

        layout.addWidget(self.airfoil_show_grid)
        layout.addWidget(self.airfoil_show_control_points)
        layout.addWidget(self.airfoil_show_construction)
        layout.addStretch()
        self.airfoil_tab.setLayout(layout)

    def init_wing_tab(self):
        layout = QVBoxLayout()
        self.wing_show_grid = QCheckBox("Show Grid")
        self.wing_show_grid.setChecked(AIRFLOW.preferences['wing_designer']['show_grid'])
        self.wing_show_ruler = QCheckBox("Show Ruler")
        self.wing_show_ruler.setChecked(AIRFLOW.preferences['wing_designer']['show_ruler'])
        layout.addWidget(self.wing_show_grid)
        layout.addWidget(self.wing_show_ruler)
        layout.addStretch()
        self.wing_tab.setLayout(layout)

    def save_preferences(self):
        AIRFLOW.preferences['airfoil_designer']["show_grid"] = self.airfoil_show_grid.isChecked()
        AIRFLOW.preferences['airfoil_designer']["show_control_points"] = self.airfoil_show_control_points.isChecked()
        AIRFLOW.preferences['airfoil_designer']["show_construction"] = self.airfoil_show_construction.isChecked()
        AIRFLOW.preferences['wing_designer']["show_grid"] = self.wing_show_grid.isChecked()
        AIRFLOW.preferences['wing_designer']["show_ruler"] = self.wing_show_ruler.isChecked()
        self.accept()
        
        """Save the airfoil data to a JSON format file."""
        # Use self.program_info to access program details

        preferences = {}

        # Fix: Remove trailing comma so this is a dict, not a tuple
        preferences['general'] = {
            "performance": str(AIRFLOW.preferences['general'].get("performance", "")),
        }
        preferences['airfoil_designer'] = {
            "show_grid": AIRFLOW.preferences['airfoil_designer'].get("show_grid", True),
            "show_control_points": AIRFLOW.preferences['airfoil_designer'].get("show_control_points", True),
            "show_construction": AIRFLOW.preferences['airfoil_designer'].get("show_construction", True),
        }
        preferences['wing_designer'] = {
            "show_grid": AIRFLOW.preferences['wing_designer'].get("show_grid", True),
            "show_ruler": AIRFLOW.preferences['wing_designer'].get("show_ruler", True),
        }
 
        json_object = json.dumps(preferences, indent=1)

        with open(f"src/settings", "w") as outfile:
            outfile.write(json_object)
            print(f"Saved file: settings")

# For testing the dialog independently
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = PreferencesWindow()
    if dlg.exec_():
        print("Preferences saved.")
    else:
        print("Cancelled.")