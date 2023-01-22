from bson.objectid import ObjectId
from utils.time_operations import str_to_datetime, modify_date_str_format
from source.db_connection.db_access import MongoDBConnection


class TransactionDB:
    def __init__(self, name_connection, account_id):

        self.connection = MongoDBConnection(name_connection)
        self.account_id = account_id

    @staticmethod
    def format_transactions_dataframe(df_transactions):

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

    def ingest(self, df_transactions):

        # Format dataframe (removing useless columns and format dates)
        df_transactions_formatted = self.format_transactions_dataframe(df_transactions)

        # Insert transactions
        self.connection.collection.insert_many(df_transactions_formatted.to_dict('records'))

    def delete(self, df_transactions):

        assert '_id' in df_transactions.columns

        # Remove transactions in the transaction DB
        for idx, row in df_transactions.iterrows():
            self.connection.collection.delete_one({"_id": ObjectId(row['_id'])})

    def delete_all(self):
        self.connection.collection.delete_many({"account_id": self.account_id})

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
        current_doc = self.connection.collection.find_one(doc_filter)
        if current_doc is not None:
            self.connection.collection.update_one(doc_filter, new_values, upsert=False)
        else:
            raise ValueError("Impossible to update the doc because the object ID doesn't exist.")

    def get_latest_date(self):
        date_latest = self.connection.collection.aggregate(
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
        date_latest = date_latest[0]['date_transaction']['dt'] if len(date_latest) > 0 else None
        return date_latest

    def get_nb_transactions(self):

        return self.connection.collection.count()

    def get_balance(self):

        balance_in_db = self.connection.collection.aggregate(
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
        balance_in_db = balance_in_db[0]['Somme'] if len(balance_in_db) > 0 else None

        return balance_in_db

    def change_category_name(self, name_previous_cat, name_previous_sub_cat, name_new_cat, name_new_sub_cat):

        assert name_previous_cat is not None
        assert (name_new_cat is not None or name_new_sub_cat is not None)

        # Define filter
        query_filter = {
            "category": name_previous_cat,
        }
        if name_previous_sub_cat is not None:
            query_filter.update({"sub_category": name_previous_sub_cat})

        # Define new set
        query_changes = {}
        if name_new_cat is not None:
            query_changes.update({"category": name_new_cat})
        if name_new_sub_cat is not None:
            query_changes.update({"sub_category": name_new_sub_cat})

        if len(query_changes) > 0:
            query_set = {
                "$set": query_changes
            }

            # Update transaction's categories name
            self.update_many(
                query_filter=query_filter,
                query_action=query_set,
            )

    def change_occasion(self, name_category, name_sub_category, previous_occasion, new_occasion):

        assert name_category is not None
        assert previous_occasion is not None
        assert new_occasion is not None

        # Define filter
        query_filter = {
            "category": name_category,
            "occasion": previous_occasion
        }
        if name_sub_category is not None:
            query_filter.update({"sub_category": name_sub_category})

        query_set = {
            "$set": {
                "occasion": new_occasion
            }
        }

        # Update transaction's occasion
        self.update_many(
            query_filter=query_filter,
            query_action=query_set,
        )

    def update_many(self, query_filter, query_action):

        return self.connection.collection.update_many(
            query_filter, query_action
        )


