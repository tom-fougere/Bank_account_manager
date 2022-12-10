import unittest
from mock import patch
import pandas as pd
import numpy as np

from utils.time_operations import str_to_datetime
from source.data_reader.bank_file_reader import BankTSVReader


class TestBankCSVReader(unittest.TestCase):
    def setUp(self):
        self.reader = BankTSVReader('test/fake_data.tsv')

    def test_clean_description(self):
        self.reader.data = pd.DataFrame({'description': ['     spaces     2    ',
                                                         'PYTHON CARTE NUMERO     569']})

        self.reader.clean_description()

        self.assertEqual(self.reader.data['description'][0] == 'spaces 2', True)
        self.assertEqual(self.reader.data['description'][1] == 'PYTHON', True)

    def test_manage_transaction_date(self):

        self.reader.data = pd.DataFrame({'description': ['python 12.02.05 ruby',
                                                         'FORTRAN'],
                                         'date_str': ['13/03/2006',
                                                      '24/11/2022']})

        self.assertEqual(self.reader.data.shape[1], 2)
        self.reader.manage_transaction_date()

        self.assertEqual(self.reader.data.shape[1], 4)
        self.assertEqual('date_transaction_str' in self.reader.data.keys(), True)
        self.assertEqual('date_transaction_dt' in self.reader.data.keys(), True)
        self.assertEqual(self.reader.data['description'][0], 'python  ruby')
        self.assertEqual(self.reader.data['date_transaction_str'][0], '12/02/2005')
        self.assertEqual(self.reader.data['date_transaction_str'][1], '24/11/2022')
        self.assertEqual(self.reader.data['date_transaction_dt'][0], str_to_datetime('12/02/2005',
                                                                                     date_format='%d/%m/%Y'))
        self.assertEqual(self.reader.data['date_transaction_dt'][1], str_to_datetime('24/11/2022',
                                                                                     date_format='%d/%m/%Y'))

    def test_manage_transaction_type(self):

        map_transaction_type = {'VIREMENT DE ': 'VIREMENT',
                                'VIREMENT POUR ': 'VIREMENT',
                                'ACHAT CB ': 'ACHAT',
                                'CREDIT ': 'CREDIT',
                                'PRELEVEMENT DE ': 'PRELEVEMENT'}

        self.reader.data = pd.DataFrame({'description': list(map_transaction_type.keys()) + ['NO KEY']})

        self.assertEqual(self.reader.data.shape[1], 1)
        self.reader.manage_transaction_type()

        df = self.reader.get_dataframe()
        self.assertEqual(df.shape[1], 2)
        self.assertEqual('type_transaction' in df.keys(), True)
        self.assertEqual(df['type_transaction'][0], 'VIREMENT')
        self.assertEqual(df['type_transaction'][1], 'VIREMENT')
        self.assertEqual(df['type_transaction'][2], 'ACHAT')
        self.assertEqual(df['type_transaction'][3], 'CREDIT')
        self.assertEqual(df['type_transaction'][4], 'PRELEVEMENT')
        self.assertEqual(df['type_transaction'][5], None)

        self.assertEqual(df['description'][0], '')
        self.assertEqual(df['description'][1], '')
        self.assertEqual(df['description'][2], '')
        self.assertEqual(df['description'][3], '')
        self.assertEqual(df['description'][4], '')
        self.assertEqual(df['description'][5], 'NO KEY')

    def test_format_date(self):
        self.reader.data = pd.DataFrame({'date_str': ['\n12/02/2005',
                                                      '13/03/2006']})

        self.reader.format_date()

        df = self.reader.get_dataframe()
        self.assertEqual(df['date_str'][0], '12/02/2005')
        self.assertEqual(df['date_str'][1], '13/03/2006')
        self.assertEqual(df['date_dt'][0], str_to_datetime('12/02/2005', date_format='%d/%m/%Y'))
        self.assertEqual(df['date_dt'][1], str_to_datetime('13/03/2006', date_format='%d/%m/%Y'))

    def test_convert_amount_in_float(self):

        self.reader.data = pd.DataFrame({'amount': ['15,5', '-5,8']})

        self.reader.convert_amount_in_float()

        df = self.reader.get_dataframe()
        self.assertEqual(df['amount'][0], 15.5)
        self.assertEqual(df['amount'][1], -5.8)

    def test_format_dataframe(self):

        self.reader.data = pd.DataFrame({'amount': [1, 2],
                                         'amount_f': [3, 4]})

        self.reader.format_dataframe()

        df = self.reader.get_dataframe()
        self.assertEqual(df.shape, (2, 7))

        self.assertEqual('amount_f' in df.keys(), False)
        np.testing.assert_array_equal(df['account_id'].values, [self.reader.account_id]*2)
        np.testing.assert_array_equal(df['check'].values, [False, False])
        for att in ['category', 'sub_category', 'occasion', 'note']:
            np.testing.assert_array_equal(df[att].values, [None]*2)

    def test_read_raw_data(self):

        df = self.reader.get_dataframe()

        self.assertEqual(df.shape, (3, 13))
        self.assertEqual(df['date_str'][0], '07/01/2022')
        self.assertEqual(df['date_dt'][0], str_to_datetime('07/01/2022', date_format='%d/%m/%Y'))
        self.assertEqual(df['account_id'][0], '008')
        self.assertEqual(df['description'][1], 'FOOD')
        self.assertEqual(df['amount'][1], -5.)
        self.assertEqual(df['type_transaction'][2], 'PRELEVEMENT')
        self.assertEqual(df['date_transaction_str'][2], self.reader.data['date_str'][2])
        self.assertEqual(df['check'][2], False)

        for att in ['category', 'sub_category', 'occasion', 'note']:
            self.assertEqual(df[att][0], None)
            self.assertEqual(df[att][1], None)
            self.assertEqual(df[att][2], None)

    def test_read_header(self):

        self.assertEqual(self.reader.account_id, '008')
        self.assertEqual(self.reader.date.day, 8)
        self.assertEqual(self.reader.date.month, 1)
        self.assertEqual(self.reader.date.year, 2022)
        self.assertEqual(self.reader.balance, 300.48)

    def test_get_account_info(self):
        info = self.reader.get_account_info()

        self.assertEqual(info, {'account_id': '008',
                                'balance': 300.48,
                                'date': str_to_datetime('08/01/2022', date_format='%d/%m/%Y')})


if __name__ == '__main__':
    unittest.main()
