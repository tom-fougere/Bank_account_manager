

class TransactionIngest:
    def __init__(self, mongodb_connection, transactions_df):
        self.connection = mongodb_connection
        self.transactions_df = transactions_df

    def ingest(self):
        for _, trans in self.transactions_df.iterrows():
            self.ingest_one_transaction(trans)

    def ingest_one_transaction(self, transaction_series):

        transaction_dict = transaction_series.to_dict()
        db_trans = self.connection.collection.find({'account_id': transaction_dict['account_id'],
                                                    'date': transaction_dict['date'],
                                                    'date_transaction': transaction_dict['date_transaction'],
                                                    'amount': transaction_dict['amount']})

        if len(list(db_trans)) >= 1:
            raise ValueError('There is 1 or more documents in the DB with the same attributes: '
                             ' - account_id: {},'
                             ' - date: {},'
                             ' - date_transaction: {},'
                             ' - amount: {}'.format(transaction_dict['account_id'],
                                                    transaction_dict['date'],
                                                    transaction_dict['date_transaction'],
                                                    transaction_dict['amount']))
        else:
            self.connection.collection.insert(transaction_dict)
