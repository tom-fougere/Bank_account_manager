import unittest

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.metadata import MetadataDB
from source.definitions import CATEGORIES

BALANCE = -101.98
ACCOUNT_ID = '007'


class TestMetadataDB(unittest.TestCase):
    def setUp(self) -> None:

        my_connection = MongoDBConnection('db_metadata_ut')
        self.metadata_db = MetadataDB(my_connection)

        self.metadata_db.init_db(account_id=ACCOUNT_ID,
                                 balance=BALANCE)

    def tearDown(self) -> None:
        # Remove all in the collection
        self.metadata_db.connection.collection.remove()

    def test_init(self):

        result = self.metadata_db.connection.collection.find_one()

        self.assertEqual(len(result), 4)
        for key in ['_id', 'account_id', 'balance', 'categories']:
            self.assertEqual(key in result.keys(), True)
        self.assertEqual(result['account_id'], ACCOUNT_ID)
        self.assertEqual(result['balance'], BALANCE)
        self.assertEqual(result['categories'], CATEGORIES)

        self.metadata_db.connection.collection.remove()

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

            print(sub_category)
