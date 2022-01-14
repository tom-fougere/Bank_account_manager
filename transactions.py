

class Transaction:
    def __init__(self, account_id, date_bank, date, description, amount, type):
        self.account_id = account_id
        self.date_bank = date_bank
        self.date = date
        self.description = description
        self.amount = amount
        self.type = type
        self.category = None