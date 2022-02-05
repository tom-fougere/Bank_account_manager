from source.definitions import CATEGORIES, OCCASIONS


class MetadataDB:
    def __init__(self, mongodb_connection):
        self.connection = mongodb_connection
        self.account_id = None
        self.balance = None
        self.categories = None
        self.occasions = None
        self.date_last_transaction = {'dt': None,
                                      'str': None}
        self.date_last_import = {'dt': None,
                                 'str': None}

    def init_db(self, account_id, balance, date_last_transaction, date_last_import,
                categories=CATEGORIES, occasions=OCCASIONS):
        self.account_id = account_id
        self.balance = balance
        self.categories = categories
        self.occasions = occasions
        self.date_last_transaction['dt'] = date_last_transaction
        self.date_last_transaction['str'] = date_last_transaction.strftime("%d/%m/%Y")
        self.date_last_import['dt'] = date_last_import
        self.date_last_import['str'] = date_last_import.strftime("%d/%m/%Y")

        data_to_ingest = {'account_id': self.account_id,
                          'balance': self.balance,
                          'categories': self.categories,
                          'occasions': self.occasions,
                          'date_last_transaction': self.date_last_transaction,
                          'date_last_import': self.date_last_import}

        self.connection.collection.insert_one(data_to_ingest)

    def get_balance(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['balance'])
        return result['balance']

    def get_categories(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['categories'])
        return list(result['categories'].keys())

    def get_sub_categories(self, account_id, category):
        result = self.connection.collection.find_one({'account_id': account_id}, ['categories'])
        return result['categories'][category]

    def get_occasions(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['occasions'])
        return result['occasions']

    def get_date_last_import(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['date_last_import.str'])
        return result['date_last_import']['str']

    def get_date_last_transaction(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['date_last_transaction.str'])
        return result['date_last_transaction']['str']

    def update_balance(self, account_id, balance):
        self.connection.collection.update({'account_id': account_id}, {"$set": {'balance': balance}}, upsert=False)
