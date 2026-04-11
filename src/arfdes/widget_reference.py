'''

Copyright (C) 2025 Jakub Kamyk

This file is part of DAEDALUS.

DAEDALUS is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

DAEDALUS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with DAEDALUS.  If not, see <http://www.gnu.org/licenses/>.

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
    QTableWidget, QTableWidgetItem, QPushButton, QDialog
    )
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal

#Self imports
import src.obj as obj
from src.arfdes.tools_airfoils import Reference_load
import src.arfdes.tools_reference as tools

from src.opengl.viewport2d import ViewportOpenGL

class ReferenceDialog(QDialog):
    def __init__(self, references, mode='show', parent=None):
        super().__init__(parent)
        self.references = references
        self.mode = mode
        self.selected_references = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Reference {self.mode.title()}")
        layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Name", "Format", "Visible"])
        self.tree.setSelectionMode(QTreeWidget.MultiSelection if self.mode in ['delete', 'show'] else QTreeWidget.SingleSelection)

        for ref in self.references:
            name = ref.info.get('name', 'Unknown')
            format_ = ref.info.get('format', 'Unknown')
            visible = "Yes" if ref.visible else "No"
            item = QTreeWidgetItem([name, format_, visible])
            self.tree.addTopLevelItem(item)

        layout.addWidget(self.tree)

        button_layout = QHBoxLayout()
        if self.mode == 'delete':
            accept_btn = QPushButton("Delete")
            accept_btn.clicked.connect(self.accept)
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(accept_btn)
            button_layout.addWidget(cancel_btn)
        elif self.mode == 'show':
            show_btn = QPushButton("Show")
            show_btn.clicked.connect(self.show_selected)
            hide_btn = QPushButton("Hide")
            hide_btn.clicked.connect(self.hide_selected)
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(show_btn)
            button_layout.addWidget(hide_btn)
            button_layout.addWidget(cancel_btn)
        else:  # edit, flip
            action_btn = QPushButton(self.mode.title())
            action_btn.clicked.connect(self.perform_action)
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.accept)
            button_layout.addWidget(action_btn)
            button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def accept(self):
        if self.mode == 'delete':
            selected_items = self.tree.selectedItems()
            for item in selected_items:
                index = self.tree.indexOfTopLevelItem(item)
                self.selected_references.append(self.references[index])
        super().accept()

    def show_selected(self):
        selected_items = self.tree.selectedItems()
        for item in selected_items:
            index = self.tree.indexOfTopLevelItem(item)
            self.references[index].visible = True
        self.update_tree()

    def hide_selected(self):
        selected_items = self.tree.selectedItems()
        for item in selected_items:
            index = self.tree.indexOfTopLevelItem(item)
            self.references[index].visible = False
        self.update_tree()

    def perform_action(self):
        # Placeholder for edit/flip
        print(f"{self.mode} action performed")

    def update_tree(self):
        for i, ref in enumerate(self.references):
            item = self.tree.topLevelItem(i)
            visible = "Yes" if ref.visible else "No"
            item.setText(2, visible)

class TreeRererence(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)
    def __init__(self, program=None, project=None, parent=None):
        super(TreeRererence, self).__init__(parent)
        self.setMinimumSize(200, 100)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.PROJECT = project
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
        addButton.clicked.connect(self.add_reference)
        addButton.setFixedSize(20, 20)  # Set fixed size for the button

        delButton = QPushButton("-")
        delButton.clicked.connect(self.delete_reference)
        delButton.setFixedSize(20, 20)  # Set fixed size for the button

        shoButton = QPushButton("Show/Hide")
        shoButton.clicked.connect(self.show_reference)
        shoButton.setFixedHeight(20)

        ediButton = QPushButton("Edit")
        ediButton.clicked.connect(self.edit_reference)
        ediButton.setFixedHeight(20)

        options_buttons.addWidget(addButton)
        options_buttons.addWidget(delButton)
        options_buttons.addWidget(shoButton)
        if self.DAEDALUS.preferences['general']['beta_features']:
            options_buttons.addWidget(ediButton)

        self.ref_widget.addLayout(options_buttons)

        # Set the layout for the widget
        self.setLayout(self.ref_widget)

    def show_delete_dialog(self):
        if not self.PROJECT or not self.PROJECT.reference_airfoils:
            return
        dialog = ReferenceDialog(self.PROJECT.reference_airfoils, mode='delete', parent=self)
        if dialog.exec_() == QDialog.Accepted:
            for ref in dialog.selected_references:
                self.PROJECT.reference_airfoils.remove(ref)
            self.update()

    def show_show_dialog(self):
        if not self.PROJECT or not self.PROJECT.reference_airfoils:
            return
        dialog = ReferenceDialog(self.PROJECT.reference_airfoils, mode='show', parent=self)
        dialog.exec_()
        self.update()

    def show_edit_dialog(self):
        if not self.PROJECT or not self.PROJECT.reference_airfoils:
            return
        dialog = ReferenceDialog(self.PROJECT.reference_airfoils, mode='edit', parent=self)
        dialog.exec_()

    def show_flip_dialog(self):
        if not self.PROJECT or not self.PROJECT.reference_airfoils:
            return
        dialog = ReferenceDialog(self.PROJECT.reference_airfoils, mode='flip', parent=self)
        dialog.exec_()

    def add_reference(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Accepted file formats (*.ddls; *.txt; *.dat);; Daedalus Database Files (*.ddls);; Selig File Format Files (*.txt);; All Files (*)", options=options)
        if fileName:
            if (fileName.split(".")[1]).lower() == "ddls":
                reference = tools.load_json_reference(fileName)
            if (fileName.split(".")[1]).lower() == "txt" or (fileName.split(".")[1]).lower() == "dat":
                reference = tools.load_selig_reference(fileName)
            if reference:
                self.PROJECT.reference_airfoils.append(reference)
                self.logger.debug(f"Opened file '{fileName}'")
                self.update()
            else:
                self.logger.error('Loading failed!')

    def delete_reference(self):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.logger.warning("First select an airfoil!")
            return

        to_remove = []
        for item in selected_items:
            index = self.tree.indexOfTopLevelItem(item)
            if 0 <= index < len(self.PROJECT.reference_airfoils):
                to_remove.append(self.PROJECT.reference_airfoils[index])

        for ref in to_remove:
            self.PROJECT.reference_airfoils.remove(ref)

        self.update()

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

        airfoil_obj = self.PROJECT.reference_airfoils[airfoil_index]
        
        airfoil_obj.visible = not airfoil_obj.visible
        
        self.update()
        self.DAEDALUS.AIRFOILDESIGNER.OPEN_GL.update()

    def edit_reference():
        pass
    
    def update(self):
        self.tree.clear()  # Clear existing items
        if self.PROJECT is None:
            return
        for airfoil in self.PROJECT.reference_airfoils:
            self.add_airfoil_to_tree(airfoil)
        self.logger.info("Reference Tree is refreshed")

    def add_airfoil_to_tree(self, airfoil_obj=None):
        """Add an airfoil to the list and tree menu."""
        name = airfoil_obj.info.get('name', 'Unknown')
        format = airfoil_obj.info.get('format', 'Unknown')
        visible = "Yes" if airfoil_obj.visible else "No"  # Convert boolean to string

        tree_item = QTreeWidgetItem([name, format, visible])  # Add 3 columns of data
        self.tree.addTopLevelItem(tree_item)
        self.logger.info(f"Airfoil '{name}' added to the tree")