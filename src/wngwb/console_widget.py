from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QLabel

class ConsoleWidget(QWidget):
    def __init__(self, parent=None):
        super(ConsoleWidget, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        layout.addWidget(QLabel("Console Output:"))
        layout.addWidget(self.output_area)

        self.input_area = QLineEdit(self)
        self.input_area.setPlaceholderText("Enter command...")
        layout.addWidget(self.input_area)

        self.setLayout(layout)

    def append_output(self, text):
        self.output_area.append(text)

    def get_input(self):
        return self.input_area.text()

    def clear_input(self):
        self.input_area.clear()