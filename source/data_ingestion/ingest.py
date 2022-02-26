from bson.objectid import ObjectId
from utils.time_operations import str_to_datetime, modify_date_str_format


class TransactionIngest:
    def __init__(self, mongodb_connection, transactions_df):
        self.connection = mongodb_connection
        self.transactions_df = transactions_df

    def ingest(self):

        df_transaction = self.transactions_df.copy()

        # Convert 2 fields of date as one with a dict
        df_transaction['date'] = \
            df_transaction.apply(lambda x: {'str': x.date_str,
                                            'dt': x.date_dt}, axis=1)
        df_transaction['date_transaction'] = \
            df_transaction.apply(lambda x: {'str': x.date_transaction_str,
                                            'dt': x.date_transaction_dt}, axis=1)

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

    def update_one_transaction(self, transaction_series):

        transaction_dict = transaction_series.to_dict()

        # Filter to get the selected document
        doc_filter = {'_id': ObjectId(transaction_dict['_id'])}

        # Remove the useless columns
        del transaction_dict['_id']

        # Values to be updated
        new_values = {"$set": transaction_dict}

        # Update the document
        current_doc = self.connection.collection.find_one(doc_filter)
        if current_doc is not None:
            self.connection.collection.update_one(doc_filter, new_values, upsert=False)
        else:
            raise ValueError("Impossible to update the doc because the object ID doesn't exist.")

    def update(self):

        df_transaction = self.transactions_df.copy()

        # Convert date in datetime
        df_transaction['date_dt'] = df_transaction.apply(
            lambda x: str_to_datetime(x.date_str, date_format='%Y-%m-%d'), axis=1)
        df_transaction['date_transaction_dt'] = df_transaction.apply(
            lambda x: str_to_datetime(x.date_transaction_str, date_format='%Y-%m-%d'), axis=1)

        # Modify string format of dates
        df_transaction['date_str'] = df_transaction.apply(
            lambda x: modify_date_str_format(x.date_str,
                                             current_format='%Y-%m-%d',
                                             new_format='%d/%m/%Y'), axis=1)
        df_transaction['date_transaction_str'] = df_transaction.apply(
            lambda x: modify_date_str_format(x.date_transaction_str,
                                             current_format='%Y-%m-%d',
                                             new_format='%d/%m/%Y'), axis=1)

        # Convert 2 fields of date as one with a dict
        df_transaction['date'] = \
            df_transaction.apply(lambda x: {'str': x.date_str,
                                            'dt': x.date_dt}, axis=1)
        df_transaction['date_transaction'] = \
            df_transaction.apply(lambda x: {'str': x.date_transaction_str,
                                            'dt': x.date_transaction_dt}, axis=1)

        df_transaction.drop(columns=['date_str', 'date_dt', 'date_transaction_str', 'date_transaction_dt'],
                            axis=1,
                            inplace=True)

        for _, trans in df_transaction.iterrows():
            self.update_one_transaction(trans)
