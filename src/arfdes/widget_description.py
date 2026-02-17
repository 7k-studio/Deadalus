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
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QDialog, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal

class TextDescription(QWidget):
    closed = pyqtSignal()  # Signal emitted when the widget is closed

    def __init__(self, parent=None, program=None, project=None):
        super().__init__(parent)
        self.DEADALUS = program
        self.PROJECT = project
        self.AIRFOILDESIGNER = parent

        self.setWindowTitle("Description Widget")
        self.setMinimumSize(200, 100)

        # Layout
        layout = QVBoxLayout(self)

        # Text area
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(False)  # Initially read-only
        layout.addWidget(self.text_area)

        # Buttons
        # button_layout = QHBoxLayout()
        # self.edit_button = QPushButton("Edit", self)
        # self.edit_button.clicked.connect(self.edit_description)
        # button_layout.addWidget(self.edit_button)

        # layout.addLayout(button_layout)

    def set_description(self, text):
        """Set the description text."""
        self.text_area.setPlainText(text)

    def edit_description(self):
        """Open a dialog to edit the description."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Description")
        dialog.setMinimumSize(400, 300)

        dialog_layout = QVBoxLayout(dialog)
        edit_area = QTextEdit(dialog)
        edit_area.setPlainText(self.text_area.toPlainText())
        dialog_layout.addWidget(edit_area)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        dialog_layout.addWidget(button_box)

        button_box.accepted.connect(lambda: self._save_description(edit_area, dialog))
        button_box.rejected.connect(dialog.reject)

        dialog.exec_()

    def _save_description(self, edit_area, dialog):
        """Save the edited description."""
        self.text_area.setPlainText(edit_area.toPlainText())
        dialog.accept()

    def closeEvent(self, event):
        """Handle the close event and emit the closed signal."""
        self.closed.emit()
        super().closeEvent(event)
    
    def display_selected_airfoil(self, item, column=None):
        """Display the selected airfoil's data in the table.
        Accepts (item, column) from QTreeWidget.itemClicked. If a child node was clicked,
        show parameters for the corresponding component (LE/TE/PS/SS).
        """
        if self.AIRFOILDESIGNER.TREE_AIRFOIL is None:
            self.logger.warning("No tree_menu assigned to TableParameters")
            return

        # Determine if a child node was clicked
        component_attr = None
        if item.parent():
            # child clicked -> map its label to component attribute
            child_label = item.text(0).strip().lower()
            mapping = {
                "leading edge": "LE", "leading_edge": "LE", "leadingedge": "LE", "le": "LE",
                "trailing edge": "TE", "trailing_edge": "TE", "trailingedge": "TE", "te": "TE",
                "pressure side": "PS", "pressure_side": "PS", "pressureside": "PS", "ps": "PS",
                "suction side": "SS", "suction_side": "SS", "suctionside": "SS", "ss": "SS",
            }
            component_attr = mapping.get(child_label)
            top_item = item.parent()
        else:
            top_item = item

        index = self.AIRFOILDESIGNER.TREE_AIRFOIL.indexOfTopLevelItem(top_item)
        if index == -1:
            self.logger.debug("Top-level item index not found for selected item")
            return

        selected_airfoil = self.PROJECT.project_airfoils[index]

        # if component_attr:
        #     # Show component parameters
        #     selected_component = getattr(selected_airfoil, component_attr, None)
        #     if selected_component:
        #         self.populate_table(selected_component)
        #         # store component state for edits (child has 'params' and 'unit')
        #         self.airfoil = {key: value for key, value in vars(selected_component).items()}
        #         # Tell viewport about parent airfoil and (optionally) component
        #         if self.open_gl:
        #             try:
        #                 self.open_gl.set_airfoil_to_display(selected_airfoil)
        #                 if hasattr(self.open_gl, "set_component_to_display"):
        #                     self.open_gl.set_component_to_display(selected_airfoil, component_attr)
        #                 # force repaint so component selection is visible
        #                 self.open_gl.update()
        #             except Exception:
        #                 self.logger.exception("Failed to update viewport for component")
        #         self.logger.debug(f"Displayed component '{component_attr}' parameters")
        #     else:
        #         self.logger.warning(f"Component '{component_attr}' not found on selected airfoil")
        # else:
        #     # Top-level airfoil selected -> show overall params
        self.logger.debug(str(selected_airfoil.infos['description']))
        self.set_description(selected_airfoil.infos['description'])
        self.logger.debug('Displayed parent airfoil parameters')