import unittest
import datetime

from source.transactions.metadata import MetadataDB
from source.definitions import CATEGORIES, OCCASIONS, TYPE_TRANSACTIONS, ALL_CATEGORIES

METADATA_CONNECTION_NAME = 'db_metadata_ut'
BALANCE_IN_DB = -101.98
BALANCE_IN_BANK = -223.67
BALANCE_BIAS = 54.3
ACCOUNT_ID = '008'
DATE_LAST_IMPORT = datetime.datetime(2022, 4, 13)
DATE_BALANCE_IN_BANK = datetime.datetime(2019, 12, 25)


class TestMetadataDB(unittest.TestCase):
    def setUp(self) -> None:

        self.metadata_db = MetadataDB(METADATA_CONNECTION_NAME, account_id=ACCOUNT_ID)

        self.metadata_db.init_db(balance_in_db=BALANCE_IN_DB,
                                 balance_in_bank=BALANCE_IN_BANK,
                                 balance_bias=BALANCE_BIAS,
                                 date_last_import=DATE_LAST_IMPORT,
                                 date_balance_in_bank=DATE_BALANCE_IN_BANK)

    def tearDown(self) -> None:
        # Remove all in the collection
        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_init(self):

        result = self.metadata_db.connection.collection.find_one()

        self.assertEqual(len(result), 11)
        self.assertEqual(result['account_id'], ACCOUNT_ID)
        self.assertEqual(result['balance_in_bank'], BALANCE_IN_BANK)
        self.assertEqual(result['balance_in_db'], BALANCE_IN_DB)
        self.assertEqual(result['balance_bias'], BALANCE_BIAS)
        self.assertEqual(result['categories'], ALL_CATEGORIES)
        self.assertEqual(result['occasions'], OCCASIONS)
        self.assertEqual(result['types_transaction'], TYPE_TRANSACTIONS)
        self.assertEqual(result['nb_transactions_db'], 0)
        self.assertEqual(result['date_last_import']['dt'], DATE_LAST_IMPORT)
        self.assertEqual(result['date_last_import']['str'], '13/04/2022')
        self.assertEqual(result['date_balance_in_bank']['dt'], DATE_BALANCE_IN_BANK)
        self.assertEqual(result['date_balance_in_bank']['str'], '25/12/2019')

        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_get_balance_in_db(self):
        balance = self.metadata_db.get_balance_in_db()

        self.assertEqual(balance, BALANCE_IN_DB)

    def test_get_balance_in_bank(self):
        balance = self.metadata_db.get_balance_in_bank()

        self.assertEqual(balance, BALANCE_IN_BANK)

    def test_get_balance_bias(self):
        balance_bias = self.metadata_db.get_balance_bias()

        self.assertEqual(balance_bias, BALANCE_BIAS)

    def test_get_categories(self):
        categories = self.metadata_db.get_categories()

        self.assertEqual(len(categories), len(CATEGORIES))
        for cat in categories:
            self.assertTrue(cat in list(CATEGORIES.keys()))

    def test_get_category_info(self):
        for cat in CATEGORIES:
            category_info = self.metadata_db.get_category_info(
                category=cat,
            )
            self.assertEqual(category_info, ALL_CATEGORIES[cat])

    def test_get_sub_categories(self):
        for category in CATEGORIES.keys():
            sub_categories = self.metadata_db.get_sub_categories(category=category)

            for sub_category, info in sub_categories.items():
                self.assertTrue(sub_category in CATEGORIES[category])
                self.assertEqual(ALL_CATEGORIES[category]['Sub-categories'][sub_category], info)

    def test_get_categories_and_sub(self):
        categories = self.metadata_db.get_categories_and_sub()
        self.assertEqual(type(categories), dict)
        self.assertDictEqual(categories, CATEGORIES)

    def test_get_occasions(self):
        occasions = self.metadata_db.get_list_occasions()

        self.assertEqual(occasions, OCCASIONS)

    def test_get_default_occasion(self):

        for cat, cat_info in ALL_CATEGORIES.items():
            if len(cat_info['Sub-categories']) > 0:
                for sub_cat in list(cat_info['Sub-categories'].keys()):
                    occasion = self.metadata_db.get_default_occasion(
                        category=cat,
                        sub_category=sub_cat,
                    )
                    self.assertEqual(occasion, cat_info['Sub-categories'][sub_cat]['Default_occasion'])
            else:
                occasion = self.metadata_db.get_default_occasion(
                    category=cat,
                    sub_category=None,
                )
                self.assertEqual(occasion, cat_info['Default_occasion'])

    def test_get_types_transaction(self):
        types = self.metadata_db.get_types_transaction()

        self.assertEqual(types, TYPE_TRANSACTIONS)

    def test_get_date_balance_in_bank(self):
        date_last_transaction = self.metadata_db.get_date_balance_in_bank()

        self.assertEqual(date_last_transaction, "25/12/2019")

    def test_get_date_last_import(self):
        date_last_import = self.metadata_db.get_date_last_import()

        self.assertEqual(date_last_import, "13/04/2022")

    def test_get_nb_transactions_db(self):
        nb_transactions = self.metadata_db.get_nb_transactions_db()

        self.assertEqual(nb_transactions, 0)

    def test_update_balance_in_bank(self):
        new_balance = 10.1
        self.metadata_db.update_balance_in_bank(balance=new_balance)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['balance_in_bank',
                                                                                           'balance_in_db'])
        self.assertEqual(doc['balance_in_bank'], new_balance)
        self.assertEqual(doc['balance_in_db'], BALANCE_IN_DB)

    def test_update_balance_in_bb(self):
        new_balance = 10.1
        self.metadata_db.update_balance_in_db(balance=new_balance)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['balance_in_bank',
                                                                                           'balance_in_db'])
        self.assertEqual(doc['balance_in_bank'], BALANCE_IN_BANK)
        self.assertEqual(doc['balance_in_db'], new_balance)

    def test_update_date_balance_in_bank(self):
        new_date = datetime.datetime(2023, 11, 1)
        self.metadata_db.update_date_balance_in_bank(date=new_date)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['date_balance_in_bank'])
        self.assertEqual(doc['date_balance_in_bank']['dt'], new_date)
        self.assertEqual(doc['date_balance_in_bank']['str'], new_date.strftime("%d/%m/%Y"))

    def test_update_date_last_import(self):
        new_date = datetime.datetime(2023, 11, 1)
        self.metadata_db.update_date_last_import(date=new_date)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID}, ['date_last_import'])
        self.assertEqual(doc['date_last_import']['dt'], new_date)
        self.assertEqual(doc['date_last_import']['str'], new_date.strftime("%d/%m/%Y"))

    def test_update_nb_transactions(self):
        self.metadata_db.update_nb_transactions(new_nb_trans_db=3, new_nb_trans_bank=4)

        doc = self.metadata_db.connection.collection.find_one({'account_id': ACCOUNT_ID},
                                                              ['nb_transactions_db'])
        self.assertEqual(doc['nb_transactions_db'], 3)

    def test_get_all_values(self):

        metadata_db = MetadataDB(METADATA_CONNECTION_NAME, account_id="009")

        metadata_db.init_db(balance_in_db=BALANCE_IN_DB,
                            balance_in_bank=BALANCE_IN_BANK,
                            balance_bias=BALANCE_BIAS,
                            date_last_import=DATE_LAST_IMPORT,
                            date_balance_in_bank=DATE_BALANCE_IN_BANK,
                            nb_trans_db=3)

        metadata_db.get_all_values()

        self.assertEqual(metadata_db.balance_in_bank, BALANCE_IN_BANK)
        self.assertEqual(metadata_db.balance_in_db, BALANCE_IN_DB)
        self.assertEqual(metadata_db.balance_bias, BALANCE_BIAS)
        self.assertEqual(metadata_db.nb_transactions_db, 3)
        self.assertEqual(metadata_db.date_balance_in_bank['dt'], DATE_BALANCE_IN_BANK)
        self.assertEqual(metadata_db.date_balance_in_bank['str'], DATE_BALANCE_IN_BANK.strftime("%d/%m/%Y"))
        self.assertEqual(metadata_db.date_last_import['dt'], DATE_LAST_IMPORT)
        self.assertEqual(metadata_db.date_last_import['str'], DATE_LAST_IMPORT.strftime("%d/%m/%Y"))

        metadata_db.connection.collection.remove({"account_id": "009"})

    def test_update_values(self):
        metadata_db = MetadataDB(METADATA_CONNECTION_NAME, account_id="009")

        metadata_db.init_db(balance_in_db=BALANCE_IN_DB,
                            balance_in_bank=BALANCE_IN_BANK,
                            balance_bias=BALANCE_BIAS,
                            date_last_import=DATE_LAST_IMPORT,
                            date_balance_in_bank=DATE_BALANCE_IN_BANK,
                            nb_trans_db=3)

        new_values = {
            'balance_in_db': 100.01,
            'balance_in_bank': -99.99,
            'balance_bias': 0.75,
            'date_last_import': datetime.datetime(2021, 9, 10),
            'date_balance_in_bank': datetime.datetime(2021, 3, 17),
            'nb_transactions_db': 10,
        }

        metadata_db.update_values(new_values)

        self.assertEqual(metadata_db.balance_in_db, new_values['balance_in_db'])
        self.assertEqual(metadata_db.balance_in_bank, new_values['balance_in_bank'])
        self.assertEqual(metadata_db.balance_bias, new_values['balance_bias'])
        self.assertEqual(metadata_db.date_last_import['dt'], new_values['date_last_import'])
        self.assertEqual(metadata_db.date_balance_in_bank['dt'], new_values['date_balance_in_bank'])
        self.assertEqual(metadata_db.nb_transactions_db, new_values['nb_transactions_db'])

        metadata_db.connection.collection.remove({"account_id": "009"})

    def test_write_values_in_db(self):
        metadata_db = MetadataDB(METADATA_CONNECTION_NAME, account_id="009")

        metadata_db.init_db(balance_in_db=BALANCE_IN_DB,
                            balance_in_bank=BALANCE_IN_BANK,
                            balance_bias=BALANCE_BIAS,
                            date_last_import=DATE_LAST_IMPORT,
                            date_balance_in_bank=DATE_BALANCE_IN_BANK,
                            nb_trans_db=3)

        new_values = {
            'balance_in_db': 100.01,
            'balance_in_bank': -99.99,
            'balance_bias': 0.75,
            'date_last_import': datetime.datetime(2021, 9, 10),
            'date_balance_in_bank': datetime.datetime(2021, 3, 17),
            'nb_transactions_db': 10,
        }

        metadata_db.update_values(new_values)
        metadata_db.write_values_in_db()

        results = list(metadata_db.connection.collection.find({"account_id": "009"}))[0]

        self.assertEqual(results['balance_in_db'], new_values['balance_in_db'])
        self.assertEqual(results['balance_in_bank'], new_values['balance_in_bank'])
        self.assertEqual(results['balance_bias'], new_values['balance_bias'])
        self.assertEqual(results['date_last_import']['dt'], new_values['date_last_import'])
        self.assertEqual(results['date_balance_in_bank']['dt'], new_values['date_balance_in_bank'])
        self.assertEqual(results['nb_transactions_db'], new_values['nb_transactions_db'])

        metadata_db.connection.collection.remove({"account_id": "009"})
