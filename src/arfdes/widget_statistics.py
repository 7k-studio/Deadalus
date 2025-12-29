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
import logging
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout,
    QPushButton, QLineEdit, QHeaderView, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal

import src.globals as globals  # Import from globals.py


class TableStatistics(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, parent=None, open_gl=None, airfoils_menu=None, project=None):
        super(TableStatistics, self).__init__(parent)
        self.setMinimumSize(200, 300)
        self.open_gl = open_gl
        self.project = project
        self.airfoils_menu = airfoils_menu
        # keep reference to the internal QTreeWidget (used to find top-level selection)
        self.tree_menu = None
        if airfoils_menu is not None:
            # airfoils_menu is TreeAirfoil instance; its tree widget is .tree
            self.tree_menu = getattr(airfoils_menu, "tree", None)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.Up_ref_points = None  # Add attribute to store Up_ref_points
        self.Dwn_ref_points = None  # Add attribute to store Dwn_ref_points
        self.init_tabele()

    def init_tabele(self, stats=None):
        # Initial Parameters
        self.stats = {}

        # Properly initialize the table without overwriting `self`
        self.setRowCount(len(self.stats))
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Statistic", "Value", "Nominal", "Unit"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        #self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnWidth(1, 100)  # Set minimum width for column 2

    def set_reference_points(self, up_ref_points, dwn_ref_points):
        """Set reference points for plotting."""
        self.Up_ref_points = up_ref_points
        self.Dwn_ref_points = dwn_ref_points

    def populate_table(self, airfoil_obj):
        """Populate the table with data from an airfoil object."""
        self.setRowCount(0)  # Clear existing rows
        param_units = airfoil_obj.unit.items()

        self.logger.debug('Populating table')

        for key, value in airfoil_obj.stats.items():
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(key))

            value = format(value, '.4f')

            airfoil_value = QTableWidgetItem(str(value))
            airfoil_value.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 1, airfoil_value)  # Optional: Add nominal value column

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

        selected_airfoil = globals.PROJECT.project_airfoils[index]

        # if component_attr:
        #     # Show component parameters
        #     selected_component = getattr(selected_airfoil, component_attr, None)
        #     if selected_component:
        #         self.populate_table(selected_component)
        #         # store component state for edits (child has 'params' and 'unit')
        #         self.airfoil = {key: value for key, value in vars(selected_component).items()}
        #         # Tell viewport about parent airfoil and (optionally) component
        #         if self.open_gl:
        #             try:
        #                 self.open_gl.set_airfoil_to_display(selected_airfoil)
        #                 if hasattr(self.open_gl, "set_component_to_display"):
        #                     self.open_gl.set_component_to_display(selected_airfoil, component_attr)
        #                 # force repaint so component selection is visible
        #                 self.open_gl.update()
        #             except Exception:
        #                 self.logger.exception("Failed to update viewport for component")
        #         self.logger.debug(f"Displayed component '{component_attr}' parameters")
        #     else:
        #         self.logger.warning(f"Component '{component_attr}' not found on selected airfoil")
        # else:
        #     # Top-level airfoil selected -> show overall params
        self.populate_table(selected_airfoil)
        self.airfoil = {key: value for key, value in vars(selected_airfoil).items() if key != "infos"}
        if self.open_gl:
            try:
                self.open_gl.set_airfoil_to_display(selected_airfoil)
            except Exception:
                self.logger.exception("Failed to set airfoil to viewport")
        self.logger.debug('Displayed parent airfoil parameters')

