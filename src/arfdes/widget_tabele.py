from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHBoxLayout,
    QPushButton, QLineEdit, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from arfdes.tools_airfoil import add_airfoil_to_tree

import globals  # Import from globals.py


class Tabele(QTableWidget):
    referenceStatus = pyqtSignal(bool, str)

    def __init__(self, parent=None, canvas=None, tree_menu=None, project=None):
        super(Tabele, self).__init__(parent)
        self.canvas = canvas
        self.project = project
        #self.airfoils_list = airfoils_list
        self.tree_menu = tree_menu
        self.Up_ref_points = None  # Add attribute to store Up_ref_points
        self.Dwn_ref_points = None  # Add attribute to store Dwn_ref_points
        self.init_tabele()

    def init_tabele(self, params=None):
        # Initial Parameters
        self.params = {}

        # Properly initialize the table without overwriting `self`
        self.setRowCount(len(self.params))
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Parameter", "Value", "Nominal"])
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        #self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnWidth(1, 100)  # Set minimum width for column 2

    def set_reference_points(self, up_ref_points, dwn_ref_points):
        """Set reference points for plotting."""
        self.Up_ref_points = up_ref_points
        self.Dwn_ref_points = dwn_ref_points

    def add_editable_row(self, row, value):
        # Create a custom widget for editing with up/down buttons and input
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        # Input field for direct keyboard input
        value = format(value, '.5f')  # Format value to 2 decimal places
        value_input = QLineEdit(str(value))
        value_input.setAlignment(Qt.AlignCenter)
        #value_input.setFixedWidth(70)
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
    
    def update_value_from_input(self, row, value_input):
        # Update parameter from the input field
        param_name = self.item(row, 0).text()
        try:
            new_value = float(value_input.text())
            self.airfoil['params'][param_name] = new_value
            # Pass reference points to update_plot
            #self.canvas.update_plot(self.airfoil, self.Up_ref_points, self.Dwn_ref_points)
            self.save_current_airfoil_state()
        except ValueError:
            # Restore the last valid value if input is invalid
            print("WARNING: Invalid input, restoring last valid value.")
            value_input.setText(str(self.airfoil['params'][param_name]))

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
        new_value = format(new_value, '.5f')  # Format value to 2 decimal places
        value_input.setText(str(new_value))
        # Pass reference points to update_plot
        #self.canvas.update_plot(index, self.Up_ref_points, self.Dwn_ref_points)
        self.save_current_airfoil_state()  # Save changes to the airfoil list

    def populate_table(self, airfoil_obj):
        """Populate the table with data from an airfoil object."""
        self.setRowCount(0)  # Clear existing rows
        for key, value in airfoil_obj.params.items():
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(key))
            self.add_editable_row(row, value)
            nominal_value = QTableWidgetItem(str(value))
            nominal_value.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, nominal_value)  # Optional: Add nominal value column

    def display_selected_airfoil(self, item):
        """Display the selected airfoil's data in the table."""
        index = self.tree_menu.indexOfTopLevelItem(item)
        if index != -1:
            selected_airfoil = self.project.project_airfoils[index]
            self.populate_table(selected_airfoil)
            # Update self.params with the selected airfoil's parameters
            self.airfoil = {key: value for key, value in vars(selected_airfoil).items() if key != "infos"}
            self.canvas.update_plot(index, self.Up_ref_points, self.Dwn_ref_points)  # Update the plot

    def save_current_airfoil_state(self):
        """Overwrite the current table data into the selected airfoil object."""
        selected_item = self.tree_menu.currentItem()
        if not selected_item:
            return  # No airfoil selected

        # Find the corresponding airfoil object
        airfoil_index = self.tree_menu.indexOfTopLevelItem(selected_item)
        if airfoil_index == -1:
            return  # Invalid selection

        current_airfoil = self.project.project_airfoils[airfoil_index]

        # Update the airfoil object with table data
        for row in range(self.rowCount()):
            key = self.item(row, 0).text()
            if key == "params":  # Skip the 'geom' parameter
                # Retrieve the value from the QLineEdit inside the custom widget
                cell_widget = self.cellWidget(row, 1)
                if cell_widget:
                    value_input = cell_widget.findChild(QLineEdit)
                    if value_input:
                        try:
                            value = float(value_input.text())
                            self.params[key] = value
                        except ValueError:
                            print(f"Invalid value for parameter '{key}', skipping update.")
        
        self.canvas.update_plot(airfoil_index, self.Up_ref_points, self.Dwn_ref_points)  # Update the plot
        # Optionally, update the tree menu display
        selected_item.setText(0, f"{current_airfoil.infos['name']}*")

