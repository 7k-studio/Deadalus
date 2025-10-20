from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QFont
import os

class LogViewer(QTextEdit):
    def __init__(self, log_file, parent=None):
        super().__init__(parent)
        self.log_file = log_file
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.last_position = 0  # Track the last read position in the file

        # Set monospaced font
        # font = QFont("Courier New")
        # font.setStyleHint(QFont.Monospace)
        # font.setPointSize(10)  # Adjust font size as needed
        # self.setFont(font)

        # Timer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log)
        self.timer.start(1000)  # Check for updates every second

        self.update_log()

    def update_log(self):
        if not os.path.exists(self.log_file):
            self.setPlainText("Log file not found.")
            return

        try:
            with open(self.log_file, 'r') as file:
                lines = file.readlines()

                # Skip the first 11 lines
                new_content = ''.join(lines[11:])

                # Update only if the content has changed
                if self.toPlainText() != new_content:
                    self.setPlainText("")  # Clear the console
                    for line in lines[11:]:
                        self.append_colored_line(line.strip())
        except Exception as e:
            self.setPlainText(f"Error reading log file: {e}")

    def append_colored_line(self, line):
        format = QTextCharFormat()
        if "ERROR" in line:
            format.setForeground(QColor("red"))
        elif "WARNING" in line:
            format.setForeground(QColor("orange"))
        elif "DEBUG" in line:
            format.setForeground(QColor("blue"))
        else:
            format.setForeground(QColor("black"))

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        cursor.insertText(line + '\n', format)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
