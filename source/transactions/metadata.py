from source.definitions import ALL_CATEGORIES, OCCASIONS, TYPE_TRANSACTIONS
from utils.time_operations import str_to_datetime
from source.db_connection.db_access import MongoDBConnection


class MetadataDB:
    def __init__(self, name_connection, account_id):
        self.connection = MongoDBConnection(name_connection)
        self.account_id = account_id
        self.balance_in_bank = None
        self.balance_in_db = None
        self.balance_bias = None
        self.categories = None
        self.occasions = None
        self.types_transaction = None
        self.nb_transactions_db = 0
        self.date_balance_in_bank = {'dt': None,
                                     'str': None}
        self.date_last_import = {'dt': None,
                                 'str': None}

    def init_db(self, balance_in_bank, balance_in_db, balance_bias,
                date_balance_in_bank, date_last_import, nb_trans_db=0,
                categories=ALL_CATEGORIES, occasions=OCCASIONS, types=TYPE_TRANSACTIONS):
        self.balance_in_bank = balance_in_bank
        self.balance_in_db = balance_in_db
        self.balance_bias = balance_bias
        self.categories = categories
        self.occasions = occasions
        self.types_transaction = types
        self.nb_transactions_db = nb_trans_db
        self.date_balance_in_bank['dt'] = date_balance_in_bank
        self.date_balance_in_bank['str'] = date_balance_in_bank.strftime("%d/%m/%Y")
        self.date_last_import['dt'] = date_last_import
        self.date_last_import['str'] = date_last_import.strftime("%d/%m/%Y")

        data_to_ingest = {'account_id': self.account_id,
                          'balance_in_bank': self.balance_in_bank,
                          'balance_in_db': self.balance_in_db,
                          'balance_bias': self.balance_bias,
                          'categories': self.categories,
                          'occasions': self.occasions,
                          'nb_transactions_db': self.nb_transactions_db,
                          'types_transaction': self.types_transaction,
                          'date_balance_in_bank': self.date_balance_in_bank,
                          'date_last_import': self.date_last_import}

        self.connection.collection.insert_one(data_to_ingest)

    def write_values_in_db(self):

        data_to_ingest = {'balance_in_bank': self.balance_in_bank,
                          'balance_in_db': self.balance_in_db,
                          'balance_bias': self.balance_bias,
                          'categories': self.categories,
                          'occasions': self.occasions,
                          'nb_transactions_db': self.nb_transactions_db,
                          'types_transaction': self.types_transaction,
                          'date_balance_in_bank': self.date_balance_in_bank,
                          'date_last_import': self.date_last_import}

        self.connection.collection.update(
            {
                'account_id': self.account_id
            },
            {
                "$set": data_to_ingest
            },
            upsert=False
        )

    def get_all_values(self):

        self.balance_in_bank = self.get_balance_in_bank()
        self.balance_in_db = self.get_balance_in_db()
        self.balance_bias = self.get_balance_bias()
        self.categories = self.get_categories_and_sub()
        self.occasions = self.get_list_occasions()
        self.types_transaction = self.get_types_transaction()
        self.nb_transactions_db = self.get_nb_transactions_db()

        date_balance_in_bank = self.get_date_balance_in_bank()
        self.date_balance_in_bank = {'dt': str_to_datetime(date_balance_in_bank, date_format="%d/%m/%Y"),
                                     'str': date_balance_in_bank}

        date_last_import = self.get_date_last_import()
        self.date_last_import = {'dt': str_to_datetime(date_last_import, date_format="%d/%m/%Y"),
                                 'str': date_last_import}

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

    def get_balance_in_bank(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['balance_in_bank'])
        return result['balance_in_bank']

    def get_balance_in_db(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['balance_in_db'])
        return result['balance_in_db']

    def get_balance_bias(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['balance_bias'])
        return result['balance_bias']

    def get_categories(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['categories'])
        return list(result['categories'].keys())

    def get_category_info(self, category):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['categories'])
        return result['categories'][category]

    def get_categories_and_sub(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['categories'])

        cat_and_sub_cat = dict()
        for cat, value in result['categories'].items():
            cat_and_sub_cat[cat] = list(value['Sub-categories'].keys())

        return cat_and_sub_cat

    def get_sub_categories(self, category):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['categories'])
        return result['categories'][category]['Sub-categories']

    def get_list_occasions(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['occasions'])
        return result['occasions']

    def get_default_occasion(self, category, sub_category=None):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['categories'])

        category_info = result['categories'][category]
        default_occasion = category_info['Default_occasion']
        if sub_category is not None and sub_category in list(category_info['Sub-categories'].keys()):
            default_occasion = category_info['Sub-categories'][sub_category]['Default_occasion']

        return default_occasion

    def get_types_transaction(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['types_transaction'])
        return result['types_transaction']

    def get_date_last_import(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['date_last_import.str'])
        return result['date_last_import']['str']

    def get_date_balance_in_bank(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['date_balance_in_bank.str'])
        return result['date_balance_in_bank']['str']

    def get_nb_transactions_db(self):
        result = self.connection.collection.find_one({'account_id': self.account_id}, ['nb_transactions_db'])
        return result['nb_transactions_db']

    def update_balance_in_bank(self, balance):
        self.connection.collection.update({'account_id': self.account_id},
                                          {"$set": {'balance_in_bank': balance}}, upsert=False)

    def update_balance_in_db(self, balance):
        self.connection.collection.update({'account_id': self.account_id},
                                          {"$set": {'balance_in_db': balance}}, upsert=False)

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

    def update_nb_transactions(self, new_nb_trans_bank=0, new_nb_trans_db=0):

        current_bn_trans_db = self.get_nb_transactions_db()

        self.connection.collection.update({'account_id': self.account_id},
                                          {"$set": {
                                              'nb_transactions_db': current_bn_trans_db + new_nb_trans_db
                                          }},
                                          upsert=False)
