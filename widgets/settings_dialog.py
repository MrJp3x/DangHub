from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_font_size=16):
        super().__init__(parent)
        self.current_font_size = current_font_size
        self.setWindowTitle("Settings")
        self.init_ui()

    def init_ui(self):
        settings_layout = QVBoxLayout()

        font_label = QLabel("Adjust Font Size:")
        font_label.setStyleSheet("font-size: 16px;")
        settings_layout.addWidget(font_label)

        self.font_input = QLineEdit()
        self.font_input.setPlaceholderText("Enter font size (e.g., 16)")
        self.font_input.setText(str(self.current_font_size))  # Set current font size
        settings_layout.addWidget(self.font_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.apply_settings)
        settings_layout.addWidget(ok_button)

        self.setLayout(settings_layout)

    def apply_settings(self):
        try:
            font_size = int(self.font_input.text())
            if 10 <= font_size <= 30:
                if self.parent():
                    self.parent().update_font_size(font_size)
                self.accept()
            else:
                QMessageBox.warning(self, "Invalid Font Size", "Font size must be between 10 and 30.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for the font size.")
