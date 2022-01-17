import unittest

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest
from source.data_reader.bank_file_reader import create_list_transactions_from_file
from source.transactions import dict_to_transaction


class TestTransactionIngest(unittest.TestCase):
    def setUp(self) -> None:

        # create list of transactions
        self.list_trans = create_list_transactions_from_file('test/fake_data.tsv')

        # Create connection
        my_connection = MongoDBConnection('db_ut')

        # Instantiate the ingestion class
        self.transInges = TransactionIngest(my_connection, self.list_trans)

    def tearDown(self) -> None:
        # Remove all transactions in the collection
        result = self.transInges.connection.collection.remove()

    def test_ingest_one_new_transaction(self):

        # Ingestion of one transaction
        self.transInges.ingest_one_transaction(self.transInges.transactions_list[0])

        # get the transaction in the mongodb
        db_trans = self.transInges.connection.collection.find_one()
        # Convert it in Transaction
        db_trans = dict_to_transaction(db_trans)

        # check equality
        self.assertEqual(self.transInges.transactions_list[0], db_trans)

    def test_ingest_one_same_transaction(self):

        # Ingestion of one transaction
        self.transInges.ingest_one_transaction(self.list_trans[0])

        with self.assertRaises(Exception) as context:
            self.transInges.ingest_one_transaction(self.list_trans[0])

    def test_ingest(self):

        # Ingestion of transactions
        self.transInges.ingest()

        # get the transaction in the mongodb
        db_all_trans = self.transInges.connection.collection.find()

        self.assertEqual(len(list(db_all_trans)), len(self.list_trans))

        idx = 0
        for db_trans in list(db_all_trans):

            # Convert it in Transaction
            db_trans = dict_to_transaction(db_trans)
            # check equality
            self.assertEqual(self.list_trans[idx], db_trans)

            idx += 1


if __name__ == '__main__':
    unittest.main()
