import sys
import math
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QWidget, QHBoxLayout, QLineEdit, QFormLayout, QLabel, QMenuBar, QAction, QFileDialog, QTreeWidget, QTreeWidgetItem, QTextEdit, QStackedWidget
from PyQt5.QtCore import Qt

import numpy as np

import src.obj.airfoil as airfoil
import src.wngwb.tools_wing as tools_wing
import src.utils.dxf as dxf
import random

from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy
)
from PyQt5.QtGui import QIcon

from src.opengl.viewport3d import ViewportOpenGL
from OpenGL.GL import *  # Import OpenGL functions
from OpenGL.GLU import *  # Import GLU functions (e.g., gluPerspective)

from src.wngwb.menu_bar import MenuBar
from src.wngwb.widget_tree import TreeMenu
from src.wngwb.widget_tabele import Tabele
from src.wngwb.widget_tree import TreeMenu  # Import TreeMenu

#from globals import airfoil_list  # Import from globals.py
import src.globals as globals  # Import from globals.py
#from designer.airfoil_designer import AirfoilDesigner  # Import AirfoilDesigner
#from wngwb import tools_wing  # Import add_component_to_tree
from datetime import date

Trans = tools_wing

class MainWindow(QMainWindow):

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(MainWindow, self).__init__(parent, flags)
        print("Opening Wing Workbench")
        self.setWindowTitle(globals.AIRFLOW.program_name)
        self.setWindowIcon(QIcon('src/assets/logo.png'))
        self.window_width, self.window_height = 1200, 800
        self.setMinimumSize(self.window_width, self.window_height)

        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)
        content_layout = QHBoxLayout()

        self.setCentralWidget(central_widget)

        # Add the OpenGL viewport to the inner splitter
        self.viewport = QWidget()
        self.open_gl = ViewportOpenGL(parent=self.viewport)
        viewport_layout = QVBoxLayout(self.viewport)
        viewport_layout.addWidget(self.open_gl)
        #self.viewport.setMinimumWidth(500)

        # Create the menu bar
        self.menu_bar = MenuBar(self)  # Use the MenuBar class
        self.setMenuBar(self.menu_bar)

        # Use the TreeMenu class directly
        self.tree_menu = TreeMenu(self)
        self.tree_menu.setMinimumWidth(200)  # Nie pozwól schować całkowicie
        self.tree_menu.setMaximumWidth(200)

        left_layout = QHBoxLayout()
        left_layout.addWidget(self.tree_menu)

        # Add the Tabele module to the inner splitter
        self.tabele = Tabele(self, tree_menu=self.tree_menu, project=globals.PROJECT)
        self.tabele.setMinimumWidth(300)
        self.tabele.setMaximumWidth(300)  # Opcjonalnie: ogranicz maksymalną szerokość
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.tabele)

        #content_layout.addWidget(self.tree_menu)
        content_layout.addWidget(self.viewport, stretch=10)
        #content_layout.addWidget(self.tabele)

        main_layout.addLayout(left_layout)
        main_layout.addLayout(content_layout)
        main_layout.addLayout(right_layout)

        if not globals.PROJECT.project_components:
            # Initialize with a default airfoil
            self.menu_bar.addComponent("Default Component")

        # Connect tree widget selection to display function
        self.tree_menu.itemClicked.connect(self.tabele.display_selected_element)

    def initializeOpenGL(self):
        """Initialize OpenGL settings."""
        glEnable(GL_DEPTH_TEST)  # Enable depth testing
        glClearColor(0.01, 0.01, 0.01, 1.0)  # Set background color

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

