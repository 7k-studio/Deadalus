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

from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLineEdit, QApplication
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

import src.globals as globals  # Import from globals.py


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
        """Add an editable row with up/down buttons and input field."""
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
        up_button.clicked.connect(lambda: self._adjust_value_with_modifiers(row, 1))

        # Down button
        down_button = QPushButton("▼")
        down_button.setFixedSize(20, 20)
        down_button.clicked.connect(lambda: self._adjust_value_with_modifiers(row, -1))

        # Add widgets to layout
        layout.addWidget(down_button)
        layout.addWidget(value_input)
        layout.addWidget(up_button)
        self.setCellWidget(row, 1, container)

        self.save_current_element_state()

    def _adjust_value_with_modifiers(self, row, direction):
            modifiers = QApplication.keyboardModifiers()
            if modifiers & Qt.ShiftModifier:
                delta = 1.0
            elif modifiers & Qt.ControlModifier:
                delta = 0.01
            else:
                delta = 0.1
            self.adjust_value(row, direction * delta)

    def update_value_from_input(self, row, value_input):
        # Update parameter from the input field
        param_name = self.item(row, 0).text()

        # Find the Airfoil object by name
        for airfoil in globals.PROJECT.project_airfoils:
            if airfoil.infos['name'] == value_input:
                selected_airfoil = airfoil
                break
            else:
                print("ERROR: Selected airfoil was not found!")
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
                self.save_current_element_state()
            
            if parent_item and not grandparent_item:

                item_index = parent_item.indexOfChild(selected_item)
                parent_index = self.tree_menu.indexOfTopLevelItem(parent_item)

                element_item = globals.PROJECT.project_components[parent_index].wings[item_index]

            if not parent_item and not grandparent_item:

                item_index = self.tree_menu.indexOfTopLevelItem(selected_item)

                element_item = globals.PROJECT.project_components[item_index]
        
        try:
            new_value = float(value_input.text())
            self.params[param_name] = new_value
            self.save_current_element_state()
        except ValueError:
            # Restore the last valid value if input is invalid
            print("WARNING: Invalid input, restoring last valid value.")
            value_input.setText(str(self.params[param_name]))

        # Optionally, update the UI or trigger a redraw
        
        print(f"Changed airfoil for segment {row} to {selected_airfoil.infos['name']}")

    def update_airfoil_value(self, row, value_input):
        # Update parameter from the input field
        param_name = self.item(row, 0).text()
        try:
            new_value = str(value_input)
            self.params[param_name] = new_value
            self.save_current_element_state()
        except ValueError:
            # Restore the last valid value if input is invalid
            print("WARNING: Invalid input, restoring last valid value.")
            value_input.setText(str(self.params[param_name]))

    def adjust_value(self, row, delta):
        # Adjust parameter value by delta
        print(self.params)
        param_name = self.item(row, 0).text()
        current_value = self.params['params'][param_name]
        new_value = current_value + delta

        # Update value
        self.params[param_name] = new_value

        # Update the input field display
        new_value = format(new_value, '.4f')  # Format value to 5 decimal places
        cell_widget = self.cellWidget(row, 1)
        value_input = cell_widget.findChild(QLineEdit)
        value_input.setText(str(new_value))

        # Update element
        self.save_current_element_state()  # Save changes to the airfoil list

    def populate_table(self, element_obj):
        """Populate the table with data from an element object."""
        self.setRowCount(0)  # Clear existing rows

        # Special handling for Segment to show available airfoils in ComboBox
        if hasattr(element_obj, 'airfoil'):
            # Airfoil ComboBox row
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem('airfoil'))
            airfoil_dropdown = QtWidgets.QComboBox(self)  # <-- przekazanie self jako parent
            airfoil_names = [airfoil.infos['name'] for airfoil in globals.PROJECT.project_airfoils]
            airfoil_dropdown.addItems(airfoil_names)
            current_name = getattr(element_obj.airfoil, 'infos', {}).get('name', '')
            if current_name in airfoil_names:
                airfoil_dropdown.setCurrentText(current_name)
            elif airfoil_names:
                airfoil_dropdown.setCurrentIndex(0)
            airfoil_dropdown.currentTextChanged.connect(lambda new_value, r=row: self.update_airfoil_value(r, new_value))
            self.setCellWidget(row, 1, airfoil_dropdown)
            nominal_value = QTableWidgetItem(current_name)
            nominal_value.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, nominal_value)
        
        # Special handling for Segment to show available anchors in ComboBox
        if hasattr(element_obj, 'anchor'):
            # Airfoil ComboBox row
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem('anchor'))
            anchor_dropdown = QtWidgets.QComboBox(self)  # <-- przekazanie self jako parent
            anchor_names = ['G0', 'G1']
            anchor_dropdown.addItems(anchor_names)
            current_name = getattr(element_obj, 'anchor', '')
            if current_name in anchor_names:
                anchor_dropdown.setCurrentText(current_name)
            elif anchor_names:
                anchor_dropdown.setCurrentIndex(0)
            anchor_dropdown.currentTextChanged.connect(lambda new_value, r=row: self.update_airfoil_value(r, new_value))
            self.setCellWidget(row, 1, anchor_dropdown)
            nominal_value = QTableWidgetItem(current_name)
            nominal_value.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, nominal_value)
        
        # Default: show all params of element
        if hasattr(element_obj, 'params'):
            # Params rows
            for key, value in element_obj.params.items():
                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, QTableWidgetItem(key))
                self.add_editable_row(row, value)
                nominal_value = QTableWidgetItem(str(value))
                nominal_value.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 2, nominal_value)

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

                    print(f'Segment at index: {grandparent_index}:{parent_index}:{item_index}')

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

                    print(f'WNGWB > Save_state > Segment at index: {grandparent_index}:{parent_index}:{item_index}')
                    
                    element_item = globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index]
                    globals.PROJECT.project_components[grandparent_index].wings[parent_index].build_connection()

                if parent_item and not grandparent_item:

                    item_index = parent_item.indexOfChild(selected_item)
                    parent_index = self.tree_menu.indexOfTopLevelItem(parent_item)

                    print(f'WNGWB > Save_state > Wing at index: {parent_index} >>> {item_index}')

                    element_item = globals.PROJECT.project_components[parent_index].wings[item_index]
                    globals.PROJECT.project_components[parent_index].wings[item_index].build_connection()

                if not parent_item and not grandparent_item:

                    item_index = self.tree_menu.indexOfTopLevelItem(selected_item)

                    print(f'WNGWB > Save_state > Component at index: {item_index}')

                    element_item = globals.PROJECT.project_components[item_index]
                    for item in element_item.wings:
                        item.build_connection()

                # Update the airfoil object with table data
                for row in range(self.rowCount()):
                    key = self.item(row, 0).text()
                    # Retrieve the value from the QLineEdit inside the custom widget
                    cell_widget = self.cellWidget(row, 1)
                    if cell_widget:
                        combo_box = self.cellWidget(row, 1) if isinstance(self.cellWidget(row, 1), QtWidgets.QComboBox) else None
                        line_edit = cell_widget.findChild(QLineEdit)

                        #print(f'Combobox: {combo_box}')

                        if combo_box:
                            value = combo_box.currentText()
                            if key == "anchor":
                                element_item.anchor = value
                                print(f"WNGWB > Save_state > Saved anchor: {value}")
                            if key == "airfoil":
                                selected_name = combo_box.currentText()
                                matched_airfoil = next(
                                    (a for a in globals.PROJECT.project_airfoils if a.infos["name"] == selected_name),
                                    None
                                )
                                if matched_airfoil:
                                    element_item.airfoil = matched_airfoil
                                    print(f"WNGWB > Save_state > Set airfoil: {matched_airfoil.infos['name']}")
                                else:
                                    print(f"WNGWB > Save_state > WARNING: Airfoil '{selected_name}' not found!")
                            else:
                                print(f"WNGWB > Save_state > Skipped unknown ComboBox: {key}")

                        elif line_edit:
                            try:
                                value = float(line_edit.text())
                                if hasattr(element_item, "params") and key in element_item.params:
                                    element_item.params[key] = value
                                else:
                                    setattr(element_item, key, value)
                            except ValueError:
                                print(f"WNGWB > Save_state > Invalid value for parameter '{key}', skipping update.")
                
                print(f"WNGWB > Save_state > Saved params of: {element_item.infos['name']}")
                try:
                    globals.PROJECT.project_components[grandparent_index].wings[parent_index].segments[item_index].transform_airfoil(grandparent_index, parent_index, item_index)
                except:
                    print('WARNING: No airfoil to transform')

                # Optionally, update the tree menu display
                selected_item.setText(0, f"{element_item.infos['name']}*")