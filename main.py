import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QPushButton, QLabel, QLineEdit,
                               QComboBox, QListWidget, QDialog)
from widgets.menu_bar import MenuBar
from logic.database_handler import DatabaseHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_handler = DatabaseHandler()  # Instance of DatabaseHandler
        self.setWindowTitle("DangHub")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()
        self.load_members()  # Load members from database

    def init_ui(self):
        # Menu Bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Main Layout
        main_layout = QVBoxLayout()

        # Checklist for Members
        self.member_list_widget = QListWidget()
        main_layout.addWidget(QLabel("Select Members for Dang:"))
        main_layout.addWidget(self.member_list_widget)

        # ComboBox for selecting the payer (Mother Kharj)
        main_layout.addWidget(QLabel("Select Payer (Mother Kharj):"))
        self.payer_combobox = QComboBox()
        main_layout.addWidget(self.payer_combobox)

        # Input for Expense Amount
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter the total expense amount")
        main_layout.addWidget(self.amount_input)

        # Calculate Button
        calculate_button = QPushButton("Calculate Dang")
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
        members = self.db_handler.get_members()
        self.member_list_widget.clear()
        self.payer_combobox.clear()

        for member in members:
            self.member_list_widget.addItem(member)
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
        selected_members = [item.text() for item in self.member_list_widget.selectedItems()]
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
