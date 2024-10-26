import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QPushButton, QLabel, QLineEdit,
                               QComboBox, QTreeWidget, QTreeWidgetItem,
                               QDialog, QMessageBox)
from PySide6.QtCore import Qt  # Import Qt for setting check states
from widgets.menu_bar import MenuBar
from logic.database_handler import DatabaseHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_handler = DatabaseHandler()  # Instance of DatabaseHandler
        self.setWindowTitle("DangHub")
        self.setGeometry(100, 100, 800, 500)
        self.font_size = 16  # Default font size
        self.init_ui()
        self.load_members()  # Load members from database

    def init_ui(self):
        # Menu Bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Main Layout
        main_layout = QVBoxLayout()

        # Tree Widget for Members
        self.member_tree_widget = QTreeWidget()
        self.member_tree_widget.setStyleSheet(f"font-size: {self.font_size}px;")
        self.member_tree_widget.setColumnCount(2)  # Columns: Member, Balance
        self.member_tree_widget.setHeaderLabels(["Member", "Balance"])
        self.member_tree_widget.itemChanged.connect(self.update_balance)  # Connect itemChanged signal
        label = QLabel("Select Members for Dang:")
        label.setStyleSheet(f"font-size: {self.font_size}px;")
        main_layout.addWidget(label)
        main_layout.addWidget(self.member_tree_widget)

        # ComboBox for selecting the payer (Mother Kharj)
        payer_label = QLabel("Select Payer (Mother Kharj):")
        payer_label.setStyleSheet(f"font-size: {self.font_size}px;")
        main_layout.addWidget(payer_label)
        self.payer_combobox = QComboBox()
        self.payer_combobox.setStyleSheet(f"font-size: {self.font_size}px;")
        main_layout.addWidget(self.payer_combobox)

        # Input for Expense Amount
        self.amount_input = QLineEdit()
        self.amount_input.setStyleSheet(f"font-size: {self.font_size}px;")
        self.amount_input.setPlaceholderText("Enter the total expense amount")
        main_layout.addWidget(self.amount_input)

        # Calculate Button
        calculate_button = QPushButton("Calculate Dang")
        calculate_button.setStyleSheet(f"font-size: {self.font_size}px;")
        calculate_button.clicked.connect(self.calculate_dang)
        main_layout.addWidget(calculate_button)

        # Result Label
        self.result_label = QLabel("")
        main_layout.addWidget(self.result_label)

        # Central Widget Setup
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def load_members(self):
        members = self.db_handler.get_balances()  # Get members with balances
        self.member_tree_widget.clear()
        self.payer_combobox.clear()

        for member, balance in members.items():
            tree_item = QTreeWidgetItem([member, f"{balance:.2f}"])
            tree_item.setCheckState(0, Qt.Unchecked)
            tree_item.setFlags(tree_item.flags() | Qt.ItemIsEditable)  # Make balance editable
            self.member_tree_widget.addTopLevelItem(tree_item)
            self.payer_combobox.addItem(member)

    def add_member_dialog(self):
        # Dialog to Add New Member
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Member")
        dialog_layout = QVBoxLayout()

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter member's name")
        dialog_layout.addWidget(name_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_member(name_input.text(), dialog))
        dialog_layout.addWidget(add_button)

        dialog.setLayout(dialog_layout)
        dialog.exec_()

    def add_member(self, name, dialog):
        if name:
            if self.db_handler.add_member(name):
                self.load_members()
                dialog.accept()

    def calculate_dang(self):
        # Calculate each person's share
        selected_members = []
        for index in range(self.member_tree_widget.topLevelItemCount()):
            item = self.member_tree_widget.topLevelItem(index)
            if item.checkState(0) == Qt.Checked:
                selected_members.append(item.text(0))

        payer = self.payer_combobox.currentText()
        try:
            total_amount = float(self.amount_input.text())
        except ValueError:
            self.result_label.setText("Please enter a valid amount.")
            return

        if not selected_members or not payer or total_amount <= 0:
            self.result_label.setText("Please select members, payer, and enter a valid amount.")
            return

        # Calculate individual share
        num_members = len(selected_members)
        share_per_person = total_amount / num_members

        result_text = f"Total Amount: {total_amount}\n"
        for member in selected_members:
            if member == payer:
                result_text += f"{member} (Payer): 0 (Already Paid)\n"
            else:
                result_text += f"{member}: {share_per_person}\n"
                # Update balance in the database
                self.db_handler.update_balance(member, share_per_person)
            # Deduct the amount paid by the payer
            if member == payer:
                self.db_handler.update_balance(member, -total_amount)

        self.result_label.setText(result_text)
        # Reload members to reflect updated balances
        self.load_members()

    def update_balance(self, item, column):
        # Update the balance in the database if the balance column is edited
        if column == 1:  # Balance column
            member_name = item.text(0)
            try:
                new_balance = float(item.text(1))
            except ValueError:
                self.result_label.setText("Please enter a valid number for the balance.")
                return

            # Update the balance in the database
            self.db_handler.update_balance(member_name, new_balance - self.db_handler.get_balances()[member_name])
            self.result_label.setText(f"Balance updated for {member_name}")

    def open_settings_dialog(self):
        # Dialog for Settings
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        settings_layout = QVBoxLayout()

        font_label = QLabel("Adjust Font Size:")
        font_label.setStyleSheet("font-size: 16px;")
        settings_layout.addWidget(font_label)

        font_input = QLineEdit()
        font_input.setPlaceholderText("Enter font size (e.g., 16)")
        font_input.setText(str(self.font_size))  # Set current font size
        settings_layout.addWidget(font_input)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.apply_settings(font_input.text(), settings_dialog))
        settings_layout.addWidget(ok_button)

        settings_dialog.setLayout(settings_layout)
        settings_dialog.exec_()

    def apply_settings(self, font_size_str, dialog):
        try:
            font_size = int(font_size_str)
            if 10 <= font_size <= 30:
                self.font_size = font_size
                style_sheet = f"font-size: {self.font_size}px;"
                self.member_tree_widget.setStyleSheet(style_sheet)
                self.payer_combobox.setStyleSheet(style_sheet)
                self.amount_input.setStyleSheet(style_sheet)
                self.result_label.setStyleSheet(style_sheet)
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Invalid Font Size", "Font size must be between 10 and 30.")
        except ValueError:
            QMessageBox.warning(dialog, "Invalid Input", "Please enter a valid number for the font size.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())