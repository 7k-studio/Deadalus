from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
import src.obj.aero as aero
from src.wngwb.tools_wing import add_component_to_tree
from datetime import date
import src.globals as globals

class TreeMenu(QTreeWidget):
    def __init__(self, parent=None):
        super(TreeMenu, self).__init__(parent)
        self.main_window = parent
        self.setHeaderLabel("Project Name")
        self.init_tree()

    def init_tree(self):
 
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