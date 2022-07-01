import datetime
import unittest
import pandas as pd

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest, TransactionDB
from source.data_ingestion.metadata import MetadataDB
from source.data_reader.bank_file_reader import BankTSVReader
from source.data_ingestion.exgest import TransactionExgest
from utils.time_operations import str_to_datetime, modify_date_str_format

ACCOUNT_ID = '008'
CONNECTION_TRANSACTION = 'db_ut'
CONNECTION_METADATA = 'db_metadata_ut'
DATE_NOW = datetime.datetime(2022, 4, 13)


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

    def test_update_existing_transaction(self):

        # Ingest test transactions
        self.transInges.ingest()

        # Find transaction to update
        original_transaction = self.transInges.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        object_id = str(original_transaction['_id'])

        # Transaction with new values
        new_trans_dict = {
            '_id': object_id,
            'account_id': ACCOUNT_ID,
            'date_transaction_str': '2022-01-10',
            'date_str': '2022-01-11',
            'description': "NEW",
            'amount': 100.01,
            'category': "Transport",
            'sub_category': "Assurance",
            'occasion': "ponctuel",
            'transaction_type': "TYPE",
            'note': "#note",
            'check': True,
        }
        new_transaction = pd.DataFrame([new_trans_dict])

        # Instantiate the ingestion class
        transUpdate = TransactionIngest(self.my_connection, new_transaction)

        # Ingestion of transactions
        transUpdate.update()

        # Previous transaction must be impossible to find
        impossible_transaction = self.transInges.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        self.assertEqual(impossible_transaction, None)

        # Find updated transaction
        updated_transaction = self.transInges.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'NEW'})

        # Assert every fields
        for key in ['account_id', 'description', 'amount', 'category', 'sub_category', 'occasion', 'transaction_type',
                    'note', 'check']:
            self.assertEqual(new_trans_dict[key], updated_transaction[key])
        self.assertEqual(modify_date_str_format(new_trans_dict['date_transaction_str'],
                                                current_format='%Y-%m-%d',
                                                new_format='%d/%m/%Y'),
                         updated_transaction['date_transaction']['str'])
        self.assertEqual(modify_date_str_format(new_trans_dict['date_str'],
                                                current_format='%Y-%m-%d',
                                                new_format='%d/%m/%Y'),
                         updated_transaction['date']['str'])

    def test_update_not_existing_transaction(self):
        # Ingest test transactions
        self.transInges.ingest()

        object_id = '000000000000000000000000'

        # Transaction with new values
        new_trans_dict = {
            '_id': object_id,
            'account_id': ACCOUNT_ID,
            'date_transaction_str': '2022-01-10',
            'date_str': '2022-01-11',
            'description': "NEW",
            'amount': 100.01,
            'category': "Transport",
            'sub_category': "Assurance",
            'occasion': "ponctuel",
            'transaction_type': "TYPE",
            'note': "#note",
            'check': True,
        }
        new_transaction = pd.DataFrame([new_trans_dict])

        # Instantiate the ingestion class
        transUpdate = TransactionIngest(self.my_connection, new_transaction)

        # Assert error during update
        with self.assertRaises(ValueError):
            transUpdate.update()


