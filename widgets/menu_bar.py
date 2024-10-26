# File path: ./widgets/menu_bar.py
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenuBar, QMenu, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menu()

    def init_menu(self):
        # Members Menu
        member_menu = self.addMenu("Members")
        add_member_action = QAction("Add Member", self)
        add_member_action.triggered.connect(self.on_add_member)
        member_menu.addAction(add_member_action)

        # File Menu
        file_menu = self.addMenu("File")
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.on_settings)
        file_menu.addAction(settings_action)

    def on_add_member(self):
        # Signal or placeholder for adding member functionality
        if self.parent():
            self.parent().add_member_dialog()

    def on_settings(self):
        # Signal or placeholder for settings functionality
        if self.parent():
            self.parent().open_settings_dialog()
