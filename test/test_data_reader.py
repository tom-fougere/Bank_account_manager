import unittest
from mock import patch
import pandas as pd

from source.data_reader.bank_file_reader import BankTSVReader, create_list_transactions_from_file


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
                                                         'FORTRAN']})

        self.assertEqual(self.reader.data.shape[1], 1)
        self.reader.manage_transaction_date()

        self.assertEqual(self.reader.data.shape[1], 2)
        self.assertEqual('date_transaction' in self.reader.data.keys(), True)
        self.assertEqual(self.reader.data['description'][0], 'python  ruby')
        self.assertEqual(self.reader.data['date_transaction'][1].day, 1)
        self.assertEqual(self.reader.data['date_transaction'][1].month, 1)
        self.assertEqual(self.reader.data['date_transaction'][1].year, 2000)
        self.assertEqual(self.reader.data['date_transaction'][0].day, 12)
        self.assertEqual(self.reader.data['date_transaction'][0].month, 2)
        self.assertEqual(self.reader.data['date_transaction'][0].year, 2005)

    def test_manage_transaction_type(self):

        map_transaction_type = {'VIREMENT DE ': 'VIREMENT',
                                'VIREMENT POUR ': 'VIREMENT',
                                'ACHAT CB ': 'ACHAT',
                                'CREDIT ': 'CREDIT',
                                'PRELEVEMENT DE ': 'PRELEVEMENT'}

        self.reader.data = pd.DataFrame({'description': list(map_transaction_type.keys()) + ['NO KEY']})

        self.assertEqual(self.reader.data.shape[1], 1)
        self.reader.manage_transaction_type()

        self.assertEqual(self.reader.data.shape[1], 2)
        self.assertEqual('type_transaction' in self.reader.data.keys(), True)
        self.assertEqual(self.reader.data['type_transaction'][0], 'VIREMENT')
        self.assertEqual(self.reader.data['type_transaction'][1], 'VIREMENT')
        self.assertEqual(self.reader.data['type_transaction'][2], 'ACHAT')
        self.assertEqual(self.reader.data['type_transaction'][3], 'CREDIT')
        self.assertEqual(self.reader.data['type_transaction'][4], 'PRELEVEMENT')
        self.assertEqual(self.reader.data['type_transaction'][5], None)

        self.assertEqual(self.reader.data['description'][0], '')
        self.assertEqual(self.reader.data['description'][1], '')
        self.assertEqual(self.reader.data['description'][2], '')
        self.assertEqual(self.reader.data['description'][3], '')
        self.assertEqual(self.reader.data['description'][4], '')
        self.assertEqual(self.reader.data['description'][5], 'NO KEY')

    def test_format_date(self):
        self.reader.data = pd.DataFrame({'date_bank': ['\n12/02/2005',
                                                       '13/03/2006']})

        self.reader.format_date()

        self.assertEqual(self.reader.data['date_bank'][0].day, 12)
        self.assertEqual(self.reader.data['date_bank'][0].month, 2)
        self.assertEqual(self.reader.data['date_bank'][0].year, 2005)
        self.assertEqual(self.reader.data['date_bank'][1].day, 13)
        self.assertEqual(self.reader.data['date_bank'][1].month, 3)
        self.assertEqual(self.reader.data['date_bank'][1].year, 2006)

    def test_convert_amount_in_float(self):

        self.reader.data = pd.DataFrame({'amount_e': ['15,5', '-5,8'],
                                         'amount_f': ['-89,37', '60,1']})

        self.reader.convert_amount_in_float()

        self.assertEqual(self.reader.data['amount_e'][0], 15.5)
        self.assertEqual(self.reader.data['amount_e'][1], -5.8)
        self.assertEqual(self.reader.data['amount_f'][0], -89.37)
        self.assertEqual(self.reader.data['amount_f'][1], 60.1)

    def test_read_raw_data(self):

        self.assertEqual(self.reader.data.shape, (3, 6))
        self.assertEqual(self.reader.data['date_bank'][0].day, 7)
        self.assertEqual(self.reader.data['date_bank'][0].month, 1)
        self.assertEqual(self.reader.data['date_bank'][0].year, 2022)
        self.assertEqual(self.reader.data['description'][1], 'FOOD')
        self.assertEqual(self.reader.data['amount_e'][1], -5.)
        self.assertEqual(self.reader.data['amount_f'][1], -32.8)
        self.assertEqual(self.reader.data['type_transaction'][2], 'PRELEVEMENT')
        self.assertEqual(self.reader.data['date_transaction'][2].day, 1)
        self.assertEqual(self.reader.data['date_transaction'][2].month, 1)
        self.assertEqual(self.reader.data['date_transaction'][2].year, 2000)

    def test_read_header(self):

        self.assertEqual(self.reader.account_id, '007')
        self.assertEqual(self.reader.date.day, 8)
        self.assertEqual(self.reader.date.month, 1)
        self.assertEqual(self.reader.date.year, 2022)
        self.assertEqual(self.reader.balance, 300.48)


class TestFunctions(unittest.TestCase):
    def test_create_list_transactions_from_file(self):

        class FakeFileReader:
            def __init__(self):
                self.account_id = 10
                self.data = pd.DataFrame({'date_bank': [1, 2],
                                          'date_transaction': [3, 4],
                                          'description': ['des1', 'des2'],
                                          'amount_e': [98.1, -0.2],
                                          'type_transaction': ['1', '2']})
        fake_file_reader = FakeFileReader()

        with patch('source.data_reader.bank_file_reader.BankTSVReader') as service_mock:
            service_mock.return_value = fake_file_reader
            list_trans = create_list_transactions_from_file('')

        self.assertEqual(len(list_trans), 2)
        for i in range(len(list_trans)):
            self.assertEqual(list_trans[i].account_id, fake_file_reader.account_id)
            self.assertEqual(list_trans[i].date_bank, fake_file_reader.data.loc[i, 'date_bank'])
            self.assertEqual(list_trans[i].date, fake_file_reader.data.loc[i, 'date_transaction'])
            self.assertEqual(list_trans[i].description, fake_file_reader.data.loc[i, 'description'])
            self.assertEqual(list_trans[i].amount, fake_file_reader.data.loc[i, 'amount_e'])
            self.assertEqual(list_trans[i].type, fake_file_reader.data.loc[i, 'type_transaction'])
            self.assertEqual(list_trans[i].category, None)


if __name__ == '__main__':
    unittest.main()
