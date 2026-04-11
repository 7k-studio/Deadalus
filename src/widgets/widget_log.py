from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import QTimer, Qt, QFileSystemWatcher
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QFont
import os
# from src.program import DAEDALUS

class LogViewer(QTextEdit):
    def __init__(self, log_file, parent=None, program=None):
        super().__init__(parent)
        self.log_file = log_file
        self.DAEDALUS = program  # Separate the program reference from the widget parent
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.last_position = 0  # Track the last read position in the file

        # Set monospaced font
        # font = QFont("Courier New")
        # font.setStyleHint(QFont.Monospace)
        # font.setPointSize(10)  # Adjust font size as needed
        # self.setFont(font)

        # File system watcher for instant updates
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self.on_file_changed)
        if os.path.exists(self.log_file):
            self.watcher.addPath(os.path.abspath(self.log_file))

        # Fallback timer for updates in case file watcher fails
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(500)  # Check every 500ms as fallback

        self.update_log()

    def on_file_changed(self, path):
        """Called when file system detects file change"""
        self.update_log()
        # Re-add the path to ensure continued monitoring (needed on some systems)
        if path not in self.watcher.files():
            self.watcher.addPath(path)

    def update_log(self):
        if not os.path.exists(self.log_file):
            self.setPlainText("Log file not found.")
            return

        try:
            with open(self.log_file, 'r') as file:
                lines = file.readlines()

                # Skip the first 11 lines and filter out DEBUG messages
                filtered_lines = [line for line in lines[11:] if "DEBUG" not in line]
                new_content = ''.join(filtered_lines)

                # Update only if the content has changed
                if self.toPlainText() != new_content:
                    self.setPlainText("")  # Clear the console
                    for line in filtered_lines:
                        self.append_colored_line(line.strip())
        except Exception as e:
            self.setPlainText(f"Error reading log file: {e}")

    def append_colored_line(self, line):
        format = QTextCharFormat()
        
        # Default color scheme if program doesn't have one
        default_colors = {
            'LoggerError': '#FF6B6B',
            'LoggerWarning': '#FFD93D',
            'LoggerDebug': '#6BCB77',
            'LoggerMain': '#FFFFFF'
        }
        
        try:
            color_scheme = self.DAEDALUS.color_scheme if self.DAEDALUS else default_colors
        except (AttributeError, TypeError):
            color_scheme = default_colors
        
        if "ERROR" in line:
            format.setForeground(QColor(color_scheme.get('LoggerError', default_colors['LoggerError'])))
        elif "WARNING" in line:
            format.setForeground(QColor(color_scheme.get('LoggerWarning', default_colors['LoggerWarning'])))
        elif "DEBUG" in line:
            format.setForeground(QColor(color_scheme.get('LoggerDebug', default_colors['LoggerDebug'])))
        else:
            format.setForeground(QColor(color_scheme.get('LoggerMain', default_colors['LoggerMain'])))

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        cursor.insertText(line + '\n', format)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def __del__(self):
        """Cleanup file watcher and timer when widget is destroyed"""
        try:
            self.timer.stop()
            self.watcher.fileChanged.disconnect()
        except:
            pass
