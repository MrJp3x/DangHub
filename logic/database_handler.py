# File path: ./logic/database_handler.py

from PySide6.QtSql import QSqlDatabase, QSqlQuery
import sys


class DatabaseHandler:
    def __init__(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("danghub.db")

        if not self.db.open():
            print("Unable to establish a database connection.")
            sys.exit(1)

        self.init_tables()

    def init_tables(self):
        query = QSqlQuery()
        query.exec("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        """)

        query.exec("""
            CREATE TABLE IF NOT EXISTS member_balances (
                member_id INTEGER PRIMARY KEY,
                balance REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(member_id) REFERENCES members(id)
            )
        """)

    def add_member(self, name):
        query = QSqlQuery()
        query.prepare("INSERT INTO members (name) VALUES (?)")
        query.addBindValue(name)
        if query.exec():
            # Initialize balance for the new member
            query = QSqlQuery()
            query.prepare(
                "INSERT INTO member_balances (member_id, balance) VALUES ((SELECT id FROM members WHERE name = ?), 0)")
            query.addBindValue(name)
            return query.exec()
        return False

    def delete_member(self, name):
        query = QSqlQuery()
        query.prepare("DELETE FROM members WHERE name = ?")
        query.addBindValue(name)
        if query.exec():
            # Also remove balance record
            query = QSqlQuery()
            query.prepare("DELETE FROM member_balances WHERE member_id = (SELECT id FROM members WHERE name = ?)")
            query.addBindValue(name)
            return query.exec()
        return False

    def update_balance(self, member_name, balance_change):
        query = QSqlQuery()
        query.prepare("""
            UPDATE member_balances 
            SET balance = balance + ? 
            WHERE member_id = (SELECT id FROM members WHERE name = ?)
        """)
        query.addBindValue(balance_change)
        query.addBindValue(member_name)
        return query.exec()

    def get_members(self):
        query = QSqlQuery("SELECT name FROM members")
        members = []
        while query.next():
            members.append(query.value(0))
        return members

    def get_balances(self):
        query = QSqlQuery("""
            SELECT m.name, b.balance 
            FROM members m
            JOIN member_balances b ON m.id = b.member_id
        """)
        balances = {}
        while query.next():
            member = query.value(0)
            balance = query.value(1)
            balances[member] = balance
        return balances
