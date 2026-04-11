'''

Copyright (C) 2026 Jakub Kamyk

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
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QDialog, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal

class TextDescription(QWidget):
    closed = pyqtSignal()  # Signal emitted when the widget is closed

    def __init__(self, parent=None, program=None, project=None):
        super().__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.DAEDALUS = program
        self.PROJECT = project
        self.AIRFOILDESIGNER = parent
        self.selected_airfoil = None
        self.selected_tree_item = None

        self.widget()

    def widget(self):
        self.setWindowTitle("Description Widget")
        self.setMinimumSize(200, 100)

        # Layout
        layout = QVBoxLayout(self)

        # Text area
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)  # Initially read-only
        layout.addWidget(self.text_area)

        # Buttons
        button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit", self)
        self.edit_button.clicked.connect(self.edit_dialog)
        button_layout.addWidget(self.edit_button)

        layout.addLayout(button_layout)

    def clear(self):
        self.text_area.setPlainText("Select an airfoil to show it's description")
        self.selected_airfoil = None
        self.selected_tree_item = None

    def set_description(self, text):
        """Set the description text."""
        self.text_area.setPlainText(text)

    def edit_dialog(self):
        """Open a dialog to edit the description."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Description")
        dialog.setMinimumSize(400, 300)

        dialog_layout = QVBoxLayout(dialog)
        edit_area = QTextEdit(dialog)
        edit_area.setPlainText(self.text_area.toPlainText())
        dialog_layout.addWidget(edit_area)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, dialog)
        dialog_layout.addWidget(button_box)

        button_box.accepted.connect(lambda: self._save_description(edit_area, dialog))
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    def _save_description(self, edit_area, dialog):
        """Save the edited description."""
        new_desc = edit_area.toPlainText()
        self.text_area.setPlainText(new_desc)

        if self.selected_airfoil is not None:
            self.selected_airfoil.info['description'] = new_desc
            if self.selected_tree_item is not None:
                name = self.selected_airfoil.info.get('name', 'Airfoil')
                self.selected_tree_item.setText(0, f"{name}*")

        dialog.accept()

    def closeEvent(self, event):
        """Handle the close event and emit the closed signal."""
        self.closed.emit()
        super().closeEvent(event)
    
    def display_selected_airfoil(self):
        """Display the selected airfoil's data in the table.
        Accepts (item, column) from QTreeWidget.itemClicked. If a child node was clicked,
        show parameters for the corresponding component (LE/TE/PS/SS).
        """
        try:
            self.selected_airfoil = self.AIRFOILDESIGNER.TREE_AIRFOIL.selected_airfoil

            self.logger.debug(str(self.selected_airfoil.info['description']))
            self.set_description(self.selected_airfoil.info['description'])
        except Exception:
            self.logger.error("No airfoil was selected in the tree")