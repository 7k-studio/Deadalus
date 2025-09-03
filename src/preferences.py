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

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QCheckBox, QLabel, QDialog, QPushButton, QHBoxLayout, QComboBox, QSlider
)
from PyQt5.QtCore import Qt
from src.globals import AIRFLOW
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

        # Slider for performance (10% - 100%)
        self.general_performance_slider = QSlider(Qt.Horizontal)
        self.general_performance_slider.setMinimum(10)
        self.general_performance_slider.setMaximum(100)
        self.general_performance_slider.setTickInterval(10)
        self.general_performance_slider.setSingleStep(10)

        # Label to show % value
        self.general_performance_label = QLabel(f"{self.general_performance_slider.value()}%")

        self.general_performance_slider.valueChanged.connect(self.on_performance_changed)

        self.general_beta_features = QCheckBox("Beta Features")
        self.general_beta_features.setChecked(AIRFLOW.preferences['general']['beta_features'])

        perf_layout.addWidget(perf_text)
        perf_layout.addWidget(self.general_performance_slider)
        perf_layout.addWidget(self.general_performance_label)
        
        layout.addLayout(perf_layout)
        layout.addWidget(self.general_beta_features)
        layout.addStretch()
        self.general_tab.setLayout(layout)

    def on_performance_changed(self, value):
        self.general_performance_label.setText(f"{value}%")
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
        AIRFLOW.preferences['general']["beta_features"] = self.general_beta_features.isChecked()
        AIRFLOW.preferences['general']["performance"] = self.general_performance_slider.value()
        AIRFLOW.preferences['airfoil_designer']["show_grid"] = self.airfoil_show_grid.isChecked()
        AIRFLOW.preferences['airfoil_designer']["show_control_points"] = self.airfoil_show_control_points.isChecked()
        AIRFLOW.preferences['airfoil_designer']["show_construction"] = self.airfoil_show_construction.isChecked()
        AIRFLOW.preferences['wing_designer']["show_grid"] = self.wing_show_grid.isChecked()
        AIRFLOW.preferences['wing_designer']["show_ruler"] = self.wing_show_ruler.isChecked()
        self.accept()
        
        preferences = {}
        preferences['general'] = {
            "performance": self.general_performance_slider.value(),
            "beta_features": AIRFLOW.preferences['general'].get("beta_features", False),
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