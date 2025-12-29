"""
Small reusable top toolbar widget for the Airfoil Designer.
Provides easy API to add buttons with optional icons and keyboard shortcuts.
"""

from PyQt5.QtWidgets import QToolBar, QAction, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence
import src.globals as globals


class ToolBar(QToolBar):
    """A QToolBar placed in the QMainWindow top area under the menu bar.

    Use add_tool_button(text, icon_path=None, shortcut=None, callback=None)
    to add actions (which are presented as toolbar buttons) with optional keyboard shortcuts.
    """

    def __init__(self, parent=None, height=75):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(height)
        self.setMovable(False)
        self.setFloatable(False)
        # Show text beside icons so labels are visible
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32,32))
        self.setStyleSheet(f"""
            QToolBar {{ background-color: rgb(255,255,255); }}
            QToolBar QToolButton {{
                min-width: 80px;
                padding: 6px;
                margin: 2px;
                border-radius: 6px;
                text-align: center;
            }}
            QToolBar QToolButton:hover {{
                background-color: rgba(0,0,0,0.05);
            }}
            QToolBar QToolButton:pressed {{
                background-color: rgba(0,0,0,0.10);
            }}
            QToolBar QToolButton::menu-indicator {{ image: none; }}
            """)


        # Add tool buttons wired to the existing toggle methods (shortcuts shown in tooltip)
        self.add_tool_button("Add Airfoil",    icon_path="src/assets/IconPack/AddAirfoil.svg",    shortcut="Ctrl+1", ) # callback=self.toggle_airfoil)
        self.add_tool_button("Append Airfoil", icon_path="src/assets/IconPack/AppendAirfoil.svg", shortcut="Ctrl+2", ) # callback=self.toggle_parameters)
        self.add_tool_button("Delete Airfoil", icon_path="src/assets/IconPack/DeleteAirfoil.svg", shortcut="Ctrl+3", ) # callback=self.toggle_reference)
        self.add_tool_button("Flip Airfoil",   icon_path="src/assets/IconPack/FlipAirfoil.svg",   shortcut="Ctrl+4", ) # callback=self.toggle_statistics)
        self.add_tool_button("Save Airfoil",   icon_path="src/assets/IconPack/SaveAirfoil.svg",   shortcut="Ctrl+5", ) # callback=self.toggle_description)

        def _rgb(c):
            if isinstance(c, (tuple, list)):
                return ",".join(str(x) for x in c)
            return c

        self.setStyleSheet(f"background-color: rgb(255,255,255);")

    def add_tool_button(self, text, icon_path=None, shortcut=None, callback=None):
        """Add an action to the toolbar.

        - text: label shown on the tool button
        - icon_path: optional path for icon
        - shortcut: optional string understood by QKeySequence (e.g., 'Ctrl+1')
        - callback: callable to connect to action triggered

        Returns the created QAction.
        """
        action = QAction(QIcon(icon_path) if icon_path else QIcon(), text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        if callback:
            action.triggered.connect(callback)
        self.addAction(action)
        # Keep accessibility tooltip showing shortcut
        if shortcut:
            action.setToolTip(f"{text} ({shortcut})")
        return action
