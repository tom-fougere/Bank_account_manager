import unittest
import pandas as pd
from utils.mixed_utils import expand_columns_of_dataframe


class TestDataFrame(unittest.TestCase):
    def test_expand_columns_of_dataframe(self):
        df = pd.DataFrame({'a1': [0, 1, 2],
                           'a2': [
                               {
                                   'b1': 10,
                                   'b2': '11'
                               },
                               {
                                   'b1': 20,
                                   'b2': '21'
                               },
                               {
                                   'b1': 30,
                                   'b2': '31'
                               }]
                           })

        df_new = expand_columns_of_dataframe(df, 'a2')

        self.assertEqual(df_new.shape, (3, 3))
        for key in ['a1', 'b1', 'b2']:
            self.assertEqual(key in df_new, True)
