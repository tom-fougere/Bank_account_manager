import unittest

from apps.tables import *


class TestFormatDataframe(unittest.TestCase):
    def test_filter_columns(self):

        df = pd.DataFrame({key: [1] for key in InfoDisplay.ALL})

        # Import
        new_df = filter_columns(df, InfoDisplay.IMPORT)
        self.assertEqual(len(new_df.keys()), len(InfoDisplay.IMPORT))
        for key in InfoDisplay.IMPORT:
            self.assertEqual(key in new_df.keys(), True)

        # Search
        new_df = filter_columns(df, InfoDisplay.SEARCH)
        self.assertEqual(len(new_df.keys()), len(InfoDisplay.SEARCH))
        for key in InfoDisplay.SEARCH:
            self.assertEqual(key in new_df.keys(), True)

    def test_rename(self):

        df = pd.DataFrame({key: [1] for key in InfoDisplay.ALL})

        rename_columns(df)

        for key, value in INFO_RENAMING.items():
            self.assertEqual(value in df.keys(), True)

    def test_format_dataframe(self):

        df = pd.DataFrame({key: [1] for key in InfoDisplay.ALL})
        df[InfoName.ID] = 'id'

        new_df = format_dataframe(df, InfoDisplay.SEARCH)

        # check number of columns
        self.assertEqual(len(new_df.keys()), len(InfoDisplay.SEARCH))

        # check keys
        for key in InfoDisplay.SEARCH:
            self.assertEqual(INFO_RENAMING[key] in new_df.keys(), True)


