import unittest
import datetime

from source.transactions.metadata import MetadataDB, LIST_ATTRIBUTES_METADATA
from source.categories import (
    OCCASIONS, TYPE_TRANSACTIONS, ALL_CATEGORIES,
    get_list_categories,
    get_sub_categories,
    get_list_categories_and_sub,
)

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

        self.metadata_db.set(balance_in_db=BALANCE_IN_DB,
                             balance_in_bank=BALANCE_IN_BANK,
                             balance_bias=BALANCE_BIAS,
                             date_last_import=DATE_LAST_IMPORT,
                             date_balance_in_bank=DATE_BALANCE_IN_BANK)
        self.metadata_db.update_db()
        self.metadata_db.set_from_db()

    def tearDown(self) -> None:
        # Remove all in the collection
        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_set(self):

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

    def test_set_from_db(self):

        # Data
        list_attributes_start = [
            'connection',
            'account_id',
        ]
        # Init
        metadata_db = MetadataDB(METADATA_CONNECTION_NAME, account_id=ACCOUNT_ID)
        list_attributes = []

        # Check before
        for attribute in LIST_ATTRIBUTES_METADATA:
            value = getattr(metadata_db, attribute)
            self.assertIsNone(value)

        # Apply function
        metadata_db.set_from_db()

        # Check after
        for attribute in LIST_ATTRIBUTES_METADATA:
            value = getattr(metadata_db, attribute)
            self.assertIsNotNone(value)

    def test_get_list_categories(self):
        categories = self.metadata_db.get_list_categories()

        self.assertEqual(len(categories), len(get_list_categories()))
        for cat in categories:
            self.assertTrue(cat in get_list_categories())

    def test_get_list_categories_and_sub(self):
        categories = self.metadata_db.get_list_categories_and_sub()
        self.assertEqual(type(categories), dict)
        self.assertDictEqual(categories, get_list_categories_and_sub())

    def test_get_list_subcategories(self):

        for cat in get_list_categories():
            sub_categories = self.metadata_db.get_list_subcategories(cat)
            self.assertEqual(sub_categories, get_sub_categories(cat))

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

    def test_update_values(self):
        metadata_db = MetadataDB(METADATA_CONNECTION_NAME, account_id="009")

        metadata_db.set(balance_in_db=BALANCE_IN_DB,
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

    def test_update_db(self):
        metadata_db = MetadataDB(METADATA_CONNECTION_NAME, account_id="009")

        metadata_db.set(balance_in_db=BALANCE_IN_DB,
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
        metadata_db.update_db()

        results = list(metadata_db.connection.collection.find({"account_id": "009"}))[0]

        self.assertEqual(results['balance_in_db'], new_values['balance_in_db'])
        self.assertEqual(results['balance_in_bank'], new_values['balance_in_bank'])
        self.assertEqual(results['balance_bias'], new_values['balance_bias'])
        self.assertEqual(results['date_last_import']['dt'], new_values['date_last_import'])
        self.assertEqual(results['date_balance_in_bank']['dt'], new_values['date_balance_in_bank'])
        self.assertEqual(results['nb_transactions_db'], new_values['nb_transactions_db'])

        metadata_db.connection.collection.remove({"account_id": "009"})

    def test_add_new_category(self):

        # Add new parent category
        new_cat = {
            "new_cat": {
                "Order": 10,
                "Default_occasion": "Def_occ"
            }
        }
        self.metadata_db.add_category(new_cat)

        self.assertTrue("new_cat" in self.metadata_db.categories.keys())
        self.assertEqual(self.metadata_db.categories["new_cat"]['Order'],
                         new_cat["new_cat"]['Order'])
        self.assertEqual(self.metadata_db.categories["new_cat"]['Default_occasion'],
                         new_cat["new_cat"]['Default_occasion'])
        self.assertEqual(self.metadata_db.categories["new_cat"]['Sub-categories'], {})

        # Add new sub-category
        new_sb_cat = {
            "new_sub_cat": {
                "Order": 2,
                "Default_occasion": "Def_occ_2"
            }
        }
        parent_cat = 'Perso'
        self.metadata_db.add_category(new_sb_cat, name_parent_category=parent_cat)

        self.assertTrue("new_sub_cat" in self.metadata_db.categories[parent_cat]['Sub-categories'].keys())
        self.assertEqual(self.metadata_db.categories[parent_cat]['Sub-categories']["new_sub_cat"],
                         new_sb_cat["new_sub_cat"])

        # Assert the values has been saved in the database (same asserts)
        self.metadata_db.set_from_db()
        self.assertTrue("new_cat" in self.metadata_db.categories.keys())
        self.assertEqual(self.metadata_db.categories["new_cat"]['Order'],
                         new_cat["new_cat"]['Order'])
        self.assertEqual(self.metadata_db.categories["new_cat"]['Default_occasion'],
                         new_cat["new_cat"]['Default_occasion'])
        self.assertEqual(self.metadata_db.categories["new_cat"]['Sub-categories'], {})
        self.assertTrue("new_sub_cat" in self.metadata_db.categories[parent_cat]['Sub-categories'].keys())
        self.assertEqual(self.metadata_db.categories[parent_cat]['Sub-categories']["new_sub_cat"],
                         new_sb_cat["new_sub_cat"])

    def test_remove_category(self):
        self.metadata_db.remove_category(
            name_category_to_remove='Assurance',
            name_parent_category='Transport'
        )
        self.metadata_db.remove_category(
            name_category_to_remove='Perso',
            name_parent_category=None
        )
        self.metadata_db.set_from_db()

        self.assertFalse('Assurance' in self.metadata_db.categories['Transport']['Sub-categories'].keys())
        self.assertFalse('Perso' in self.metadata_db.categories.keys())

    def test_update_category_properties(self):

        # Update parent category
        new_cat = {
            "new_Parent_cat": {
                "Default_occasion": "Default_occ",
                "Order": 11,
            }
        }
        previous_cat = self.metadata_db.categories['Perso']['Sub-categories']
        self.metadata_db.update_category_properties(
            name_category="Perso",
            name_parent_category=None,
            new_category=new_cat)
        self.metadata_db.set_from_db()

        self.assertFalse("Perso" in self.metadata_db.categories.keys())
        self.assertTrue("new_Parent_cat" in self.metadata_db.categories.keys())
        self.assertEqual(previous_cat, new_cat['new_Parent_cat']['Sub-categories'])
        self.assertEqual(
            self.metadata_db.categories['new_Parent_cat']["Default_occasion"],
            new_cat['new_Parent_cat']["Default_occasion"]
        )
        self.assertEqual(
            self.metadata_db.categories['new_Parent_cat']["Order"],
            new_cat['new_Parent_cat']["Order"]
        )

        # Update child category
        new_cat = {
            "new_cat": {
                "Default_occasion": "Default_occ",
                "Order": 10,
            }
        }
        self.metadata_db.update_category_properties(
            name_category="Assurance",
            name_parent_category="Transport",
            new_category=new_cat)
        self.metadata_db.set_from_db()

        self.assertFalse("Assurance" in self.metadata_db.categories['Transport']['Sub-categories'].keys())
        self.assertTrue("new_cat" in self.metadata_db.categories['Transport']['Sub-categories'].keys())
        self.assertEqual(self.metadata_db.categories['Transport']['Sub-categories']["new_cat"], new_cat['new_cat'])

    def test_change_parent_category(self):
        self.metadata_db.change_parent_category(
            name_category='Culture',
            name_current_parent_category='Sortie/Voyage',
            name_new_parent_category='Alimentation',
        )

        self.assertFalse("Culture" in self.metadata_db.categories['Sortie/Voyage']['Sub-categories'].keys())
        self.assertTrue("Culture" in self.metadata_db.categories['Alimentation']['Sub-categories'].keys())

