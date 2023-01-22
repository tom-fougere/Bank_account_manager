import datetime
import unittest
import pandas as pd

from source.transactions.transactions_db import TransactionDB
from source.data_reader.bank_file_reader import BankTSVReader
from source.transactions.exgest import TransactionExgest
from utils.time_operations import modify_date_str_format

ACCOUNT_ID = '008'
CONNECTION_TRANSACTION = 'db_ut'
CONNECTION_METADATA = 'db_metadata_ut'
DATE_NOW = datetime.datetime(2022, 4, 13)


class TestTransactionDB(unittest.TestCase):

    def setUp(self) -> None:

        # Create database for UT
        self.db = TransactionDB(
            name_connection=CONNECTION_TRANSACTION,
            account_id=ACCOUNT_ID,
        )

        # create list of transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        self.df_transactions = data_reader.get_dataframe()

        self.db.ingest(
            df_transactions=self.df_transactions,
        )

    def tearDown(self) -> None:
        # Remove all in the collection
        self.db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_ingest_and_delete(self):

        self.assertEqual(self.db.connection.collection.count(), len(self.df_transactions))

        self.db.delete_all()
        self.assertEqual(self.db.connection.collection.count(), 0)

    def test_delete(self):

        # Exgestion data to get only one transaction
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID})
        transactions = data_extractor.exgest()
        transactions = transactions.drop([0, 2])

        # Delete selected transaction
        self.db.delete(df_transactions=transactions)

        self.assertTrue(self.db.connection.collection.count(), len(self.df_transactions) - 1)

    def test_update(self):

        # Find transaction to update
        original_transaction = self.db.connection.collection.find_one(
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
        impossible_transaction = self.db.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        self.assertEqual(impossible_transaction, None)

        # Find updated transaction
        updated_transaction = self.db.connection.collection.find_one(
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

    def test_get_latest_date(self):

        latest_date = self.db.get_latest_date()
        self.assertEqual(latest_date, max(self.df_transactions['date_transaction_dt']))

    def test_get_nb_transactions(self):

        nb_transactions = self.db.get_nb_transactions()
        self.assertEqual(nb_transactions, len(self.df_transactions))

    def test_get_balance(self):

        balance = self.db.get_balance()
        self.assertEqual(balance, sum(self.df_transactions['amount']))

    def test_change_category_name(self):

        descriptions = ['TEST', 'FOOD', 'TELECOM']
        categories = ['Transport', 'Transport', 'Perso']
        sub_categories = ['Assurance', 'Carburant', 'Autre']

        for des, cat, sub_cat in zip(descriptions, categories, sub_categories):
            # Find transaction to update
            original_transaction = self.db.connection.collection.find_one(
                {'account_id': ACCOUNT_ID,
                 'description': des})
            object_id = str(original_transaction['_id'])

            # Transaction with new values
            new_trans_dict = {
                '_id': object_id,
                'account_id': ACCOUNT_ID,
                'description': des,
                'category': cat,
                'sub_category': sub_cat,
                'date_transaction_str': '2022-01-10',
                'date_str': '2022-01-11',
                'amount': 100.01,
                'occasion': "ponctuel",
                'transaction_type': "TYPE",
                'note': "#note",
                'check': True,
            }
            new_transaction = pd.DataFrame([new_trans_dict])

            # Ingestion of transactions
            self.db.update(new_transaction)

        # Update category 1
        self.db.change_category_name(
            name_previous_cat='Transport',
            name_previous_sub_cat='Assurance',
            name_new_cat=None,
            name_new_sub_cat="Carburant",
        )
        transaction = self.db.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        self.assertEqual(transaction['category'], "Transport")
        self.assertEqual(transaction['sub_category'], "Carburant")

        # Update category 2
        self.db.change_category_name(
            name_previous_cat='Transport',
            name_previous_sub_cat=None,
            name_new_cat="Perso",
            name_new_sub_cat=None,
        )
        transaction = self.db.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'TEST'})
        self.assertEqual(transaction['category'], "Perso")
        transaction = self.db.connection.collection.find_one(
            {'account_id': ACCOUNT_ID,
             'description': 'FOOD'})
        self.assertEqual(transaction['category'], "Perso")


if __name__ == '__main__':
    unittest.main()
