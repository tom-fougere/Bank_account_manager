import unittest
import pandas as pd
import numpy as np
from source.data_reader.bank_file_reader import BankTSVReader

from source.transactions.transaction_operations import check_duplicates_in_df


class TestMixedUtils(unittest.TestCase):

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