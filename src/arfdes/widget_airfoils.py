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
    QTableWidget, QTableWidgetItem, QPushButton, 
    )
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

#Self imports
import src.obj as obj
import src.wngwb.tools_wing

from src.obj.class_airfoil import Airfoil
from src.arfdes.tools_airfoils import Reference_load
import src.arfdes.tools_reference as tools
import src.globals as globals

from src.opengl.viewport2d import ViewportOpenGL

logger = logging.getLogger(__name__)

class TreeAirfoil(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super(TreeAirfoil, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.init_tree()

    def init_tree(self):

        self.arf_widget = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)  # Adjust the number of columns
        self.tree.setHeaderLabels(["Name", "Last modification", "Creation Date"])
        self.tree.setMinimumHeight(100)  # Set minimum height for the tree menu
        self.setColumnWidth(0, 150)
        self.arf_widget.addWidget(self.tree)
        self.setLayout(self.arf_widget)

    def add_airfoil_to_tree(self, airfoil_obj=None, name="Unknown"):
        """Add an airfoil to the list and tree menu."""
        modification_date = airfoil_obj.infos.get('modification_date', 'Unknown')
        creation_date = airfoil_obj.infos.get('creation_date', 'Unknown')
        description = airfoil_obj.infos.get('description', 'No description')
        tree_item = QTreeWidgetItem([name, str(modification_date), str(creation_date)])
        self.tree.addTopLevelItem(tree_item)

        if airfoil_obj.LE:
            name = 'Leading Edge'
            le_item = QTreeWidgetItem([str(name)])
            tree_item.addChild(le_item)
        if airfoil_obj.TE:
            name = 'Trailing Edge'
            te_item = QTreeWidgetItem([str(name)])
            tree_item.addChild(te_item)
        if airfoil_obj.PS:
            name = 'Pressure Side'
            ps_item = QTreeWidgetItem([str(name)])
            tree_item.addChild(ps_item)
        if airfoil_obj.SS:
            name = 'Suction Side'
            ss_item = QTreeWidgetItem([str(name)])
            tree_item.addChild(ss_item)


        logger.info(f"Airfoil '{name}' added to the tree")
        

    def refresh_tree(self):
        """Update the tree menu based on the current self.project.project_airfoils."""
        self.tree.clear()  # Clear existing items

        # Set up tree columns
        self.tree.setColumnCount(3)  # Adjust the number of columns
        self.tree.setHeaderLabels(["Name", "Last modification", "Creation Date"])  # Set column headers

        for airfoil in globals.PROJECT.project_airfoils:
            # Assuming airfoil_list contains objects with 'infos' dictionary
            name = airfoil.infos.get('name', 'Unknown')
            modification_date = airfoil.infos.get('modification_date', 'Unknown')
            creation_date = airfoil.infos.get('creation_date', 'Unknown')
            description = airfoil.infos.get('description', 'No description')

            # Create a tree item with multiple columns
            tree_item = QTreeWidgetItem([name, str(modification_date), str(creation_date)])
            self.tree.addTopLevelItem(tree_item)

            if airfoil.LE:
                name = 'Leading Edge'
                le_item = QTreeWidgetItem(str(name))
                tree_item.addChild(le_item)
            elif airfoil.PS:
                name = 'Pressure Side'
                ps_item = QTreeWidgetItem(str(name))
                tree_item.addChild(ps_item)
            elif airfoil.SS:
                name = 'Suction Side'
                ss_item = QTreeWidgetItem(str(name))
                tree_item.addChild(ss_item)
            elif airfoil.TE:
                name = 'Trailing Edge'
                te_item = QTreeWidgetItem(str(name))
                tree_item.addChild(te_item)
        
        logger.info("Tree is refreshed")
    
    def new(self, name, time, dscr='designed from scratch in airfoil designer'):
        """ Creates new airfoil out of initial parameters"""
        airfoil_obj = Airfoil()
        airfoil_obj.infos['name'] = name  # Ensure the name is set in infos
        airfoil_obj.infos['creation_date'] = time
        airfoil_obj.infos['modification_date'] = time
        airfoil_obj.infos['description'] = dscr
        globals.PROJECT.project_airfoils.append(airfoil_obj)
        globals.PROJECT.nominal_airfoils.append(airfoil_obj)
        self.add_airfoil_to_tree(airfoil_obj, name=name)
    
    def append(self, fileName):
        """ Opens an airfoil from saved file and appends it into project """
        try:
            airfoil_obj, _ = tools.load_airfoil_from_json(fileName)
            globals.PROJECT.project_airfoils.append(airfoil_obj)
            if airfoil_obj:
                self.logger.debug(f"An airfoil was loaded: {airfoil_obj.info['name']}")
                self.add_airfoil_to_tree(airfoil_obj, airfoil_obj.infos['name'])
                self.logger.info("Appending an airfoil was sucessful!")
        except TypeError:
            self.logger.error("Failed to append airfoil!")
            
    def delete(self):
        selected_item = self.tree.currentItem()
        if not selected_item:
            self.logger.error("No airfoil selected to be deleted!")
            return

        # Find the index of the selected item
        index = self.tree.indexOfTopLevelItem(selected_item)
        if index != -1:
            # Remove the item from the tree menu
            self.tree.takeTopLevelItem(index)
            # Remove the corresponding airfoil from the airfoils_list
            self.logger.debug(f"Available airfoils count: {len(globals.PROJECT.project_airfoils)}")
            self.logger.debug(f"Does airoils match nominals: {len(globals.PROJECT.project_airfoils) == len(globals.PROJECT.nominal_airfoils)}")
            name = globals.PROJECT.project_airfoils[index].infos['name']
            del globals.PROJECT.project_airfoils[index]
            del globals.PROJECT.nominal_airfoils[index]
            self.logger.debug(f"Deleted airfoil at index {index} with it's nominal copy.")
            return True, name
        
        else:
            self.logger.debug("Invalid selection.")
            return False

