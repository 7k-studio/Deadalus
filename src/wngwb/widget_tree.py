'''

Copyright (C) 2025 Jakub Kamyk

This file is part of AirFLOW.

AirFLOW is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

AirFLOW is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AirFLOW.  If not, see <http://www.gnu.org/licenses/>.

'''

from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
import src.obj.airfoil as airfoil
from src.wngwb.tools_wing import add_component_to_tree
from datetime import date
import src.globals as globals

class TreeMenu(QTreeWidget):
    def __init__(self, parent=None):
        super(TreeMenu, self).__init__(parent)
        self.main_window = parent
        self.setHeaderLabel(f"{globals.PROJECT.project_name}")
        self.init_tree()

    def init_tree(self):
        self.clear()
 
        for component in globals.PROJECT.project_components:
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
        print(f"Clicked on: {item.text(column)}")