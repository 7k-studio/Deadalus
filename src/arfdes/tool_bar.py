"""
Small reusable top toolbar widget for the Airfoil Designer.
Provides easy API to add buttons with optional icons and keyboard shortcuts.
"""

from PyQt5.QtWidgets import QToolBar, QAction, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence


class ToolBar(QToolBar):
    """A QToolBar placed in the QMainWindow top area under the menu bar.

    Use add_tool_button(text, icon_path=None, shortcut=None, callback=None)
    to add actions (which are presented as toolbar buttons) with optional keyboard shortcuts.
    """

    def __init__(self, program=None, project=None, parent=None, height=75):
        super().__init__(parent)
        self.DAEDALUS = program
        self.PROJECT = project
        self.AIRFOILDESIGNER = parent
        self.setFixedHeight(height)
        self.setMovable(False)
        self.setFloatable(False)
        # Show text beside icons so labels are visible
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(32,32))
        
        # Add tool buttons wired to the existing toggle methods (shortcuts shown in tooltip)
        self.add_tool_button("New Airfoil",    icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/AddAirfoil.svg",    shortcut="Shift+N", callback=self.AIRFOILDESIGNER.newAirfoil)
        self.add_tool_button("Append Airfoil", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/AppendAirfoil.svg", shortcut="Shift+A", callback=self.AIRFOILDESIGNER.appendAirfoil)
        self.add_tool_button("Delete Airfoil", icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/DeleteAirfoil.svg", shortcut="Shift+X", callback=self.AIRFOILDESIGNER.deleteAirfoil)
        self.add_tool_button("Flip Airfoil",   icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/FlipAirfoil.svg",   shortcut="Shift+F", callback=self.AIRFOILDESIGNER.flipAirfoil)
        self.add_tool_button("Save Airfoil",   icon_path=f"{self.DAEDALUS.color_scheme['pathToIcons']}/SaveAirfoil.svg",   shortcut="Shift+S", callback=self.AIRFOILDESIGNER.saveAirfoil)

        def _rgb(c):
            if isinstance(c, (tuple, list)):
                return ",".join(str(x) for x in c)
            return c

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
