from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

import globals  # Import from globals.py


class Tabele(QTableWidget):
    def __init__(self, parent=None, tree_menu=None, project=None):
        super(Tabele, self).__init__(parent)
        self.main_window = parent
        self.project = project
        self.tree_menu = tree_menu
        self.init_tabele()
    
    def init_tabele(self, params=None):

        # Initial Parameters
        self.params = {}

        # Parameter Table
        self.setRowCount(len(self.params))
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Parameter", "Value", "Nominal"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        #self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnWidth(1, 100)  # Set minimum width for column 2

    def add_editable_row(self, row, value):
        param_name = self.item(row, 0).text()
        if param_name == 'airfoil':
            airfoil_dropdown = QtWidgets.QComboBox()
            #airfoil_dropdown.addItems([airfoil.name for airfoil in globals.airfoil_list])
            #airfoil_dropdown.addItems(globals.PROJECT.project_airfoils)
            airfoil_dropdown.addItems([airfoil.infos['name'] for airfoil in globals.PROJECT.project_airfoils])
                
            try:
                airfoil_dropdown.setCurrentText(value)  # Set the current value
            except TypeError:
                print("ERROR: globals.PROJECT.project_airfoils is not iterable.")

            airfoil_dropdown.currentTextChanged.connect(lambda new_value: self.update_airfoil_value(row, new_value))
            self.setCellWidget(row, 1, airfoil_dropdown)

            self.save_current_element_state()
        
        elif param_name == 'wings' or param_name == 'segments':
            pass  # Skip these parameters as they are not editable in this context

        else:
            # Create a custom widget for editing with up/down buttons and input
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            # Input field for direct keyboard input
            try:
                value = format(value, '.4f')  # Format value to 4 decimal places
            except TypeError:
                pass
            value_input = QLineEdit(str(value))
            value_input.setAlignment(Qt.AlignCenter)
            value_input.setMinimumWidth(60)
            value_input.editingFinished.connect(lambda: self.update_value_from_input(row, value_input))

            # Up button
            up_button = QPushButton("▲")
            up_button.setFixedSize(20, 20)
            up_button.clicked.connect(lambda: self.adjust_value(row, 0.1))

            # Down button
            down_button = QPushButton("▼")
            down_button.setFixedSize(20, 20)
            down_button.clicked.connect(lambda: self.adjust_value(row, -0.1))

            # Add widgets to layout
            layout.addWidget(down_button)
            layout.addWidget(value_input)
            layout.addWidget(up_button)

            self.setCellWidget(row, 1, container)

            self.save_current_element_state()

    def update_airfoil_value(self, row, new_name):
        # Find the Airfoil object by name
        for airfoil in globals.PROJECT.project_airfoils:
            if airfoil.infos['name'] == new_name:
                selected_airfoil = airfoil
                break
        else:
            print("Airfoil not found!")
            return

        selected_item = self.tree_menu.currentItem()
        parent_item = selected_item.parent()
        try:
            grandparent_item = parent_item.parent()
        except AttributeError:
            grandparent_item = None
            
        if selected_item:
            if parent_item and grandparent_item:

                item_index = parent_item.indexOfChild(selected_item)
                parent_index = grandparent_item.indexOfChild(parent_item)
                grandparent_index = self.tree_menu.indexOfTopLevelItem(grandparent_item)

                element_item = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index]

        element_item.airfoil = selected_airfoil

        # Optionally, update the UI or trigger a redraw
        print(f"Changed airfoil for segment {row} to {selected_airfoil.infos['name']}")

    def update_value_from_input(self, row, value_input):
        # Update parameter from the input field
        param_name = self.item(row, 0).text()
        try:
            new_value = float(value_input.text())
            self.params[param_name] = new_value
            self.save_current_element_state()
            
        except ValueError:
            # Restore the last valid value if input is invalid
            print("WARNING: Invalid input, restoring last valid value.")
            value_input.setText(str(self.params[param_name]))

    def adjust_value(self, row, delta):
        # Adjust parameter value by delta
        param_name = self.item(row, 0).text()
        current_value = self.params[param_name]
        new_value = current_value + delta

        # Update value
        self.params[param_name] = new_value

        # Update the input field display
        new_value = format(new_value, '.5f')  # Format value to 5 decimal places
        cell_widget = self.cellWidget(row, 1)
        value_input = cell_widget.findChild(QLineEdit)
        value_input.setText(str(new_value))

        # Update element
        self.save_current_element_state()  # Save changes to the airfoil list


    def populate_table(self, element_obj):
        """Populate the table with data from an element object."""
        self.setRowCount(0)  # Clear existing rows
        for key, value in element_obj.params.items():
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(key))
            self.add_editable_row(row, value)
            nominal_value = QTableWidgetItem(str(value))
            nominal_value.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, nominal_value)  # Optional: Add nominal value column

    def display_selected_element(self, item):
        """Display the selected element in the table."""
        # Ensure main_window is set
        if self.tree_menu:

            selected_item = self.tree_menu.currentItem()
            parent_item = selected_item.parent()
            try:
                grandparent_item = parent_item.parent()
            except AttributeError:
                grandparent_item = None
            
            if selected_item:
                if parent_item and grandparent_item:

                    item_index = parent_item.indexOfChild(selected_item)
                    parent_index = grandparent_item.indexOfChild(parent_item)
                    grandparent_index = self.tree_menu.indexOfTopLevelItem(grandparent_item)

                    print(f'Segment at index: {grandparent_index} >>> {parent_index} >>> {item_index}')

                    element_item = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index]
                    print(type(element_item))

                    self.populate_table(element_item)
                    self.params = {key: value for key, value in vars(element_item).items() if key != "infos"}
                    element_item.transform_airfoil(grandparent_index, parent_index, item_index)

                if parent_item and not grandparent_item:

                    item_index = parent_item.indexOfChild(selected_item)
                    parent_index = self.tree_menu.indexOfTopLevelItem(parent_item)

                    print(f'Wing at index: {parent_index} >>> {item_index}')

                    element_item = globals.PROJECT.project_components[parent_index].wings[item_index]
                    self.populate_table(element_item)
                    self.params = {key: value for key, value in vars(element_item).items() if key != "infos"}

                if not parent_item and not grandparent_item:

                    item_index = self.tree_menu.indexOfTopLevelItem(selected_item)

                    print(f'Component at index: {item_index}')

                    element_item = globals.PROJECT.project_components[item_index]
                    self.populate_table(element_item)
                    self.params = {key: value for key, value in vars(element_item).items() if key != "infos"}

    def save_current_element_state(self):
        """Overwrite the current table data into the selected airfoil object."""
        
        if self.tree_menu:

            selected_item = self.tree_menu.currentItem()
            parent_item = selected_item.parent()
            try:
                grandparent_item = parent_item.parent()
            except AttributeError:
                grandparent_item = None
            
            if selected_item:
                if parent_item and grandparent_item:

                    item_index = parent_item.indexOfChild(selected_item)
                    parent_index = grandparent_item.indexOfChild(parent_item)
                    grandparent_index = self.tree_menu.indexOfTopLevelItem(grandparent_item)

                    print(f'Segment at index: {grandparent_index} >>> {parent_index} >>> {item_index}')

                    element_item = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index]

                if parent_item and not grandparent_item:

                    item_index = parent_item.indexOfChild(selected_item)
                    parent_index = self.tree_menu.indexOfTopLevelItem(parent_item)

                    print(f'Wing at index: {parent_index} >>> {item_index}')

                    element_item = globals.PROJECT.project_components[parent_index].wings[item_index]

                if not parent_item and not grandparent_item:

                    item_index = self.tree_menu.indexOfTopLevelItem(selected_item)

                    print(f'Component at index: {item_index}')

                    element_item = globals.PROJECT.project_components[item_index]

                # Update the airfoil object with table data
                for row in range(self.rowCount()):
                    key = self.item(row, 0).text()
                    # Retrieve the value from the QLineEdit inside the custom widget
                    cell_widget = self.cellWidget(row, 1)
                    if cell_widget:
                        value_input = cell_widget.findChild(QLineEdit)
                        if value_input:
                            try:
                                value = float(value_input.text())
                                setattr(element_item, key, value)
                            except ValueError:
                                print(f"Invalid value for parameter '{key}', skipping update.")
                try:
                    globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].transform_airfoil(grandparent_index, parent_index, item_index)
                except:
                    print('WARNING: No airfoil to transform')

                # Optionally, update the tree menu display
                selected_item.setText(0, f"{element_item.infos['name']}*")