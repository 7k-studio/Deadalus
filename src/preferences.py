import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QCheckBox, QLabel, QDialog, QPushButton, QHBoxLayout, QComboBox
)
from globals import AIRFLOW

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

        perf_layout.addWidget(perf_text)
        perf_layout.addWidget(self.general_performance)

        layout.addLayout(perf_layout)
        layout.addStretch()
        self.general_tab.setLayout(layout)

    def on_performance_changed(self, value):
        AIRFLOW.general["performance"] = value

    def init_airfoil_tab(self):
        layout = QVBoxLayout()
        self.airfoil_show_grid = QCheckBox("Show Grid")
        self.airfoil_show_grid.setChecked(AIRFLOW.airfoil_designer["show_grid"])
        self.airfoil_show_construction = QCheckBox("Show Construction")
        self.airfoil_show_construction.setChecked(AIRFLOW.airfoil_designer["show_construction"])
        layout.addWidget(self.airfoil_show_grid)
        layout.addWidget(self.airfoil_show_construction)
        layout.addStretch()
        self.airfoil_tab.setLayout(layout)

    def init_wing_tab(self):
        layout = QVBoxLayout()
        self.wing_show_grid = QCheckBox("Show Grid")
        self.wing_show_grid.setChecked(AIRFLOW.wing_designer["show_grid"])
        self.wing_show_construction = QCheckBox("Show Ruler")
        self.wing_show_construction.setChecked(AIRFLOW.wing_designer["show_ruler"])
        layout.addWidget(self.wing_show_grid)
        layout.addWidget(self.wing_show_construction)
        layout.addStretch()
        self.wing_tab.setLayout(layout)

    def save_preferences(self):
        AIRFLOW.airfoil_designer["show_grid"] = self.airfoil_show_grid.isChecked()
        AIRFLOW.airfoil_designer["show_construction"] = self.airfoil_show_construction.isChecked()
        AIRFLOW.wing_designer["show_grid"] = self.wing_show_grid.isChecked()
        AIRFLOW.wing_designer["show_construction"] = self.wing_show_construction.isChecked()
        self.accept()

# For testing the dialog independently
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = PreferencesWindow()
    if dlg.exec_():
        print("Preferences saved.")
    else:
        print("Cancelled.")