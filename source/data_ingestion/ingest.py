from utils.time_operations import str_to_datetime


class TransactionIngest:
    def __init__(self, mongodb_connection, transactions_df):
        self.connection = mongodb_connection
        self.transactions_df = transactions_df

    def ingest(self):

        df_transaction = self.transactions_df.copy()

        # Convert 2 fields of date as one with a dict
        df_transaction['date'] = \
            df_transaction.apply(lambda x: {'str': x.date_str,
                                            'dt': x.date_dt.isoformat()}, axis=1)
        df_transaction['date_transaction'] = \
            df_transaction.apply(lambda x: {'str': x.date_transaction_str,
                                            'dt': x.date_transaction_dt.isoformat()}, axis=1)

        df_transaction.drop(columns=['date_str', 'date_dt', 'date_transaction_str', 'date_transaction_dt'],
                            axis=1,
                            inplace=True)

        for _, trans in df_transaction.iterrows():
            self.ingest_one_transaction(trans)

    def ingest_one_transaction(self, transaction_series):

        transaction_dict = transaction_series.to_dict()
        db_trans = self.connection.collection.find({'account_id': transaction_dict['account_id'],
                                                    'date.str': transaction_dict['date']['str'],
                                                    'date_transaction.str': transaction_dict['date_transaction']['str'],
                                                    'amount': transaction_dict['amount']})

        if len(list(db_trans)) >= 1:
            raise ValueError('There is 1 or more documents in the DB with the same attributes: '
                             ' - account_id: {},'
                             ' - date: {},'
                             ' - date_transaction: {},'
                             ' - amount: {}'.format(transaction_dict['account_id'],
                                                    transaction_dict['date']['str'],
                                                    transaction_dict['date_transaction']['str'],
                                                    transaction_dict['amount']))
        else:
            self.connection.collection.insert(transaction_dict)
