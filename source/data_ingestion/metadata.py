from source.definitions import CATEGORIES


class MetadataDB:
    def __init__(self, mongodb_connection):
        self.connection = mongodb_connection
        self.account_id = None
        self.balance = None
        self.categories = None

    def init_db(self, account_id, balance, categories=CATEGORIES):
        self.account_id = account_id
        self.balance = balance
        self.categories = categories

        data_to_ingest = {'account_id': self.account_id,
                          'balance': self.balance,
                          'categories': categories}

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
