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
import src.wngdes.tools_wing

from src.obj.class_airfoil import Airfoil
from src.arfdes.tools_airfoils import Reference_load
import src.arfdes.tools_reference as tools


from src.opengl.viewport2d import ViewportOpenGL

logger = logging.getLogger(__name__)

class TreeAirfoil(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, program=None, project=None, parent=None, open_gl=None):
        super(TreeAirfoil, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.DEADALUS = program
        self.PROJECT = project
        self.AIRFOILDESIGNER = parent

        self.item = None
        self.item_top = None
        self.selected = None
        self.selected_airfoil = None
        self.selected_airfoil_index = None

        self.init_tree()

    def init_tree(self):

        self.arf_widget = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)  # Adjust the number of columns
        self.tree.setHeaderLabels(["Name", "Type", "Last modification", "Creation Date"])
        self.tree.setMinimumHeight(100)  # Set minimum height for the tree menu
        self.tree.setColumnWidth(0, 120) # Set width of the first column
        self.tree.setColumnWidth(1, 35)  # Set width of the second column
        self.tree.setColumnWidth(2, 100)  # Set width of the third column
        self.tree.setColumnWidth(3, 100)  # Set width of the forth column

        self.arf_widget.addWidget(self.tree)
        self.setLayout(self.arf_widget)

        # Expose the internal tree's itemClicked signal so external code can connect to TreeAirfoil.itemClicked
        self.itemClicked = self.tree.itemClicked

        self.logger.debug('Tree initialized')
        # Connect internal tree signal to the handler
        self.tree.itemClicked.connect(self.on_select)

    def on_select(self, item, column):
        
        if not item:
            # Determine if a child node was clicked
            self.item = self.tree.currentItem()

        # Handle item click events
        try:
            self.item = item
            self.logger.debug(f"Clicked on: {self.item.text(0)}")
        except Exception:
            self.logger.debug("Clicked on tree item")

        if self.item:
            component_attr = None
            if self.item.parent():
                # child clicked -> map its label to component attribute
                child_label = self.item.text(0).strip().lower()
                mapping = {
                    "leading edge": "LE", "leading_edge": "LE", "leadingedge": "LE", "le": "LE",
                    "trailing edge": "TE", "trailing_edge": "TE", "trailingedge": "TE", "te": "TE",
                    "pressure side": "PS", "pressure_side": "PS", "pressureside": "PS", "ps": "PS",
                    "suction side": "SS", "suction_side": "SS", "suctionside": "SS", "ss": "SS",
                }
                component_attr = mapping.get(child_label)
                self.top_item = self.item.parent()
            else:
                self.top_item = self.item

            self.selected_airfoil_index = self.tree.indexOfTopLevelItem(self.top_item)
            if self.selected_airfoil_index == -1:
                self.logger.debug("Top-level item index not found for selected item")
                return

            self.selected_airfoil = self.PROJECT.airfoils[self.selected_airfoil_index]
            self.selected_airfoil.update()

            if component_attr:
                self.selected = getattr(self.selected_airfoil, component_attr)
            else:
                self.selected = self.selected_airfoil
    
            if self.AIRFOILDESIGNER.OPEN_GL:
                    # Always set the full airfoil; if viewport supports component-highlight, call it
                    self.AIRFOILDESIGNER.OPEN_GL.set_airfoil_to_display(self.selected_airfoil)
                    if component_attr and hasattr(self.AIRFOILDESIGNER.OPEN_GL, "set_component_to_display"):
                        try:
                            self.AIRFOILDESIGNER.OPEN_GL.set_component_to_display(self.selected_airfoil, component_attr)
                        except Exception:
                            self.logger.exception("Viewport failed to set component display")
                    # force repaint so component selection is immediately visible
                    try:
                        self.AIRFOILDESIGNER.OPEN_GL.update()
                    except Exception:
                        self.logger.exception("Failed to request viewport update")
                    self.logger.debug('Passed airfoil (and component if any) to be displayed')
            else:
                self.logger.exception("Failed to set airfoil to viewport")
        else:
            self.logger.debug("Top-level item index not found")

    def add_airfoil_to_tree(self, airfoil_obj=None, name="Airfoil"):
        """Add an airfoil to the list and tree menu."""
        modification_date = airfoil_obj.info.get('modification_date', 'Unknown')
        creation_date = airfoil_obj.info.get('creation_date', 'Unknown')
        description = airfoil_obj.info.get('description', 'No description')
        tree_item = QTreeWidgetItem([airfoil_obj.name, None, str(modification_date), str(creation_date)])
        self.tree.addTopLevelItem(tree_item)

        if airfoil_obj.LE:
            name = 'Leading Edge'
            type = airfoil_obj.LE.type
            le_item = QTreeWidgetItem([str(name), str(type)])
            tree_item.addChild(le_item)
        if airfoil_obj.TE:
            name = 'Trailing Edge'
            type = airfoil_obj.TE.type
            te_item = QTreeWidgetItem([str(name), str(type)])
            tree_item.addChild(te_item)
        if airfoil_obj.PS:
            name = 'Pressure Side'
            type = airfoil_obj.PS.type
            ps_item = QTreeWidgetItem([str(name), str(type)])
            tree_item.addChild(ps_item)
        if airfoil_obj.SS:
            name = 'Suction Side'
            type = airfoil_obj.SS.type
            ss_item = QTreeWidgetItem([str(name), str(type)])
            tree_item.addChild(ss_item)


        logger.info(f"Airfoil '{name}' added to the tree")
        
    def update(self):
        """Update the tree menu based on the current self.project.airfoils."""
        self.tree.clear()  # Clear existing items

        if self.PROJECT is None:
            return

        # Set up tree columns
        self.tree.setColumnCount(4)  # Adjust the number of columns
        self.tree.setHeaderLabels(["Name", "Type", "Last modification", "Creation Date"])  # Set column headers

        for airfoil in self.PROJECT.airfoils:
            self.logger.debug(airfoil)
            # Assuming airfoil_list contains objects with 'info' dictionary
            name = airfoil.name
            modification_date = airfoil.info.get('modification_date', 'Unknown')
            creation_date = airfoil.info.get('creation_date', 'Unknown')
            description = airfoil.info.get('description', 'No description')

            # Create a tree item with multiple columns
            tree_item = QTreeWidgetItem([name, None, str(modification_date), str(creation_date)])
            self.tree.addTopLevelItem(tree_item)

            print("airfoil ", airfoil.LE)
            
            if airfoil.LE:
                name = 'Leading Edge'
                le_item = QTreeWidgetItem([str(name), airfoil.LE.type])
                tree_item.addChild(le_item)
            if airfoil.PS:
                name = 'Pressure Side'
                ps_item = QTreeWidgetItem([str(name), airfoil.LE.type])
                tree_item.addChild(ps_item)
            if airfoil.SS:
                name = 'Suction Side'
                ss_item = QTreeWidgetItem([str(name), airfoil.LE.type])
                tree_item.addChild(ss_item)
            if airfoil.TE:
                name = 'Trailing Edge'
                te_item = QTreeWidgetItem([str(name), airfoil.LE.type])
                tree_item.addChild(te_item)
        
        logger.info("Tree is refreshed")
    
    def add(self, name, time, dscr='designed from scratch in airfoil designer'):
        """ Creates new airfoil out of initial parameters"""
        if self.PROJECT is None:
            self.logger.error("Cannot add airfoil: PROJECT is not set")
            return

        airfoil_obj = Airfoil(self.DEADALUS)
        airfoil_obj.name = name  # Ensure the name is set
        airfoil_obj.info['creation_date'] = time
        airfoil_obj.info['modification_date'] = time
        airfoil_obj.info['description'] = dscr

        self.PROJECT._ensure_unique_name(airfoil_obj)  # Ensure unique name

        self.PROJECT.airfoils.append(airfoil_obj)
        self.PROJECT.nominal_airfoils.append(airfoil_obj)
        self.add_airfoil_to_tree(airfoil_obj, name=airfoil_obj.name)
    
    def append(self, fileName):
        """ Opens an airfoil from saved file and appends it into project """
        try:
            airfoil_obj, _ = tools.load_airfoil_from_json(fileName)
            self.PROJECT._ensure_unique_name(airfoil_obj)  # Ensure unique name
            self.PROJECT.airfoils.append(airfoil_obj)
            if airfoil_obj:
                self.logger.debug(f"An airfoil was loaded: {airfoil_obj.name}")
                self.add_airfoil_to_tree(airfoil_obj, airfoil_obj.name)
                self.logger.info("Appending an airfoil was sucessful!")
        except TypeError:
            self.logger.error("Failed to append airfoil!")
            
    def delete(self):
        try:
            if self.selected_airfoil is None:
                self.logger.error('No valid airfoil selected!')
                return False, None
            
            name = self.selected_airfoil.name
            
            # Remove from project airfoils
            self.PROJECT.airfoils.remove(self.selected_airfoil)
            
            # If it's in nominal_airfoils, remove from there too
            if self.selected_airfoil in self.PROJECT.nominal_airfoils:
                self.PROJECT.nominal_airfoils.remove(self.selected_airfoil)
            
            # Remove the item from the tree menu
            self.tree.takeTopLevelItem(self.selected_airfoil_index)
            
            self.logger.debug(f"Deleted airfoil: {name}") 
            self.AIRFOILDESIGNER.OPEN_GL.clear()
            return True, name
        except (ValueError, AttributeError, TypeError):
            self.logger.error('Failed to delete airfoil!')
            return False, None  
        
    def mark_edited(self):
        self.top_item.setText(0, f"{self.selected_airfoil.name}*")