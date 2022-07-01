from bson.objectid import ObjectId
from utils.time_operations import str_to_datetime, modify_date_str_format
from source.data_ingestion.metadata import MetadataDB
from source.db_connection.db_access import MongoDBConnection

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

class TransactionDB:
    def __init__(self, name_connection_metadata, name_connection_transaction, account_id):

        self.connection_transaction = MongoDBConnection(name_connection_transaction)
        self.account_id = account_id

        self.metadata = MetadataDB(name_connection=name_connection_metadata,
                                   account_id=self.account_id)
        self.metadata.get_all_values()

    @staticmethod
    def _format_transactions_dataframe(df_transactions):

        df_transactions_formatted = df_transactions.copy()

        # Convert 2 fields of date as one with a dict
        df_transactions_formatted['date'] = \
            df_transactions_formatted.apply(lambda x: {'str': x.date_str,
                                            'dt': x.date_dt}, axis=1)
        df_transactions_formatted['date_transaction'] = \
            df_transactions_formatted.apply(lambda x: {'str': x.date_transaction_str,
                                            'dt': x.date_transaction_dt}, axis=1)

        df_transactions_formatted.drop(
            columns=['date_str', 'date_dt', 'date_transaction_str', 'date_transaction_dt'],
            axis=1,
            inplace=True
        )

        return df_transactions_formatted

    def ingest(self, df_transactions, bank_info):

        # Format dataframe (removing useless columns and format dates)
        df_transactions_2 = self._format_transactions_dataframe(df_transactions)

        # Insert transactions
        self.connection_transaction.collection.insert_many(df_transactions_2.to_dict('records'))

        # Update metadata info
        self._update_metadata(df_transactions_2, bank_info)

    def delete(self, df_transactions):

        assert '_id' in df_transactions.columns

        # Remove transactions in the transaction DB
        for idx, row in df_transactions.iterrows():
            self.connection_transaction.collection.delete_one({"_id": ObjectId(row['_id'])})

        # Update metadata DB
        self._update_metadata(
            df=[],
            bank_info={
                'balance': self.metadata.balance_in_bank,
                'date': self.metadata.date_balance_in_bank['dt'],
                'account_id': self.account_id,
            }
        )

    def check(self, df_transactions, bank_info):

        new_nb_transactions = self.metadata.nb_transactions_bank + len(df_transactions)
        new_balance = self._get_balance_in_db() + df_transactions['amount'].sum()

        diff_nb_transaction = self.connection_transaction.collection.count(
                {'account_id': self.account_id}) - new_nb_transactions
        diff_balance = new_balance - bank_info['balance']

        return diff_nb_transaction, diff_balance

    def update(self, df_transactions):

        df_transaction = df_transactions.copy()

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

    def update_one_transaction(self, transaction_series):

        transaction_dict = transaction_series.to_dict()

        # Filter to get the selected document
        doc_filter = {'_id': ObjectId(transaction_dict['_id'])}

        # Remove the useless columns
        del transaction_dict['_id']

        # Values to be updated
        new_values = {"$set": transaction_dict}

        # Update the document
        current_doc = self.connection_transaction.collection.find_one(doc_filter)
        if current_doc is not None:
            self.connection_transaction.collection.update_one(doc_filter, new_values, upsert=False)
        else:
            raise ValueError("Impossible to update the doc because the object ID doesn't exist.")

    def _update_metadata(self, df, bank_info):

        new_nb_transactions = self.metadata.nb_transactions_bank + len(df)

        self.metadata.update_values(
            {
                # BANK
                'balance_in_bank': bank_info['balance'],
                'nb_transactions_bank': new_nb_transactions,
                'date_balance_in_bank': bank_info['date'],

                # DATABASE
                'balance_in_db': self._get_balance_in_db(),
                'nb_transactions_db': self.connection_transaction.collection.count(
                    {'account_id': self.account_id}),
                'date_last_import': self._get_lastest_date(),
            }
        )
        self.metadata.write_values_in_db()

    def _get_balance_in_db(self):
        balance_in_db = self.connection_transaction.collection.aggregate(
            pipeline=[
                {
                    "$match": {
                        "account_id": self.account_id
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "Somme": {
                            '$sum': "$amount"}
                    }
                }
            ]
        )
        balance_in_db = list(balance_in_db)
        balance_in_db = balance_in_db[0]['Somme'] if len(balance_in_db) > 0 else self.metadata.balance_in_db

        return balance_in_db

    def _get_lastest_date(self):
        date_latest = self.connection_transaction.collection.aggregate(
            pipeline=[
                {
                    "$match": {
                        "account_id": self.account_id
                    }
                },
                {
                    "$sort": {
                        "date_transaction.dt": -1,
                    }
                },
                {
                    "$limit": 1
                }
            ]
        )
        date_latest = list(date_latest)
        date_latest = date_latest[0]['date_transaction']['dt']\
            if len(date_latest) > 0 else self.metadata.date_last_import['dt']
        return date_latest

    def _count_nb_transactions(self):

        self.connection_transaction.collection.count()



