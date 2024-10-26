# File path: ./logic/split_calculator.py

class SplitCalculator:
    def __init__(self, expenses, payer):
        """
        Initialize the SplitCalculator with expenses and payer.

        Parameters:
            expenses (dict): A dictionary where keys are members and values are their expenses.
            payer (str): The person who initially paid the total amount.
        """
        self.expenses = expenses
        self.payer = payer
        self.balances = self.calculate_dang()

    def calculate_dang(self):
        """
        Calculate the share of each member and optimize the transactions.

        Returns:
            dict: A dictionary with each member's balance (positive means they owe money, negative means they should be paid).
        """
        total_expense = sum(self.expenses.values())
        num_members = len(self.expenses)
        share_per_person = total_expense / num_members

        balances = {}
        for member, amount in self.expenses.items():
            if member == self.payer:
                balances[member] = amount - total_expense
            else:
                balances[member] = amount - share_per_person

        return balances

    def optimize_transactions(self):
        """
        Optimize the transactions to reduce the number of payments.

        Returns:
            list of tuple: A list of transactions where each tuple represents (from, to, amount).
        """
        transactions = []
        creditors = [(member, balance) for member, balance in self.balances.items() if balance < 0]
        debtors = [(member, balance) for member, balance in self.balances.items() if balance > 0]

        creditors.sort(key=lambda x: x[1])  # Sort creditors by how much they are owed (ascending)
        debtors.sort(key=lambda x: x[1], reverse=True)  # Sort debtors by how much they owe (descending)

        i, j = 0, 0
        while i < len(creditors) and j < len(debtors):
            creditor, credit_balance = creditors[i]
            debtor, debt_balance = debtors[j]

            payment = min(-credit_balance, debt_balance)
            transactions.append((debtor, creditor, payment))

            # Update balances
            self.balances[creditor] += payment
            self.balances[debtor] -= payment

            # Move to next creditor or debtor if settled
            if self.balances[creditor] == 0:
                i += 1
            if self.balances[debtor] == 0:
                j += 1

        return transactions
