import unittest
import datetime

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.metadata import MetadataDB
from source.definitions import CATEGORIES, OCCASIONS

BALANCE = -101.98
ACCOUNT_ID = '007'
DATE_LAST_IMPORT = datetime.datetime(2022, 4, 13)
DATE_LAST_TRANSACTION = datetime.datetime(2019, 12, 25)


class TestMetadataDB(unittest.TestCase):
    def setUp(self) -> None:

        my_connection = MongoDBConnection('db_metadata_ut')
        self.metadata_db = MetadataDB(my_connection)

        self.metadata_db.init_db(account_id=ACCOUNT_ID,
                                 balance=BALANCE,
                                 date_last_import=DATE_LAST_IMPORT,
                                 date_last_transaction=DATE_LAST_TRANSACTION)

    def tearDown(self) -> None:
        # Remove all in the collection
        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_init(self):

        result = self.metadata_db.connection.collection.find_one()

        self.assertEqual(len(result), 7)
        for key in ['_id', 'account_id', 'balance', 'categories']:
            self.assertEqual(key in result.keys(), True)
        self.assertEqual(result['account_id'], ACCOUNT_ID)
        self.assertEqual(result['balance'], BALANCE)
        self.assertEqual(result['categories'], CATEGORIES)
        self.assertEqual(result['occasions'], OCCASIONS)
        self.assertEqual(result['date_last_import']['dt'], DATE_LAST_IMPORT)
        self.assertEqual(result['date_last_import']['str'], '13/04/2022')
        self.assertEqual(result['date_last_transaction']['dt'], DATE_LAST_TRANSACTION)
        self.assertEqual(result['date_last_transaction']['str'], '25/12/2019')

        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_get_balance(self):
        balance = self.metadata_db.get_balance(account_id=ACCOUNT_ID)

        self.assertEqual(balance, BALANCE)

    def test_get_categories(self):
        categories = self.metadata_db.get_categories(account_id=ACCOUNT_ID)

        self.assertEqual(len(categories), len(CATEGORIES))
        self.assertEqual(categories, list(CATEGORIES.keys()))

    def test_get_sub_categories(self):
        for category in CATEGORIES.keys():
            sub_category = self.metadata_db.get_sub_categories(account_id=ACCOUNT_ID, category=category)

            self.assertEqual(CATEGORIES[category], sub_category)

    def test_get_occasions(self):
        occasions = self.metadata_db.get_occasions(account_id=ACCOUNT_ID)

        self.assertEqual(occasions, OCCASIONS)

    def test_get_date_last_transaction(self):
        date_last_transaction = self.metadata_db.get_date_last_transaction(account_id=ACCOUNT_ID)

        self.assertEqual(date_last_transaction, "25/12/2019")

    def test_get_date_last_import(self):
        date_last_import = self.metadata_db.get_date_last_import(account_id=ACCOUNT_ID)

        self.assertEqual(date_last_import, "13/04/2022")

    def test_update_balance(self):
        new_balance = 10.1
        self.metadata_db.update_balance(account_id=ACCOUNT_ID, balance=new_balance)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['balance'])
        self.assertEqual(doc['balance'], new_balance)