class TestTransactionDB(unittest.TestCase):

    def setUp(self) -> None:

        # Init databases with data
        self.metadata = MetadataDB(
            name_connection=CONNECTION_METADATA,
            account_id=ACCOUNT_ID,
        )
        self.metadata.init_db(
            balance_in_bank=1.1,
            balance_in_db=2.2,
            balance_bias=3.3,
            date_balance_in_bank=DATE_NOW,
            date_last_import=DATE_NOW,
        )

        # Create database for UT
        self.db = TransactionDB(
            name_connection_transaction=CONNECTION_TRANSACTION,
            name_connection_metadata=CONNECTION_METADATA,
            account_id=ACCOUNT_ID,
        )

    def tearDown(self) -> None:
        # Remove all in the collection
        self.db.connection_transaction.collection.remove({"account_id": ACCOUNT_ID})
        self.db.metadata.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_update_metadata(self):

        self.db._update_metadata(
            df=[1],
            bank_info={
                'balance': 100,
                'date': datetime.datetime(2021, 5, 24),
                'account_id': ACCOUNT_ID,
            }
        )

        self.assertEqual(self.db.metadata.balance_in_bank, 100)
        self.assertEqual(self.db.metadata.balance_in_db, 2.2)
        self.assertEqual(self.db.metadata.nb_transactions_db, 0)
        self.assertEqual(self.db.metadata.nb_transactions_bank, 1)
        self.assertEqual(self.db.metadata.date_balance_in_bank['dt'], datetime.datetime(2021, 5, 24))
        self.assertEqual(self.db.metadata.date_last_import['dt'], DATE_NOW)

    def test_ingest(self):
        # create list of transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        bank_info = data_reader.get_account_info()

        self.db.ingest(
            df_transactions=df_transactions,
            bank_info=bank_info
        )

        self.assertEqual(self.db.metadata.balance_in_bank, 300.48)
        self.assertEqual(self.db.metadata.balance_in_db, -34.99)
        self.assertEqual(self.db.metadata.nb_transactions_db, 3)
        self.assertEqual(self.db.metadata.nb_transactions_bank, 3)
        self.assertEqual(self.db.metadata.date_balance_in_bank['dt'], datetime.datetime(2022, 1, 8))
        self.assertEqual(self.db.metadata.date_last_import['dt'], datetime.datetime(2022, 1, 7))

    def test_delete(self):

        # Ingestion data
        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        bank_info = data_reader.get_account_info()
        self.db.ingest(
            df_transactions=df_transactions,
            bank_info=bank_info
        )

        # Exgestion data to get only one transaction
        con_transaction = MongoDBConnection(CONNECTION_TRANSACTION)
        data_extractor = TransactionExgest(con_transaction)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID})
        transactions = data_extractor.exgest()
        transactions = transactions.drop([0, 2])

        # Delete selected transaction
        self.db.delete(df_transactions=transactions)

        self.assertEqual(self.db.metadata.balance_in_bank, 300.48)
        self.assertEqual(self.db.metadata.balance_in_db, -34.99+5)
        self.assertEqual(self.db.metadata.nb_transactions_db, 2)
        self.assertEqual(self.db.metadata.nb_transactions_bank, 3)
        self.assertEqual(self.db.metadata.date_balance_in_bank['dt'], datetime.datetime(2022, 1, 8))
        self.assertEqual(self.db.metadata.date_last_import['dt'], datetime.datetime(2022, 1, 7))

    def test_check(self):

        new_trans_dict = {
            'amount': 9.81,
        }
        new_transaction = pd.DataFrame([new_trans_dict])

        diff_nb_trans, diff_balance = self.db.check(
            df_transactions=new_transaction,
            bank_info={
                'account_id': ACCOUNT_ID,
                'balance': 72.01,
            }
        )

        self.assertEqual(diff_balance, -60.0)
        self.assertEqual(diff_nb_trans, -1)

    def test_update(self):

        # Ingest test transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        bank_info = data_reader.get_account_info()
        self.db.ingest(
            df_transactions=df_transactions,
            bank_info=bank_info
        )

        # Find transaction to update
        original_transaction = self.db.connection_transaction.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        object_id = str(original_transaction['_id'])

        # Transaction with new values
        new_trans_dict = {
            '_id': object_id,
            'account_id': ACCOUNT_ID,
            'date_transaction_str': '2022-01-10',
            'date_str': '2022-01-11',
            'description': "NEW",
            'amount': 100.01,
            'category': "Transport",
            'sub_category': "Assurance",
            'occasion': "ponctuel",
            'transaction_type': "TYPE",
            'note': "#note",
            'check': True,
        }
        new_transaction = pd.DataFrame([new_trans_dict])

        # Ingestion of transactions
        self.db.update(new_transaction)

        # Previous transaction must be impossible to find
        impossible_transaction = self.db.connection_transaction.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        self.assertEqual(impossible_transaction, None)

        # Find updated transaction
        updated_transaction = self.db.connection_transaction.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'NEW'})

        # Assert every fields
        for key in ['account_id', 'description', 'amount', 'category', 'sub_category', 'occasion', 'transaction_type',
                    'note', 'check']:
            self.assertEqual(new_trans_dict[key], updated_transaction[key])
        self.assertEqual(modify_date_str_format(new_trans_dict['date_transaction_str'],
                                                current_format='%Y-%m-%d',
                                                new_format='%d/%m/%Y'),
                         updated_transaction['date_transaction']['str'])
        self.assertEqual(modify_date_str_format(new_trans_dict['date_str'],
                                                current_format='%Y-%m-%d',
                                                new_format='%d/%m/%Y'),
                         updated_transaction['date']['str'])

    def test_update_not_existing_transaction(self):
        # Ingest test transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        bank_info = data_reader.get_account_info()
        self.db.ingest(
            df_transactions=df_transactions,
            bank_info=bank_info
        )

        object_id = '000000000000000000000000'

        # Transaction with new values
        new_trans_dict = {
            '_id': object_id,
            'account_id': ACCOUNT_ID,
            'date_transaction_str': '2022-01-10',
            'date_str': '2022-01-11',
            'description': "NEW",
            'amount': 100.01,
            'category': "Transport",
            'sub_category': "Assurance",
            'occasion': "ponctuel",
            'transaction_type': "TYPE",
            'note': "#note",
            'check': True,
        }
        new_transaction = pd.DataFrame([new_trans_dict])

        # Assert error during update
        with self.assertRaises(ValueError):
            self.db.update(new_transaction)


if __name__ == '__main__':
    unittest.main()
