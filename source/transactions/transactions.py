import pandas as pd

from utils.class_operations import get_class_attributes


class Transaction:
    def __init__(self, account_id, date_bank, date, description, amount, type,
                 category=None, sub_category=None, occasion=None, comment=None):
        self.account_id = account_id
        self.date_bank = date_bank
        self.date = date
        self.description = description
        self.amount = amount
        self.type = type
        self.category = category
        self.sub_category = sub_category
        self.occasion = occasion
        self.comment = comment

    def __eq__(self, other):
        # Get attributes of the class (not the methods)
        attributes = get_class_attributes(self)

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
            'category': self.category,
            'sub_category': self.sub_category,
            'occasion': self.occasion,
            'comment': self.comment
        }


def dict_to_transaction(my_dict):
    return Transaction(account_id=my_dict['account_id'],
                       date_bank=my_dict['date_bank'],
                       date=my_dict['date'],
                       description=my_dict['description'],
                       amount=my_dict['amount'],
                       type=my_dict['type'],
                       category=my_dict['category'],
                       sub_category=my_dict['sub_category'],
                       occasion=my_dict['occasion'],
                       comment=my_dict['comment'])


def list_transactions_to_dataframe(list_transactions):
    column_names = ['account_id', 'date_bank', 'date', 'description', 'amount',
                    'type', 'category', 'sub_category', 'occasion']
    column_names = get_class_attributes(list_transactions[0])

    # Init dict with empty list
    dict_trans = dict()
    for name in column_names:
        dict_trans[name] = []

    for trans in list_transactions:
        for att in column_names:
            dict_trans[att].append(getattr(trans, att))

    df_transactions = pd.DataFrame(dict_trans, columns=column_names)

    return df_transactions
