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
#System imports
import sys
from datetime import date
import logging

#PyQt5 imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QVBoxLayout, 
    QWidget, QHBoxLayout, QLineEdit, QFormLayout, QLabel, 
    QMenuBar, QAction, QFileDialog, QTreeWidget, 
    QTreeWidgetItem, QTextEdit, QStackedWidget, QHeaderView,
    QTableWidget, QTableWidgetItem, QPushButton
    )
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal

#Self imports
import src.obj as obj
from src.obj.objects2D import Airfoil
from src.arfdes.tools_airfoils import Reference_load
import src.arfdes.tools_reference as tools
import src.globals as globals

from src.opengl.viewport2d import ViewportOpenGL

class TreeRererence(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)
    def __init__(self, parent=None):
        super(TreeRererence, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.init_tree()

    def init_tree(self):
        self.ref_widget = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)  # Set column count to 3
        self.tree.setHeaderLabels(["Reference airfoils", "Format", "Visible"])  # Update header labels
        self.tree.setMinimumHeight(50)  # Set minimum height for the tree menu

        # Configure column widths and resizing behavior
        self.tree.setColumnWidth(0, 130) # Set width of the first column
        self.tree.setColumnWidth(1, 50)  # Set width of the second column
        self.tree.setColumnWidth(2, 50)  # Set width of the third column

        self.ref_widget.addWidget(self.tree)

        options_buttons = QHBoxLayout()
        addButton = QPushButton("+")
        addButton.setStyleSheet("background-color: lightgrey;")
        addButton.clicked.connect(self.add_reference)
        addButton.setFixedSize(20, 20)  # Set fixed size for the button

        delButton = QPushButton("-")
        delButton.setStyleSheet("background-color: lightgrey;")
        delButton.clicked.connect(self.delete_reference)
        delButton.setFixedSize(20, 20)  # Set fixed size for the button

        shoButton = QPushButton("Show/Hide")
        shoButton.setStyleSheet("background-color: lightgrey;")
        shoButton.clicked.connect(self.show_reference)
        shoButton.setFixedHeight(20)

        ediButton = QPushButton("Edit")
        ediButton.setStyleSheet("background-color: lightgrey;")
        ediButton.clicked.connect(self.edit_reference)
        ediButton.setFixedHeight(20)

        options_buttons.addWidget(addButton)
        options_buttons.addWidget(delButton)
        options_buttons.addWidget(shoButton)
        options_buttons.addWidget(ediButton)

        self.ref_widget.addLayout(options_buttons)

        # Set the layout for the widget
        self.setLayout(self.ref_widget)

    def add_reference(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Accepted file formats (*.ddls; *.txt; *.dat);; Deadalus Database Files (*.ddls);; Selig File Format Files (*.txt);; All Files (*)", options=options)
        if fileName:
            if (fileName.split(".")[1]).lower() == "ddls":
                tools.load_json_reference(fileName)
            if (fileName.split(".")[1]).lower() == "txt" or (fileName.split(".")[1]).lower() == "dat":
                tools.load_selig_reference(fileName)
            self.logger.debug(f"Opened file '{fileName}'")
            self.refresh_tree()

    def delete_reference():
        pass

    def show_reference(self):
        selected_item = self.tree.currentItem()
        if not selected_item:
            self.logger.warning("First select an airfoil!")
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.tree.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            self.logger.error("No connection between selected airfoil and project airfoil")
            return  # Invalid selection

        airfoil_obj = globals.PROJECT.reference_airfoils[airfoil_index]
        
        if airfoil_obj.visible == False:
            airfoil_obj.visible = True
        else:
            airfoil_obj.visible = False
        
        self.refresh_tree()

    def edit_reference():
        pass
    
    def refresh_tree(self):
        self.tree.clear()  # Clear existing items
        for airfoil in globals.PROJECT.reference_airfoils:
            self.add_airfoil_to_tree(airfoil)
        self.logger.info("Reference Tree is refreshed")

    def add_airfoil_to_tree(self, airfoil_obj=None):
        """Add an airfoil to the list and tree menu."""
        name = airfoil_obj.infos.get('name', 'Unknown')
        format = airfoil_obj.infos.get('format', 'Unknown')
        visible = "Yes" if airfoil_obj.visible else "No"  # Convert boolean to string

        tree_item = QTreeWidgetItem([name, format, visible])  # Add 3 columns of data
        self.tree.addTopLevelItem(tree_item)
        self.logger.info(f"Airfoil '{name}' added to the tree")