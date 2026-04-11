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
import logging
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from datetime import date
from src.obj.class_airfoil import Airfoil

class TreeObject(QTreeWidget):
    def __init__(self, program=None, project=None, parent=None):
        super(TreeObject, self).__init__(parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.DAEDALUS = program
        self.PROJECT = project
        self.main_window = parent
        self.selected_component = None
        self.selected_wing = None
        self.selected_segment = None
        self.update()

    def update(self):
        """Update the tree menu based on the current self.PROJECT.components."""
        self.clear()  # Clear existing items

        if self.PROJECT is None:
            return

        for component in self.PROJECT.components:
            name = component.infos.get('name', 'Unknown')
            modification_date = component.infos.get('modification_date', 'Unknown')
            creation_date = component.infos.get('creation_date', 'Unknown')
            tree_item = QTreeWidgetItem([str(name), str(modification_date), str(creation_date)])
            self.addTopLevelItem(tree_item)

            for wing in component.wings:
                wing_name = wing.infos.get('name', 'Unknown')
                wing_item = QTreeWidgetItem([str(wing_name)])
                tree_item.addChild(wing_item)

                for segment in wing.segments:
                    segment_name = segment.infos.get('name', 'Unknown')
                    segment_item = QTreeWidgetItem([str(segment_name)])
                    wing_item.addChild(segment_item)

        self.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item, column):
        # Handle item click events
        self.logger.debug(f"Clicked on: {item.text(column)}")
        
        # Determine the level and set selected items
        if item.parent() is None:
            # Top-level: component
            self.selected_component = self.PROJECT.components[self.indexOfTopLevelItem(item)]
            self.selected_wing = None
            self.selected_segment = None
        elif item.parent().parent() is None:
            # Wing level
            component_index = self.indexOfTopLevelItem(item.parent())
            self.selected_component = self.PROJECT.components[component_index]
            wing_index = item.parent().indexOfChild(item)
            self.selected_wing = self.selected_component.wings[wing_index]
            self.selected_segment = None
        else:
            # Segment level
            component_index = self.indexOfTopLevelItem(item.parent().parent())
            self.selected_component = self.PROJECT.components[component_index]
            wing_index = item.parent().parent().indexOfChild(item.parent())
            self.selected_wing = self.selected_component.wings[wing_index]
            segment_index = item.parent().indexOfChild(item)
            self.selected_segment = self.selected_wing.segments[segment_index]
    
    def add_component_to_tree(self, component_obj):
        """Add a component to the list and tree menu."""
        self.PROJECT.components.append(component_obj)
        name = component_obj.name
        modification_date = component_obj.infos.get('modification_date', 'Unknown')
        creation_date = component_obj.infos.get('creation_date', 'Unknown')
        tree_item = QTreeWidgetItem([str(name), str(modification_date), str(creation_date)])
        self.addTopLevelItem(tree_item)

    def add_wing_to_tree(self, item, name, wing_obj, component_obj):
        """Add a wing to the component."""     
        component_obj.wings.append(wing_obj)

    def add_segment_to_tree(self, tree_menu, name, segment_obj, component_index, wing_index):
        """Add a segment to the wing."""
        self.PROJECT.components[component_index].wings[wing_index].segments.append(segment_obj)
        """ Creates new airfoil out of initial parameters"""
        if self.PROJECT is None:
            self.logger.error("Cannot add airfoil: PROJECT is not set")
            return

        airfoil_obj = self.PROJECT.airfoils[0]
            
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