from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from arfdes.airfoil_designer import AirfoilDesigner  # Import the AirfoilDesigner class from the correct module
from wngwb.main_window import MainWindow
import globals


class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.AIRFLOW = parent
        self.setWindowTitle("Splash Screen")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        #self.setAttribute(Qt.WA_TranslucentBackground, True)
        #self.setAttribute(Qt.WA_DeleteOnClose, True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add splash image
        splash_label = QLabel(self)
        pixmap = QPixmap("src/splash/splash.png")
        if pixmap.isNull():
            print("Error: 'splash.png' not found or invalid path.")
        splash_label.setPixmap(pixmap)
        splash_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(splash_label)

        program_label = QLabel('AirFoil & Lifting Objects Workbench')
        program_label.setStyleSheet("font-size: 12px; font-weight: regular; color: black;")
        layout.addWidget(program_label, alignment=Qt.AlignLeft | Qt.AlignTop)

        version_label = QLabel('v{}'.format(self.AIRFLOW.program_version))
        version_label.setStyleSheet("font-size: 12px; font-weight: regular; color: black;")
        layout.addWidget(version_label, alignment=Qt.AlignLeft | Qt.AlignTop)

        # Add buttons
        button_layout = QHBoxLayout()
        button1 = QPushButton("New Project")
        button1.setStyleSheet("background-color: lightblue;")
        button1.clicked.connect(self.open_airfoil_designer)
        button1.setFixedSize(220, 30)  # Set fixed size for the button

        button2 = QPushButton("Open Project")
        button2.setStyleSheet("background-color: lightgreen;")
        button2.clicked.connect(self.open_wing_designer)
        button2.setFixedSize(220, 30)  # Set fixed size for the button

        button_layout.addWidget(button1)
        button_layout.addWidget(button2)
        layout.addLayout(button_layout)

        # Center the buttons
        button_layout.setAlignment(Qt.AlignCenter)

        # Add close button
        close_button = QPushButton(self)
        icon = QIcon("src/splash/cross.png")
        if icon.isNull():
            print("Error: 'cross.png' not found or invalid path.")
        close_button.setIcon(icon)
        close_button.setFixedSize(30, 30)
        close_button.setStyleSheet("border: none;")
        close_button.clicked.connect(self.close)

        # Add close button to the top-right corner
        close_layout = QHBoxLayout()
        close_layout.addWidget(close_button)
        close_layout.setAlignment(Qt.AlignRight)
        layout.insertLayout(0, close_layout)  # Insert at the top of the main layout

    def open_airfoil_designer(self):
        """Open the AirfoilDesigner window."""
        self.PROJECT = globals.PROJECT.newProject()
        self.airfoil_designer_window = AirfoilDesigner(globals.AIRFLOW, globals.PROJECT)  # Pass airfoil_list
        self.airfoil_designer_window.show()
        self.close()

    def open_wing_designer(self):
        """Open the WingDesigner window."""
        
        #msg = QMessageBox(self)
        #msg.setWindowTitle("Wing Module")
        #msg.setText("Wing Module functionality is under development.")
        #msg.setIcon(QMessageBox.Information)
        #msg.setStandardButtons(QMessageBox.Ok)
        #msg.exec_()
        self.PROJECT = globals.newProject()
        self.airfoil_designer_window = MainWindow()  # Pass airfoil_list
        self.airfoil_designer_window.show()
        self.close()

        # Add a button or menu action to open the AirfoilDesigner
        #self.open_airfoil_designer_action = QAction("Open Airfoil Designer", self)
        #self.open_airfoil_designer_action.triggered.connect(self.open_airfoil_designer)
        #self.menu_bar.addAction(self.open_airfoil_designer_action)

    #def open_airfoil_designer(self):
        """Open the AirfoilDesigner window."""
        #self.airfoil_designer = AirfoilDesigner(airfoil_list)  # Pass airfoil_list
        #self.airfoil_designer.show()
