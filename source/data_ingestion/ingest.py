

class TransactionIngest:
    def __init__(self, mongodb_connection, transactions_list):
        self.connection = mongodb_connection
        self.transactions_list = transactions_list
        print('ok')

    def ingest(self):
        for trans in self.transactions_list:
            self.ingest_one_transaction(trans)

    def ingest_one_transaction(self, transaction):
        db_trans = self.connection.collection.find({'account_id': transaction.account_id,
                                                    'date': transaction.date,
                                                    'date_bank': transaction.date_bank,
                                                    'amount': transaction.amount})

        if len(list(db_trans)) >= 1:
            raise ValueError('There is 1 or more documents in the DB with the same attributes: '
                             ' - account_id: {},'
                             ' - date: {},'
                             ' - date_bank: {},'
                             ' - amount: {}'.format(transaction.account_id,
                                                    transaction.date,
                                                    transaction.date_bank,
                                                    transaction.amount))
        else:
            self.connection.collection.insert(transaction.get_dict())
