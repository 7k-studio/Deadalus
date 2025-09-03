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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QFileDialog
from src.arfdes.airfoil_designer import AirfoilDesigner  # Import the AirfoilDesigner class from the correct module
from src.wngwb.main_window import MainWindow
import src.globals as globals


class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.AIRFLOW = parent
        self.setWindowTitle("Splash Screen")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        #self.setAttribute(Qt.WA_DeleteOnClose, True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add splash image
        splash_label = QLabel(self)
        pixmap = QPixmap("src/assets/splash.png")
        if pixmap.isNull():
            print("Error: 'splash.png' not found or invalid path.")
        splash_label.setPixmap(pixmap)
        splash_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(splash_label)

        program_label = QLabel('AirFoil & Lifting Objects Workbench')
        program_label.setStyleSheet("font-size: 12px; font-weight: regular; color: black;")
        layout.addWidget(program_label, alignment=Qt.AlignLeft | Qt.AlignTop)

        version_label = QLabel('v{}'.format(self.AIRFLOW.program_version))
        version_label.setStyleSheet("font-size: 12px; font-weight: regular; color: black;")
        layout.addWidget(version_label, alignment=Qt.AlignLeft | Qt.AlignTop)

        copyright_label = QLabel('Copyright (C) 2025 Jakub Kamyk')
        copyright_label.setStyleSheet("font-size: 9px; font-weight: regular; color: black;")
        layout.addWidget(copyright_label, alignment=Qt.AlignCenter | Qt.AlignTop)
        

        # Add buttons
        button_layout = QHBoxLayout()
        button1 = QPushButton("New Project")
        button1.setStyleSheet("background-color: lightgrey;")
        button1.clicked.connect(self.new_project)
        button1.setFixedSize(220, 30)  # Set fixed size for the button

        button2 = QPushButton("Open Project")
        button2.setStyleSheet("background-color: lightgrey;")
        button2.clicked.connect(self.open_project)
        button2.setFixedSize(220, 30)  # Set fixed size for the button

        button_layout.addWidget(button1)
        button_layout.addWidget(button2)
        layout.addLayout(button_layout)

        # Center the buttons
        button_layout.setAlignment(Qt.AlignCenter)

        # Add close button
        close_button = QPushButton(self)
        icon = QIcon("src/assets/cross.png")
        if icon.isNull():
            print("Error: 'cross.png' not found or invalid path.")
        close_button.setIcon(icon)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("border: none;")
        close_button.clicked.connect(self.close)

        # Add close button to the top-right corner
        close_layout = QHBoxLayout()
        close_layout.addWidget(close_button)
        close_layout.setAlignment(Qt.AlignRight)
        layout.insertLayout(0, close_layout)  # Insert at the top of the main layout

    def new_project(self):
        """Create new AirFLOW project and open the AirfoilDesigner window."""
        self.PROJECT = globals.PROJECT.newProject()
        self.airfoil_designer_window = AirfoilDesigner(globals.AIRFLOW, globals.PROJECT)  # Pass airfoil_list
        self.airfoil_designer_window.show()
        self.close()

    def open_project(self):
        """Load AirFLOW project and open the AirfoilDesigner window."""
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "AirFLOW Database Files (*.afdb);; All Files (*)", options=options)
        if fileName:
            self.PROJECT = globals.loadProject(fileName)
            self.airfoil_designer_window = AirfoilDesigner(globals.AIRFLOW, globals.PROJECT)  # Pass airfoil_list
            self.airfoil_designer_window.show()
            self.close()
