import unittest
import datetime

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.metadata import MetadataDB
from source.definitions import CATEGORIES, OCCASIONS

BALANCE_IN_DB = -101.98
BALANCE_IN_BANK = -223.67
BALANCE_BIAS = 54.3
ACCOUNT_ID = '007'
DATE_LAST_IMPORT = datetime.datetime(2022, 4, 13)
DATE_BALANCE_IN_BANK = datetime.datetime(2019, 12, 25)


class TestMetadataDB(unittest.TestCase):
    def setUp(self) -> None:

        my_connection = MongoDBConnection('db_metadata_ut')
        self.metadata_db = MetadataDB(my_connection)

        self.metadata_db.init_db(account_id=ACCOUNT_ID,
                                 balance_in_db=BALANCE_IN_DB,
                                 balance_in_bank=BALANCE_IN_BANK,
                                 balance_bias=BALANCE_BIAS,
                                 date_last_import=DATE_LAST_IMPORT,
                                 date_balance_in_bank=DATE_BALANCE_IN_BANK)

    def tearDown(self) -> None:
        # Remove all in the collection
        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_init(self):

        result = self.metadata_db.connection.collection.find_one()

        self.assertEqual(len(result), 9)
        self.assertEqual(result['account_id'], ACCOUNT_ID)
        self.assertEqual(result['balance_in_bank'], BALANCE_IN_BANK)
        self.assertEqual(result['balance_in_db'], BALANCE_IN_DB)
        self.assertEqual(result['balance_bias'], BALANCE_BIAS)
        self.assertEqual(result['categories'], CATEGORIES)
        self.assertEqual(result['occasions'], OCCASIONS)
        self.assertEqual(result['date_last_import']['dt'], DATE_LAST_IMPORT)
        self.assertEqual(result['date_last_import']['str'], '13/04/2022')
        self.assertEqual(result['date_balance_in_bank']['dt'], DATE_BALANCE_IN_BANK)
        self.assertEqual(result['date_balance_in_bank']['str'], '25/12/2019')

        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_get_balance_in_db(self):
        balance = self.metadata_db.get_balance_in_db(account_id=ACCOUNT_ID)

        self.assertEqual(balance, BALANCE_IN_DB)

    def test_get_balance_in_bank(self):
        balance = self.metadata_db.get_balance_in_bank(account_id=ACCOUNT_ID)

        self.assertEqual(balance, BALANCE_IN_BANK)

    def test_get_balance_bias(self):
        balance_bias = self.metadata_db.get_balance_bias(account_id=ACCOUNT_ID)

        self.assertEqual(balance_bias, BALANCE_BIAS)

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

    def test_get_date_balance_in_bank(self):
        date_last_transaction = self.metadata_db.get_date_balance_in_bank(account_id=ACCOUNT_ID)

        self.assertEqual(date_last_transaction, "25/12/2019")

    def test_get_date_last_import(self):
        date_last_import = self.metadata_db.get_date_last_import(account_id=ACCOUNT_ID)

        self.assertEqual(date_last_import, "13/04/2022")

    def test_update_balance_in_bank(self):
        new_balance = 10.1
        self.metadata_db.update_balance_in_bank(account_id=ACCOUNT_ID, balance=new_balance)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['balance_in_bank',
                                                                                           'balance_in_db'])
        self.assertEqual(doc['balance_in_bank'], new_balance)
        self.assertEqual(doc['balance_in_db'], BALANCE_IN_DB)

    def test_update_balance_in_bb(self):
        new_balance = 10.1
        self.metadata_db.update_balance_in_db(account_id=ACCOUNT_ID, balance=new_balance)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['balance_in_bank',
                                                                                           'balance_in_db'])
        self.assertEqual(doc['balance_in_bank'], BALANCE_IN_BANK)
        self.assertEqual(doc['balance_in_db'], new_balance)

    def test_update_date_balance_in_bank(self):
        new_date = datetime.datetime(2023, 11, 1)
        self.metadata_db.update_date_balance_in_bank(account_id=ACCOUNT_ID, date=new_date)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['date_balance_in_bank'])
        self.assertEqual(doc['date_balance_in_bank']['dt'], new_date)
        self.assertEqual(doc['date_balance_in_bank']['str'], new_date.strftime("%d/%m/%Y"))

    def test_update_date_last_import(self):
        new_date = datetime.datetime(2023, 11, 1)
        self.metadata_db.update_date_last_import(account_id=ACCOUNT_ID, date=new_date)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['date_last_import'])
        self.assertEqual(doc['date_last_import']['dt'], new_date)
        self.assertEqual(doc['date_last_import']['str'], new_date.strftime("%d/%m/%Y"))

