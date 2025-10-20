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

#PyQt5 imports
from PyQt5.QtWidgets import (
    QWidget, QLabel, QAction, QMenuBar,
    QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, 
    QApplication, QMainWindow, QSplitter, 
    QFormLayout, 
    QFileDialog, QTreeWidget, 
    QTreeWidgetItem, QStackedWidget, QHeaderView,
    QTableWidget, QTableWidgetItem, QPushButton, QDialog, QDialogButtonBox
    )
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

#Self imports
import src.obj as obj
import src.wngwb.tools_wing

from src.obj.objects2D import Airfoil
from src.arfdes.tools_airfoils import Reference_load
import src.arfdes.tools_reference as tools
import src.globals as globals

from src.opengl.viewport2d import ViewportOpenGL

logger = logging.getLogger(__name__)

class TextDescription(QDialog):

    def __init__(self, parent=None, target_airfoil=None):
        super(TextDescription, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.airfoil_obj = target_airfoil
        self.setWindowTitle("Edit Airfoil Description")
        self.init_ui()

    def init_ui(self):
        # Create a custom dialog with QTextEdit
        layout = QVBoxLayout(self)

        label = QLabel("Edit the description below:", self)
        layout.addWidget(label)

        self.text = QTextEdit(self)
        self.text.setText(self.airfoil_obj.infos.get('description', ''))  # Pre-fill with current description
        layout.addWidget(self.text)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        layout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
    
    def accept(self):
        new_description = self.text.toPlainText()
        if new_description:
            # Update the airfoil object with the new description
            self.airfoil_obj.infos['description'] = new_description
            self.logger.info(f"Updated description for airfoil: {self.airfoil_obj.infos['name']}")
        super().accept()
