import unittest

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest
from source.data_reader.bank_file_reader import BankTSVReader
from source.transactions import dict_to_transaction


class TestTransactionIngest(unittest.TestCase):
    def setUp(self) -> None:

        # create list of transactions
        data_reader = BankTSVReader('test/fake_data.tsv')
        self.df_transactions = data_reader.get_dataframe()

        # Create connection
        my_connection = MongoDBConnection('db_ut')

        # Instantiate the ingestion class
        self.transInges = TransactionIngest(my_connection, self.df_transactions)

    def tearDown(self) -> None:
        # Remove all transactions in the collection
        result = self.transInges.connection.collection.remove()

    def test_ingest_one_new_transaction(self):

        # Ingestion of one transaction
        self.transInges.ingest_one_transaction(self.df_transactions.iloc[0])

        # get the transaction in the mongodb
        db_trans = self.transInges.connection.collection.find_one()
        # Remove id field for the comparison
        db_trans.pop('_id', None)

        # check equality
        self.assertEqual(self.df_transactions.iloc[0].to_dict(), db_trans)

    def test_ingest_one_same_transaction(self):

        # Ingestion of one transaction
        self.transInges.ingest_one_transaction(self.df_transactions.iloc[0])

        with self.assertRaises(Exception) as context:
            self.transInges.ingest_one_transaction(self.df_transactions.iloc[0])

    def test_ingest(self):

        # Ingestion of transactions
        self.transInges.ingest()

        # get the transaction in the mongodb
        db_all_trans = self.transInges.connection.collection.find()

        self.assertEqual(len(list(db_all_trans)), len(self.df_transactions))

        idx = 0
        db_all_trans.rewind()  # Reset the index of the cursor
        for db_trans in db_all_trans:

            # Remove '_id' for comparison
            db_trans.pop('_id', None)

            # check equality
            self.assertEqual(self.df_transactions.iloc[idx].to_dict(), db_trans)

            idx += 1


if __name__ == '__main__':
    unittest.main()
