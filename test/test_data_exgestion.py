import datetime
import unittest
from source.data_ingestion.ingest import TransactionDB
from source.data_reader.bank_file_reader import BankTSVReader
from source.data_ingestion.exgest import TransactionExgest
from source.transactions.metadata import MetadataDB
from apps.current_stats.cs_pipelines import p_salary_vs_other

ACCOUNT_ID = '008'
CONNECTION_METADATA = 'db_metadata_ut'
CONNECTION_TRANSACTION = 'db_ut'
DATE_NOW = datetime.datetime.now()
data_reader = BankTSVReader('test/fake_data.tsv')
df_transactions = data_reader.get_dataframe()


class TestTransactionExgest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:

        # Init databases with data
        metadata = MetadataDB(
            name_connection=CONNECTION_METADATA,
            account_id=ACCOUNT_ID,
        )
        metadata.init_db(
            balance_in_bank=1.1,
            balance_in_db=2.2,
            balance_bias=3.3,
            date_balance_in_bank=DATE_NOW,
            date_last_import=DATE_NOW,
        )

        # Ingest
        cls.db = TransactionDB(
            name_connection_transaction=CONNECTION_TRANSACTION,
            name_connection_metadata=CONNECTION_METADATA,
            account_id=ACCOUNT_ID
        )

        cls.db.ingest(df_transactions,
                      bank_info=
                      {
                          'account_id': ACCOUNT_ID,
                          'balance': None,
                          'date': datetime.datetime.now()
                      })

    @classmethod
    def tearDownClass(cls) -> None:
        # Remove all transactions in the collection
        cls.db.connection_transaction.collection.remove({"account_id": ACCOUNT_ID})
        cls.db.metadata.connection.collection.remove({"account_id": ACCOUNT_ID})

    def test_exgest_all(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID})
        results = data_extractor.exgest_all()

        self.assertEqual(len(results), 3)

    def test_exgest_empty_pipeline(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 3)

    def test_exgest_account_id(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 3)

    def test_exgest_type_transaction(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID,
                                            "type_transaction": "VIREMENT"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 1)

    def test_exgest_date(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID,
                                            "date": [datetime.datetime(2022, 1, 7),
                                                     datetime.datetime(2022, 1, 7)]})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 2)

    def test_exgest_amount(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID,
                                            "amount": [-10, 10]})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 2)

    def test_exgest_description(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID,
                                            "description": "co"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 1)
        self.assertEqual(results['description'].values, 'TELECOM')

    def test_exgest_empty_description(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_search_criteria({"account_id": ACCOUNT_ID,
                                            "description": "tom"})
        results = data_extractor.exgest()

        self.assertEqual(len(results), 0)

    def test_exgest_set_empty_pipeline(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_pipeline([])
        results = data_extractor.exgest()

        self.assertEqual(len(results), 0)

    def test_exgest_set_pipeline(self):
        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        data_extractor.set_pipeline(p_salary_vs_other)
        results = data_extractor.exgest()

        self.assertEqual(len(results), 1)

    def test_get_distinct_year(self):

        data_extractor = TransactionExgest(CONNECTION_TRANSACTION)
        list_years = data_extractor.get_distinct_years()

        self.assertEqual(len(list_years), 1)
        self.assertEqual(list_years[0], 2022)


if __name__ == '__main__':
    unittest.main()
