import datetime
import unittest
import pandas as pd

from source.transactions.account_manager_db import AccountManagerDB
from source.transactions.metadata import MetadataDB
from source.data_reader.bank_file_reader import BankTSVReader
from source.transactions.exgest import TransactionExgest
from utils.time_operations import modify_date_str_format

ACCOUNT_ID = '008'
CONNECTION_TRANSACTION = 'db_ut'
CONNECTION_METADATA = 'db_metadata_ut'
DATE_NOW = datetime.datetime(2022, 4, 13)


class TestAccountManagerDB(unittest.TestCase):

    def setUp(self) -> None:

        # Init databases with data
        self.metadata = MetadataDB(
            name_connection=CONNECTION_METADATA,
            account_id=ACCOUNT_ID,
        )
        self.metadata.set(
            balance_in_bank=1.1,
            balance_in_db=2.2,
            balance_bias=3.3,
            date_balance_in_bank=DATE_NOW,
            date_last_import=DATE_NOW,
        )
        self.metadata.update_db()

        # Create database for UT
        self.db = AccountManagerDB(
            name_connection_transaction=CONNECTION_TRANSACTION,
            name_connection_metadata=CONNECTION_METADATA,
            account_id=ACCOUNT_ID,
        )

    def tearDown(self) -> None:
        # Remove all in the collection
        self.db.transactions_db.connection.collection.delete_many({"account_id": ACCOUNT_ID})
        self.db.metadata_db.connection.collection.delete_many({"account_id": ACCOUNT_ID})

    def test_ingest(self):
        # create list of transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        bank_info = data_reader.get_account_info()

        self.db.ingest(
            df_transactions=df_transactions,
            bank_info=bank_info
        )

        self.assertEqual(self.db.transactions_db.get_nb_transactions(), len(df_transactions))
        self.assertEqual(self.db.metadata_db.balance_in_bank, bank_info['balance'])
        self.assertEqual(self.db.metadata_db.balance_in_db, sum(df_transactions['amount']))
        self.assertEqual(self.db.metadata_db.nb_transactions_db, len(df_transactions))
        self.assertEqual(self.db.metadata_db.date_balance_in_bank['dt'], datetime.datetime(2022, 1, 8))
        self.assertEqual(self.db.metadata_db.date_last_import['dt'], datetime.datetime(2022, 1, 7))

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
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID})
        transactions = data_extractor.exgest()
        transactions = transactions.drop([0, 2])

        # Delete selected transaction
        self.db.delete(df_transactions=transactions)

        self.assertEqual(self.db.metadata_db.balance_in_bank, bank_info['balance'])
        self.assertEqual(self.db.metadata_db.balance_in_db, sum(df_transactions['amount'])+5)
        self.assertEqual(self.db.metadata_db.nb_transactions_db, len(df_transactions)-1)
        self.assertEqual(self.db.metadata_db.date_balance_in_bank['dt'], datetime.datetime(2022, 1, 8))
        self.assertEqual(self.db.metadata_db.date_last_import['dt'], datetime.datetime(2022, 1, 7))

    def test_check_consistency(self):

        # Ingestion data
        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        bank_info = data_reader.get_account_info()
        self.db.ingest(
            df_transactions=df_transactions,
            bank_info=bank_info
        )

        results = self.db.check_consistency()

        for key, value in results.items():
            self.assertTrue(value)

    def test_check_with_new_transactions(self):

        new_trans_dict = {
            'amount': 9.81,
        }
        new_transaction = pd.DataFrame([new_trans_dict])

        result = self.db.check_with_new_transactions(
            df_transactions=new_transaction,
            bank_info={
                'account_id': ACCOUNT_ID,
                'balance': 72.01,
            }
        )

        self.assertEqual(result['balance_bank'], 72.01)
        self.assertEqual(result['potential_balance'], 2.2+3.3+9.81)
        self.assertEqual(result['difference'], 2.2+3.3+9.81-72.01)
        self.assertFalse(result['identical'])

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
        original_transaction = self.db.transactions_db.connection.collection.find_one(
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
        impossible_transaction = self.db.transactions_db.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        self.assertEqual(impossible_transaction, None)

        # Find updated transaction
        updated_transaction = self.db.transactions_db.connection.collection.find_one(
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

    def test_update_metadata(self):

        # create list of transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        bank_info = data_reader.get_account_info()

        self.db.ingest(
            df_transactions=df_transactions,
            bank_info=bank_info
        )

        self.db._update_metadata(
            bank_info={
                'balance': 100,
                'date': datetime.datetime(2021, 5, 24),
                'account_id': ACCOUNT_ID,
            }
        )

        self.assertEqual(self.db.metadata_db.balance_in_bank, 100)
        self.assertEqual(self.db.metadata_db.date_balance_in_bank['dt'], datetime.datetime(2021, 5, 24))

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

    def test_add_new_category(self):
        pass

    def test_update_category_properties(self):
        pass

    def test_remove_category(self):
        pass


if __name__ == '__main__':
    unittest.main()
