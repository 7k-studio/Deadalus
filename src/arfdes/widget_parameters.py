'''

Copyright (C) 2026 Jakub Kamyk

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
import logging
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,  QHBoxLayout,
    QTableWidget, QTableWidgetItem, 
    QPushButton, QLineEdit, QHeaderView, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal


class TableParameters(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)
    parametersChanged = pyqtSignal(object)

    def __init__(self, program=None, project=None, parent=None, open_gl=None, airfoils_menu=None, stat_table=None, ):
        super(TableParameters, self).__init__(parent)
        self.setMinimumSize(200, 300)
        self.DEADALUS = program
        self.PROJECT = project
        self.open_gl = open_gl
        self.airfoils_menu = airfoils_menu
        self.stat_table = stat_table
        # keep reference to the internal QTreeWidget (used to find top-level selection)
        self.tree_menu = None
        if airfoils_menu is not None:
            # airfoils_menu is TreeAirfoil instance; its tree widget is .tree
            self.tree_menu = getattr(airfoils_menu, "tree", None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Up_ref_points = None  # Add attribute to store Up_ref_points
        self.Dwn_ref_points = None  # Add attribute to store Dwn_ref_points
        self.init_tabele()

    def init_tabele(self, params=None):
        # Initial Parameters
        self.params = {}

        # Properly initialize the table without overwriting `self`
        self.setRowCount(len(self.params))
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Parameter", "Value", "Nominal", "Unit"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        #self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnWidth(0, 70) # Set width of the first column
        self.setColumnWidth(1, 100)  # Set width of the second column
        self.setColumnWidth(2, 70)  # Set width of the third column
        self.setColumnWidth(3, 50)  # Set width of the forth column

    def set_reference_points(self, up_ref_points, dwn_ref_points):
        """Set reference points for plotting."""
        self.Up_ref_points = up_ref_points
        self.Dwn_ref_points = dwn_ref_points

    def add_editable_row(self, row, value):
        """Add an editable row with up/down buttons and input field."""
        # Create a custom widget for editing with up/down buttons and input
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        # Input field for direct keyboard input
        value = format(value, '.4f')  # Format value to 4 decimal places
        value_input = QLineEdit(str(value))
        value_input.setAlignment(Qt.AlignCenter)
        #value_input.setFixedWidth(70)
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

    def update_value_from_input(self, row, value_input):
        # Update parameter from the input field
        param_name = self.item(row, 0).text()
        try:
            new_value = float(value_input.text())
            self.airfoil['params'][param_name] = new_value
            # Pass reference points to update_plot
            self.save_current_airfoil_state()
        except ValueError:
            # Restore the last valid value if input is invalid
            self.logger.warning("Invalid input, restoring last valid value.")
            value_input.setText(str(self.airfoil['params'][param_name]))
    
    def _adjust_value_with_modifiers(self, row, direction):
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ShiftModifier:
            delta = 1.0
        elif modifiers & Qt.ControlModifier:
            delta = 0.01
        else:
            delta = 0.1
        self.adjust_value(row, direction * delta)

    def adjust_value(self, row, delta):
        # Adjust parameter value by delta
        param_name = self.item(row, 0).text()
        current_value = self.airfoil['params'][param_name]
        new_value = current_value + delta
        # Update value
        self.airfoil['params'][param_name] = new_value
        # Update the input field display
        cell_widget = self.cellWidget(row, 1)
        value_input = cell_widget.findChild(QLineEdit)
        new_value = format(new_value, '.4f')  # Format value to 2 decimal places
        value_input.setText(str(new_value))
        # Pass reference points to update_plot
        self.save_current_airfoil_state()  # Save changes to the airfoil list

    def update(self, airfoil_obj=None):
        """Populate the table with data from an airfoil object."""
        
        self.setRowCount(0)  # Clear existing rows
        self.logger.debug("THE PARAMETERS SHOULD CLEAR NOW")
        if airfoil_obj:
            param_units = airfoil_obj.unit.items()

            self.logger.debug('Populating table')

            for key, value in airfoil_obj.params.items():
                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, QTableWidgetItem(key))
                self.add_editable_row(row, value)
                value = format(value, '.4f')
                nominal_value = QTableWidgetItem(str(value))
                nominal_value.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 2, nominal_value)  # Optional: Add nominal value column
                unit = airfoil_obj.unit.get(key, '')
                if unit == 'length':
                    unit = globals.DEADALUS.preferences['general']['units'].get('length', 'm')
                if unit == 'angle':
                    unit = globals.DEADALUS.preferences['general']['units'].get('angle', 'rad')
                unit_value = QTableWidgetItem(str(unit))
                unit_value.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, 3, unit_value)

    def display_selected_airfoil(self, item, column=None):
        """Display the selected airfoil's data in the table.
        Accepts (item, column) from QTreeWidget.itemClicked. If a child node was clicked,
        show parameters for the corresponding component (LE/TE/PS/SS).
        """
        if self.tree_menu is None:
            self.logger.warning("No tree_menu assigned to TableParameters")
            return

        # Determine if a child node was clicked
        component_attr = None
        if item.parent():
            # child clicked -> map its label to component attribute
            child_label = item.text(0).strip().lower()
            mapping = {
                "leading edge": "LE", "leading_edge": "LE", "leadingedge": "LE", "le": "LE",
                "trailing edge": "TE", "trailing_edge": "TE", "trailingedge": "TE", "te": "TE",
                "pressure side": "PS", "pressure_side": "PS", "pressureside": "PS", "ps": "PS",
                "suction side": "SS", "suction_side": "SS", "suctionside": "SS", "ss": "SS",
            }
            component_attr = mapping.get(child_label)
            top_item = item.parent()
        else:
            top_item = item

        index = self.tree_menu.indexOfTopLevelItem(top_item)
        if index == -1:
            self.logger.debug("Top-level item index not found for selected item")
            return

        selected_airfoil = self.PROJECT.airfoils[index]

        if component_attr:
            # Show component parameters
            selected_component = getattr(selected_airfoil, component_attr, None)
            if selected_component:
                self.update(selected_component)
                # store component state for edits (child has 'params' and 'unit')
                self.airfoil = {key: value for key, value in vars(selected_component).items()}
                # Tell viewport about parent airfoil and (optionally) component
                if self.open_gl:
                    try:
                        self.open_gl.set_airfoil_to_display(selected_airfoil)
                        if hasattr(self.open_gl, "set_component_to_display"):
                            self.open_gl.set_component_to_display(selected_airfoil, component_attr)
                        # force repaint so component selection is visible
                        self.open_gl.update()
                    except Exception:
                        self.logger.exception("Failed to update viewport for component")
                self.logger.debug(f"Displayed component '{component_attr}' parameters")
            else:
                self.logger.warning(f"Component '{component_attr}' not found on selected airfoil")
        else:
            # Top-level airfoil selected -> show overall params
            self.update(selected_airfoil)
            self.airfoil = {key: value for key, value in vars(selected_airfoil).items() if key != "info"}
            if self.open_gl:
                try:
                    self.open_gl.set_airfoil_to_display(selected_airfoil)
                except Exception:
                    self.logger.exception("Failed to set airfoil to viewport")
            self.logger.debug('Displayed parent airfoil parameters')

    def save_current_airfoil_state(self):
        """Overwrite the current table data into the selected airfoil object."""
        selected_item = self.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # If the current item is a child, climb to parent and detect component
        component_attr = None
        top_item = selected_item
        if selected_item.parent():
            child_label = selected_item.text(0).strip().lower()
            mapping = {
                "leading edge": "LE", "leading_edge": "LE", "leadingedge": "LE", "le": "LE",
                "trailing edge": "TE", "trailing_edge": "TE", "trailingedge": "TE", "te": "TE",
                "pressure side": "PS", "pressure_side": "PS", "pressureside": "PS", "ps": "PS",
                "suction side": "SS", "suction_side": "SS", "suctionside": "SS", "ss": "SS",
            }
            component_attr = mapping.get(child_label)
            top_item = selected_item.parent()

        airfoil_index = self.tree_menu.indexOfTopLevelItem(top_item)
        if airfoil_index == -1:
            return  # Invalid selection

        current_airfoil = self.PROJECT.airfoils[airfoil_index]

        # Decide target object (parent airfoil or one of its components)
        if component_attr:
            target = getattr(current_airfoil, component_attr, None)
        else:
            target = current_airfoil

        if target is None:
            self.logger.error("No target object to save parameters into.")
            return

        # Update the target's params from the table rows
        for row in range(self.rowCount()):
            param_name = self.item(row, 0).text()
            cell_widget = self.cellWidget(row, 1)
            if not cell_widget:
                continue
            value_input = cell_widget.findChild(QLineEdit)
            if not value_input:
                continue
            try:
                value = float(value_input.text())
            except ValueError:
                self.logger.error(f"Invalid value for parameter '{param_name}', skipping update.")
                continue
            # Write back only if target has params dict
            try:
                target.params[param_name] = value
            except Exception:
                # top-level airfoil stores params directly on .params (same), so this is safe
                try:
                    target[param_name] = value
                except Exception:
                    self.logger.exception(f"Failed to save parameter '{param_name}'")

        # Update tree label to indicate modification and force viewport repaint
        current_airfoil.update()

        top_item.setText(0, f"{current_airfoil.name}*")
        # Notify listeners that parameters changed
        self.parametersChanged.emit(current_airfoil)
        try:
            # ensure viewport reflects changes
            self.open_gl.set_airfoil_to_display(current_airfoil)
            if component_attr and hasattr(self.open_gl, "set_component_to_display"):
                self.open_gl.set_component_to_display(current_airfoil, component_attr)
            self.open_gl.update()
        except Exception:
            self.logger.exception("Failed to request viewport update after saving")

