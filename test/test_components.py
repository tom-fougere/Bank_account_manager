import unittest
import datetime
from source.categories import (
    OCCASIONS,
    get_list_categories,
    get_sub_categories,
)
from apps.components import *

ACCOUNT_ID = '008'
DB_TITLE_CONNECTION = 'db_metadata_ut'


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:

        self.metadata_db = MetadataDB(DB_TITLE_CONNECTION, account_id=ACCOUNT_ID)

        self.metadata_db.set(balance_in_db=10.34,
                             balance_in_bank=8.84,
                             balance_bias=712.70,
                             date_last_import=datetime.datetime(2022, 4, 13),
                             date_balance_in_bank=datetime.datetime(2021, 12, 28))
        self.metadata_db.update_db()

    def tearDown(self) -> None:
        # Remove all in the collection
        self.metadata_db.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_get_categories(self):
        categories = get_categories_for_dropdown_menu(DB_TITLE_CONNECTION, ACCOUNT_ID)

        self.assertEqual(len(categories), len(get_list_categories()))

        for cat in categories:
            self.assertEqual(cat['label'], cat['value'])

    def test_get_sub_categories_without_suffix(self):
        selected_category = 'Travail'
        sub_categories = get_sub_categories_for_dropdown_menu(
            DB_TITLE_CONNECTION,
            ACCOUNT_ID,
            categories=[selected_category],
            add_suffix_cat=False)

        expected_categories = []
        for cat in get_sub_categories(selected_category):
            expected_categories.append({'label': cat, 'value': cat})

        self.assertEqual(sub_categories, expected_categories)

    def test_get_sub_categories_with_suffix(self):
        selected_category = 'Travail'
        sub_categories = get_sub_categories_for_dropdown_menu(
            DB_TITLE_CONNECTION,
            ACCOUNT_ID,
            categories=[selected_category],
            add_suffix_cat=True)

        expected_categories = []
        for cat in get_sub_categories(selected_category):
            expected_categories.append({'label': selected_category + ':' + cat,
                                        'value': selected_category + ':' + cat})

        self.assertEqual(sub_categories, expected_categories)

    def test_get_occasions(self):
        occasions = get_occasions_for_dropdown_menu(DB_TITLE_CONNECTION, ACCOUNT_ID)

        expected_occasions = []
        for occ in OCCASIONS:
            expected_occasions.append({'label': occ, 'value': occ})

        self.assertEqual(occasions, expected_occasions)


if __name__ == '__main__':
    unittest.main()
