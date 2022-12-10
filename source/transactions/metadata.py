from source.categories import ALL_CATEGORIES, OCCASIONS, TYPE_TRANSACTIONS
from utils.time_operations import str_to_datetime
from source.db_connection.db_access import MongoDBConnection

LIST_ATTRIBUTES_METADATA = [
    'balance_in_bank',
    'balance_in_db',
    'balance_bias',
    'categories',
    'occasions',
    'nb_transactions_db',
    'types_transaction',
    'date_balance_in_bank',
    'date_last_import',
]


class MetadataDB:
    def __init__(self, name_connection, account_id):
        self.connection = MongoDBConnection(name_connection)
        self.account_id = account_id

        # Set default value
        for attribute in LIST_ATTRIBUTES_METADATA:
            setattr(self, attribute, None)

    def set(self, balance_in_bank, balance_in_db, balance_bias,
            date_balance_in_bank, date_last_import, nb_trans_db=0,
            categories=ALL_CATEGORIES, occasions=OCCASIONS, types=TYPE_TRANSACTIONS):

        self.balance_in_bank = balance_in_bank
        self.balance_in_db = balance_in_db
        self.balance_bias = balance_bias
        self.categories = categories
        self.occasions = occasions
        self.types_transaction = types
        self.nb_transactions_db = nb_trans_db
        self.date_balance_in_bank = dict()
        self.date_balance_in_bank['dt'] = date_balance_in_bank
        self.date_balance_in_bank['str'] = date_balance_in_bank.strftime("%d/%m/%Y")
        self.date_last_import = dict()
        self.date_last_import['dt'] = date_last_import
        self.date_last_import['str'] = date_last_import.strftime("%d/%m/%Y")

        # self.connection.collection.insert_one(data_to_ingest)

    def set_from_db(self):
        # Extract all data
        data = self.connection.collection.find_one({'account_id': self.account_id})

        if data is not None:
            # remove useless field
            del data['_id']
            del data['account_id']

            # Set dict as class attributes
            for key, value in data.items():
                setattr(self, key, value)

    def update_db(self):

        data_to_ingest = {
            'balance_in_bank': self.balance_in_bank,
            'balance_in_db': self.balance_in_db,
            'balance_bias': self.balance_bias,
            'categories': self.categories,
            'occasions': self.occasions,
            'nb_transactions_db': self.nb_transactions_db,
            'types_transaction': self.types_transaction,
            'date_balance_in_bank': self.date_balance_in_bank,
            'date_last_import': self.date_last_import,
        }

        self.connection.collection.update(
            {
                'account_id': self.account_id
            },
            {
                "$set": data_to_ingest
            },
            upsert=True
        )

    def update_values(self, new_values):
        for key, value in new_values.items():
            if (key == 'date_balance_in_bank') or (key == 'date_last_import'):
                value_dict = {
                    'dt': value,
                    'str': value.strftime("%d/%m/%Y"),
                }
                self.__setattr__(key, value_dict)
            elif key in self.__dict__.keys():
                self.__setattr__(key, value)

    def get_list_categories(self):
        return list(self.categories.keys())

    def get_list_categories_and_sub(self):

        cat_and_sub_cat = dict()
        for cat, value in self.categories.items():
            cat_and_sub_cat[cat] = list(value['Sub-categories'].keys())

        return cat_and_sub_cat

    def get_default_occasion(self, category, sub_category=None):

        category_info = self.categories[category]
        default_occasion = category_info['Default_occasion']
        if sub_category is not None and sub_category in list(category_info['Sub-categories'].keys()):
            default_occasion = category_info['Sub-categories'][sub_category]['Default_occasion']

        return default_occasion

    def update_date_balance_in_bank(self, date):

        date_dt = date
        date_str = date.strftime("%d/%m/%Y")

        self.connection.collection.update({'account_id': self.account_id},
                                          {"$set": {'date_balance_in_bank.str': date_str,
                                                    'date_balance_in_bank.dt': date_dt}}, upsert=False)

    def update_date_last_import(self, date):

        date_dt = date
        date_str = date.strftime("%d/%m/%Y")

        self.connection.collection.update({'account_id': self.account_id},
                                          {"$set": {'date_last_import.str': date_str,
                                                    'date_last_import.dt': date_dt}}, upsert=False)
