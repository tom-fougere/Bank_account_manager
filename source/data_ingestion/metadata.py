from source.definitions import CATEGORIES, OCCASIONS, TYPE_TRANSACTIONS


class MetadataDB:
    def __init__(self, mongodb_connection):
        self.connection = mongodb_connection
        self.account_id = None
        self.balance_in_bank = None
        self.balance_in_db = None
        self.balance_bias = None
        self.categories = None
        self.occasions = None
        self.types_transaction = None
        self.date_balance_in_bank = {'dt': None,
                                     'str': None}
        self.date_last_import = {'dt': None,
                                 'str': None}

    def init_db(self, account_id, balance_in_bank, balance_in_db, balance_bias,
                date_balance_in_bank, date_last_import,
                categories=CATEGORIES, occasions=OCCASIONS, types=TYPE_TRANSACTIONS):
        self.account_id = account_id
        self.balance_in_bank = balance_in_bank
        self.balance_in_db = balance_in_db
        self.balance_bias = balance_bias
        self.categories = categories
        self.occasions = occasions
        self.types_transaction = types
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
                          'types_transaction': self.types_transaction,
                          'date_balance_in_bank': self.date_balance_in_bank,
                          'date_last_import': self.date_last_import}

        self.connection.collection.insert_one(data_to_ingest)

    def get_balance_in_bank(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['balance_in_bank'])
        return result['balance_in_bank']

    def get_balance_in_db(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['balance_in_db'])
        return result['balance_in_db']

    def get_balance_bias(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['balance_bias'])
        return result['balance_bias']

    def get_categories(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['categories'])
        return list(result['categories'].keys())

    def get_sub_categories(self, account_id, category):
        result = self.connection.collection.find_one({'account_id': account_id}, ['categories'])
        return result['categories'][category]

    def get_occasions(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['occasions'])
        return result['occasions']

    def get_types_transaction(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['types_transaction'])
        return result['types_transaction']

    def get_date_last_import(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['date_last_import.str'])
        return result['date_last_import']['str']

    def get_date_balance_in_bank(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['date_balance_in_bank.str'])
        return result['date_balance_in_bank']['str']

    def update_balance_in_bank(self, account_id, balance):
        self.connection.collection.update({'account_id': account_id},
                                          {"$set": {'balance_in_bank': balance}}, upsert=False)

    def update_balance_in_db(self, account_id, balance):
        self.connection.collection.update({'account_id': account_id},
                                          {"$set": {'balance_in_db': balance}}, upsert=False)

    def update_date_balance_in_bank(self, account_id, date):

        date_dt = date
        date_str = date.strftime("%d/%m/%Y")

        self.connection.collection.update({'account_id': account_id},
                                          {"$set": {'date_balance_in_bank.str': date_str,
                                                    'date_balance_in_bank.dt': date_dt}}, upsert=False)

    def update_date_last_import(self, account_id, date):

        date_dt = date
        date_str = date.strftime("%d/%m/%Y")

        self.connection.collection.update({'account_id': account_id},
                                          {"$set": {'date_last_import.str': date_str,
                                                    'date_last_import.dt': date_dt}}, upsert=False)
