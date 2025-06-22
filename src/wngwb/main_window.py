import sys
import math
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout, QLabel, QMenuBar, QAction, QFileDialog, QTreeWidget, QTreeWidgetItem, QTextEdit, QStackedWidget
from PyQt5.QtCore import Qt

import numpy as np

import obj.aero
import utils.tools_wing
import utils.dxf
import random

from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QPushButton
)

from opengl.viewport import ViewportOpenGL
from OpenGL.GL import *  # Import OpenGL functions
from OpenGL.GLU import *  # Import GLU functions (e.g., gluPerspective)

from wngwb.menu_bar import MenuBar
from wngwb.widget_tree import TreeMenu
from wngwb.widget_tabele import Tabele

from wngwb.widget_tree import TreeMenu  # Import TreeMenu

#from globals import airfoil_list  # Import from globals.py
import globals  # Import from globals.py
#from designer.airfoil_designer import AirfoilDesigner  # Import AirfoilDesigner
from utils import tools_wing  # Import add_component_to_tree
from datetime import date

Trans = utils.tools_wing

class MainWindow(QMainWindow):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent, flags)
        self.setWindowTitle(globals.AIRFLOW.program_name)
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create the main layout with a splitter
        main_layout = QVBoxLayout(self.central_widget)

        # Set margins and spacing to zero for the main layout
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        #main_layout.setSpacing(0)  # Remove spacing between widgets

        # Outer splitter to divide TreeMenu and the rest
        self.outer_splitter = QSplitter(Qt.Horizontal)

        # Create the menu bar
        self.menu_bar = MenuBar(self)  # Use the MenuBar class
        self.setMenuBar(self.menu_bar)

        # Use the TreeMenu class directly
        self.tree_menu = TreeMenu(self)  # Use the TreeMenu class
        self.tree_menu.setMinimumWidth(100)  # Set minimum width for TreeMenu
        self.outer_splitter.addWidget(self.tree_menu)

        # Inner splitter to divide Viewport and Tabele
        self.inner_splitter = QSplitter(Qt.Horizontal)

        # Add the OpenGL viewport to the inner splitter
        self.viewport = QWidget()
        self.open_gl = ViewportOpenGL(parent=self.viewport)
        viewport_layout = QVBoxLayout(self.viewport)
        viewport_layout.addWidget(self.open_gl)
        self.viewport.setMinimumWidth(500)  # Set minimum width for Viewport
        self.inner_splitter.addWidget(self.viewport)

        # Add the Tabele module to the inner splitter
        self.tabele = Tabele(self, tree_menu=self.tree_menu, project=globals.PROJECT)
        self.tabele.setMinimumWidth(100)  # Set minimum width for Tabele
        self.inner_splitter.addWidget(self.tabele)

        # Add the inner splitter to the outer splitter
        self.outer_splitter.addWidget(self.inner_splitter)

        # Add the outer splitter to the main layout
        main_layout.addWidget(self.outer_splitter)

        # Set the initial splitter sizes
        self.outer_splitter.setSizes([300, 900])
        self.inner_splitter.setSizes([700, 200])

        if not globals.PROJECT.project_components:
            # Initialize with a default airfoil
            self.menu_bar.addComponent("Default Component")

        # Connect tree widget selection to display function
        self.tree_menu.itemClicked.connect(self.tabele.display_selected_element)

    def initializeOpenGL(self):
        """Initialize OpenGL settings."""
        glEnable(GL_DEPTH_TEST)  # Enable depth testing
        glClearColor(0.1, 0.1, 0.1, 1.0)  # Set background color

    def resizeGL(self, w, h):
        """Handle OpenGL viewport resizing."""
        if h == 0:
            h = 1  # Prevent division by zero
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h, 0.1, 50.0)  # Set perspective projection
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the OpenGL scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Add rendering logic here
        
