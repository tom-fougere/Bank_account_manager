import unittest
import numpy as np
from source.data_reader.bank_file_reader import BankTSVReader

from source.transactions.transaction_operations import *
from source.definitions import CATEGORIES, OCCASIONS

ACCOUNT_ID = '008'
DB_TITLE_CONNECTION = 'db_metadata_ut'


class TestDuplicate(unittest.TestCase):

    def test_check_duplicates_in_df(self):

        data_reader = BankTSVReader('test/fake_data.tsv')
        df_transactions = data_reader.get_dataframe()
        keys = list(df_transactions.keys())

        df2 = pd.DataFrame({'account_id': ['007', '007', '007'],
                            'amount': [-20.0, -9.99, 10.],
                            'date_str': ['07/01/2022', '06/01/2022', '07/01/2022'],
                            'date_transaction_str': ['07/01/2022', '06/01/2022', '07/01/2022'],
                            'description': ['TEST', 'TELECOM', ''],
                            'category': ['cat1', 'cat2', 'cat3'],
                            'sub_category': ['scat1', 'scat2', 'scat3'],
                            'occasion': ['occa1', 'occa2', 'occ3'],
                            'note': ['note1', 'note2', 'note3'],
                            'check': [True, False, True],
                            'type_transaction': ['type1', 'type2', 'type3']})

        check_duplicates_in_df(df_transactions, df2)

        self.assertEqual(keys + ['duplicate'], list(df_transactions.keys()))
        np.testing.assert_array_equal(df_transactions['duplicate'].values, [True, False, True])
        np.testing.assert_array_equal(df_transactions['category'].values, ['cat1', None, 'cat2'])
        np.testing.assert_array_equal(df_transactions['check'].values, [True, False, False])
        np.testing.assert_array_equal(df_transactions['type_transaction'].values, ['type1', 'ACHAT', 'type2'])


class TestSelectedColumns(unittest.TestCase):
    def test_keep_selected_columns_no_option(self):
        df = pd.DataFrame({'test1': [1],
                           'test2': [1],
                           'date_str': [1],
                           'test3': [1],
                           'description': [1],
                           'amount': [1],
                           'duplicate': [1],
                           'category': [1]})
        new_df = keep_selected_columns(df, show_new_data=False, show_category=False)

        self.assertEqual(len(new_df.keys()), 3)
        self.assertEqual('date_str' in new_df.keys(), True)
        self.assertEqual('description' in new_df.keys(), True)
        self.assertEqual('amount' in new_df.keys(), True)

    def test_keep_selected_columns_option_duplicate(self):
        df = pd.DataFrame({'test1': [1],
                           'amount': [1],
                           'duplicate': [1],
                           'category': [1]})
        new_df = keep_selected_columns(df, show_new_data=True, show_category=False)

        self.assertEqual(len(new_df.keys()), 2)
        self.assertEqual('amount' in new_df.keys(), True)
        self.assertEqual('duplicate' in new_df.keys(), True)

    def test_keep_selected_columns_option_category(self):
        df = pd.DataFrame({'test1': [1],
                           'amount': [1],
                           'duplicate': [1],
                           'sub_category': [1]})
        new_df = keep_selected_columns(df, show_new_data=False, show_category=True)

        self.assertEqual(len(new_df.keys()), 2)
        self.assertEqual('amount' in new_df.keys(), True)
        self.assertEqual('sub_category' in new_df.keys(), True)


class TestGetLists(unittest.TestCase):
    def test_get_categories(self):
        categories = get_categories(DB_TITLE_CONNECTION, ACCOUNT_ID)

        expected_categories = []
        for cat in CATEGORIES:
            expected_categories.append({'label': cat, 'value': cat})

        self.assertEqual(categories, expected_categories)

    def test_get_sub_categories_without_suffix(self):
        selected_category = 'Travail'
        sub_categories = get_sub_categories(DB_TITLE_CONNECTION, ACCOUNT_ID, categories=[selected_category],
                                            add_suffix_cat=False)

        expected_categories = []
        for cat in CATEGORIES[selected_category]:
            expected_categories.append({'label': cat, 'value': cat})

        self.assertEqual(sub_categories, expected_categories)

    def test_get_sub_categories_with_suffix(self):
        selected_category = 'Travail'
        sub_categories = get_sub_categories(DB_TITLE_CONNECTION, ACCOUNT_ID, categories=[selected_category],
                                            add_suffix_cat=True)

        expected_categories = []
        for cat in CATEGORIES[selected_category]:
            expected_categories.append({'label': selected_category + '/' + cat,
                                        'value': selected_category + '/' + cat})

        self.assertEqual(sub_categories, expected_categories)

    def test_get_occasions(self):
        occasions = get_occasion(DB_TITLE_CONNECTION, ACCOUNT_ID)

        expected_occasions = []
        for occ in OCCASIONS:
            expected_occasions.append({'label': occ, 'value': occ})

        self.assertEqual(occasions, expected_occasions)
