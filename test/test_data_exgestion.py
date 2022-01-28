import unittest
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest
from source.data_reader.bank_file_reader import BankTSVReader
from source.data_ingestion.exgest import TransactionExgest


class TestTransactionExgest(unittest.TestCase):
    def setUp(self) -> None:

        # Ingest
        data_reader = BankTSVReader('test/fake_data.tsv')
        self.df_transactions = data_reader.get_dataframe()
        my_connection = MongoDBConnection('db_ut')
        self.transInges = TransactionIngest(my_connection, self.df_transactions)
        self.transInges.ingest()

        # Instantiate the ingestion class
        self.transExges = TransactionExgest(my_connection, {})

    def tearDown(self) -> None:
        # Remove all transactions in the collection
        result = self.transInges.connection.collection.remove()

    def test_exgest_all(self):
        results = self.transExges.exgest_all()
        self.assertEqual(len(results), 3)

    def test_exgest_empty_pipeline(self):
        results = self.transExges.exgest()
        self.assertEqual(results, None)


if __name__ == '__main__':
    unittest.main()
