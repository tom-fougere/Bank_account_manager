import unittest

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest
from source.data_reader.bank_file_reader import BankTSVReader
from utils.time_operations import str_to_datetime

ACCOUNT_ID = '008'


class TestTransactionIngest(unittest.TestCase):
    def setUp(self) -> None:

        # create list of transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        self.df_transactions = data_reader.get_dataframe()

        # Create connection
        self.my_connection = MongoDBConnection('db_ut')

        # Instantiate the ingestion class
        self.transInges = TransactionIngest(self.my_connection, self.df_transactions)

    def tearDown(self) -> None:
        # Remove all transactions in the collection
        result = self.transInges.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_ingest_one_new_transaction(self):

        # Get transactions
        df = self.df_transactions

        # Convert 2 fields of date as one with a dict
        df['date_transaction'] = \
            df.apply(lambda x: {'str': x.date_transaction_str, 'dt': x.date_transaction_dt}, axis=1)
        df['date'] = \
            df.apply(lambda x: {'str': x.date_str, 'dt': x.date_dt}, axis=1)
        df.drop(columns=['date_str', 'date_dt', 'date_transaction_str', 'date_transaction_dt'],
                axis=1,
                inplace=True)
        expected_transaction = df.iloc[0]

        # Ingestion of one transaction
        self.transInges.ingest_one_transaction(df.iloc[0])

        # get the transaction in the mongodb
        db_trans = self.transInges.connection.collection.find_one({"account_id": ACCOUNT_ID})
        # Remove id field for the comparison
        db_trans.pop('_id', None)

        # check equality
        self.assertEqual(expected_transaction.to_dict(), db_trans)

    def test_ingest_one_same_transaction(self):

        # Get transactions
        df = self.df_transactions

        # Convert 2 fields of date as one with a dict
        df['date_transaction'] = \
            df.apply(lambda x: {'str': x.date_transaction_str, 'dt': x.date_transaction_dt}, axis=1)
        df['date'] = \
            df.apply(lambda x: {'str': x.date_str, 'dt': x.date_dt}, axis=1)
        df.drop(columns=['date_str', 'date_dt', 'date_transaction_str', 'date_transaction_dt'],
                axis=1,
                inplace=True)
        expected_transaction = df.iloc[0]

        # Ingestion of one transaction
        self.transInges.ingest_one_transaction(expected_transaction)

        with self.assertRaises(Exception) as context:
            self.transInges.ingest_one_transaction(expected_transaction)

    def test_ingest(self):

        # Ingestion of transactions
        self.transInges.ingest()

        # get the transaction in the mongodb
        db_all_trans = self.transInges.connection.collection.find({"account_id": ACCOUNT_ID})

        self.assertEqual(len(list(db_all_trans)), len(self.df_transactions))

        idx = 0
        db_all_trans.rewind()  # Reset the index of the cursor
        for db_trans in db_all_trans:

            # Compare dates
            self.assertEqual(str_to_datetime(db_trans['date']['str'], date_format="%d/%m/%Y"),
                             db_trans['date']['dt'])
            self.assertEqual(str_to_datetime(db_trans['date_transaction']['str'], date_format="%d/%m/%Y"),
                             db_trans['date_transaction']['dt'])
            self.assertEqual(db_trans['date']['str'], self.df_transactions.loc[idx, 'date_str'])
            self.assertEqual(db_trans['date_transaction']['str'], self.df_transactions.loc[idx, 'date_transaction_str'])

            # Remove '_id' for comparison
            db_trans.pop('_id', None)
            db_trans.pop('date', None)
            db_trans.pop('date_transaction', None)

            current_df = self.df_transactions.iloc[idx].copy()
            current_df.drop(labels=['date_dt', 'date_str', 'date_transaction_dt', 'date_transaction_str'], inplace=True)

            # check equality
            self.assertEqual(current_df.to_dict(), db_trans)

            idx += 1


if __name__ == '__main__':
    unittest.main()
