import unittest
import datetime

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.metadata import MetadataDB
from source.definitions import CATEGORIES, OCCASIONS

BALANCE = -101.98
ACCOUNT_ID = '007'
DATE_LAST_UPDATE = datetime.datetime(2022, 4, 13)
LAST_DATE = datetime.datetime(2019, 12, 25)


class TestMetadataDB(unittest.TestCase):
    def setUp(self) -> None:

        my_connection = MongoDBConnection('db_metadata_ut')
        self.metadata_db = MetadataDB(my_connection)

        self.metadata_db.init_db(account_id=ACCOUNT_ID,
                                 balance=BALANCE,
                                 date_late_update=DATE_LAST_UPDATE,
                                 last_date=LAST_DATE)

    def tearDown(self) -> None:
        # Remove all in the collection
        self.metadata_db.connection.collection.remove()

    def test_init(self):

        result = self.metadata_db.connection.collection.find_one()

        self.assertEqual(len(result), 7)
        for key in ['_id', 'account_id', 'balance', 'categories']:
            self.assertEqual(key in result.keys(), True)
        self.assertEqual(result['account_id'], ACCOUNT_ID)
        self.assertEqual(result['balance'], BALANCE)
        self.assertEqual(result['categories'], CATEGORIES)
        self.assertEqual(result['occasions'], OCCASIONS)
        self.assertEqual(result['date_last_update']['dt'], DATE_LAST_UPDATE)
        self.assertEqual(result['date_last_update']['str'], '13/04/2022')
        self.assertEqual(result['last_date']['dt'], LAST_DATE)
        self.assertEqual(result['last_date']['str'], '25/12/2019')

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

            self.assertEqual(CATEGORIES[category], sub_category)

    def test_get_occasions(self):
        occasions = self.metadata_db.get_occasions(account_id=ACCOUNT_ID)

        self.assertEqual(occasions, OCCASIONS)

    def test_get_last_date(self):
        last_date = self.metadata_db.get_last_date(account_id=ACCOUNT_ID)

        self.assertEqual(last_date, "25/12/2019")

    def test_get_date_last_update(self):
        date_last_update = self.metadata_db.get_date_last_update(account_id=ACCOUNT_ID)

        self.assertEqual(date_last_update, "13/04/2022")
