import unittest

from apps.tables import *


class TestFormatDataframe(unittest.TestCase):
    def test_filter_columns(self):

        df = pd.DataFrame({key: [1] for key in ColumnsDisplay.ALL})

        # Import
        new_df = filter_columns(df, ColumnsDisplay.IMPORT)
        self.assertEqual(len(new_df.keys()), len(ColumnsDisplay.IMPORT))
        for key in ColumnsDisplay.IMPORT:
            self.assertEqual(key in new_df.keys(), True)

        # Search
        new_df = filter_columns(df, ColumnsDisplay.SEARCH)
        self.assertEqual(len(new_df.keys()), len(ColumnsDisplay.SEARCH))
        for key in ColumnsDisplay.SEARCH:
            self.assertEqual(key in new_df.keys(), True)

    def test_rename(self):

        df = pd.DataFrame({key: [1] for key in ColumnsDisplay.ALL})

        rename_columns(df)

        for key, value in COLUMNS_RENAMING.items():
            self.assertEqual(value in df.keys(), True)

    def test_format_dataframe(self):

        df = pd.DataFrame({key: [1] for key in ColumnsDisplay.ALL})
        df[ColumnsName.ID] = 'id'

        new_df = format_dataframe(df, ColumnsDisplay.SEARCH)

        # check number of columns
        self.assertEqual(len(new_df.keys()), len(ColumnsDisplay.SEARCH))

        # check keys
        for key in ColumnsDisplay.SEARCH:
            self.assertEqual(COLUMNS_RENAMING[key] in new_df.keys(), True)


