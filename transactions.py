

class Transaction:
    def __init__(self, account_id, date_bank, date, description, amount, type, category=None):
        self.account_id = account_id
        self.date_bank = date_bank
        self.date = date
        self.description = description
        self.amount = amount
        self.type = type
        self.category = category

    def __eq__(self, other):
        # Get attributes of the class (not the methods)
        attributes = [att for att in dir(self) if not att.startswith('__') and not callable(getattr(self, att))]

        # counter of same attributes between classes
        counter_same_attr = len(attributes)

        # Loop through attributes
        for attribute in attributes:
            self_value = getattr(self, attribute)
            other_value = getattr(other, attribute)
            if self_value == other_value:
                counter_same_attr -= 1

        if counter_same_attr == 0:
            same_class = True
        else:
            same_class = False

        return same_class

    def get_dict(self):
        return {
            'account_id': self.account_id,
            'date_bank': self.date_bank,
            'date': self.date,
            'description': self.description,
            'amount': self.amount,
            'type': self.type,
            'category': self.category
        }


def dict_to_transaction(my_dict):
    return Transaction(account_id=my_dict['account_id'],
                       date_bank=my_dict['date_bank'],
                       date=my_dict['date'],
                       description=my_dict['description'],
                       amount=my_dict['amount'],
                       type=my_dict['type'],
                       category=my_dict['category'])
