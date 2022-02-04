import datetime
import unittest
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest
from source.data_reader.bank_file_reader import BankTSVReader
from source.data_ingestion.exgest import TransactionExgest

data_reader = BankTSVReader('test/fake_data.tsv')
df_transactions = data_reader.get_dataframe()
db_connection = MongoDBConnection('db_ut')


class TestTransactionExgest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Ingest
        cls.transInges = TransactionIngest(db_connection, df_transactions)
        cls.transInges.ingest()

    @classmethod
    def tearDownClass(cls) -> None:
        # Remove all transactions in the collection
        result = cls.transInges.connection.collection.remove({"account_id": "007"})

    def test_exgest_all(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007"})
        results = data_extractor.exgest_all()

        self.assertEqual(len(results), 6)

    def test_exgest_empty_pipeline(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 3)

    def test_exgest_account_id(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 3)

    def test_exgest_type_transaction(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007",
                                                           "type_transaction": "VIREMENT"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 1)

    def test_exgest_date(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007",
                                                           "date": [datetime.datetime(2022, 1, 7),
                                                                    datetime.datetime(2022, 1, 7)]})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 2)

    def test_exgest_amount(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007",
                                                           "amount": [-10, 10]})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 2)

    def test_exgest_description(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007",
                                                           "description": "co"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 1)
        self.assertEqual(results['description'].values, 'TELECOM')

    def test_exgest_empty_description(self):
        data_extractor = TransactionExgest(db_connection, {"account_id": "007",
                                                           "description": "tom"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()