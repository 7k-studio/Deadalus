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

    def __init__(self, parent=None):
        super().__init__(parent)
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