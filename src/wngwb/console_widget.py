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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QLabel

class ConsoleWidget(QWidget):
    def __init__(self, parent=None):
        super(ConsoleWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(QLabel("Console Output:"))
        layout.addWidget(self.output_area)

        self.input_area = QLineEdit(self)
        self.input_area.setPlaceholderText("Enter command...")
        layout.addWidget(self.input_area)

        self.setLayout(layout)

    def append_output(self, text):
        self.output_area.append(text)

    def get_input(self):
        return self.input_area.text()

    def clear_input(self):
        self.input_area.clear()