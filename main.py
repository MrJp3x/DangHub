import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QPushButton, QLabel, QLineEdit,
                               QComboBox, QListWidget, QDialog)
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from widgets.menu_bar import MenuBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DangHub")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()
        self.init_db()

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

    def init_db(self):
        # Setting up SQLite Database
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("danghub.db")

        if not self.db.open():
            print("Unable to establish a database connection.")
            sys.exit(1)

        # Creating Members Table if not exists
        query = QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)
        self.load_members()

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
            query = QSqlQuery()
            query.prepare("INSERT INTO members (name) VALUES (?)")
            query.addBindValue(name)
            if query.exec_():
                self.load_members()
                dialog.accept()

    def load_members(self):
        # Load Members from Database into Checklist and ComboBox
        self.member_list_widget.clear()
        self.payer_combobox.clear()

        query = QSqlQuery("SELECT name FROM members")
        while query.next():
            name = query.value(0)
            self.member_list_widget.addItem(name)
            self.payer_combobox.addItem(name)

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

        self.result_label.setText(result_text)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

