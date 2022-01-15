import unittest

from db_connection.db_access import MongoDBConnection
from data_reader.bank_file_reader import create_list_transactions_from_file
from transactions import dict_to_transaction
from data_ingestion.ingest import *


class TestTransactionIngest(unittest.TestCase):
    def setUp(self) -> None:

        # create list of transactions
        list_trans = create_list_transactions_from_file('test/fake_data.tsv')

        # Create connection
        my_connection = MongoDBConnection('db_ut')

        # Instantiate the ingestion class
        self.transInges = TransactionIngest(my_connection, list_trans)

    def tearDown(self) -> None:
        # Remove all transactions in the collection
        result = self.transInges.connection.collection.remove()

    def test_ingest_one_transaction(self):

        # Ingestion of one transaction
        self.transInges.ingest_one_transaction(self.transInges.transactions_list[0])

        # get the transaction in the mongodb
        db_trans = self.transInges.connection.collection.find_one()
        # Convert it in Transaction
        db_trans = dict_to_transaction(db_trans)

        # check equality
        self.assertEqual(self.transInges.transactions_list[0], db_trans)


if __name__ == '__main__':
    unittest.main()
