from source.definitions import CATEGORIES, OCCASIONS


class MetadataDB:
    def __init__(self, mongodb_connection):
        self.connection = mongodb_connection
        self.account_id = None
        self.balance = None
        self.categories = None
        self.occasions = None
        self.date_last_update = {'dt': None,
                                 'str': None}
        self.last_date = {'dt': None,
                          'str': None}

    def init_db(self, account_id, balance, date_late_update, last_date,
                categories=CATEGORIES, occasions=OCCASIONS):
        self.account_id = account_id
        self.balance = balance
        self.categories = categories
        self.occasions = occasions
        self.date_last_update['dt'] = date_late_update
        self.date_last_update['str'] = date_late_update.strftime("%d/%m/%Y")
        self.last_date['dt'] = last_date
        self.last_date['str'] = last_date.strftime("%d/%m/%Y")

        data_to_ingest = {'account_id': self.account_id,
                          'balance': self.balance,
                          'categories': self.categories,
                          'occasions': self.occasions,
                          'date_last_update': self.date_last_update,
                          'last_date': self.last_date}

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

    def get_last_date(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['last_date.str'])
        return result['last_date']['str']

    def get_date_last_update(self, account_id):
        result = self.connection.collection.find_one({'account_id': account_id}, ['date_last_update.str'])
        return result['date_last_update']['str']
