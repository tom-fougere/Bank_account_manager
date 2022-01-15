import unittest
import numpy as np

from transactions import *


class TestTransactions(unittest.TestCase):
    # def setUp(self) -> None:

    def test_init(self):

        # Create transaction
        trans = Transaction(account_id=0,
                            date_bank=1,
                            date=2,
                            description=3,
                            amount=4,
                            type=5,
                            category=None)

        self.assertEqual(trans.account_id, 0)
        self.assertEqual(trans.date_bank, 1)
        self.assertEqual(trans.date, 2)
        self.assertEqual(trans.description, 3)
        self.assertEqual(trans.amount, 4)
        self.assertEqual(trans.type, 5)
        self.assertEqual(trans.category, None)

    def test_eq(self):

        trans1 = Transaction(account_id=0,
                             date_bank=1,
                             date=2,
                             description=3,
                             amount=4,
                             type=5,
                             category=None)

        trans2 = Transaction(account_id=0,
                             date_bank=1,
                             date=2,
                             description=3,
                             amount=4,
                             type=5,
                             category=None)

        self.assertEqual(trans1, trans2)

    def test_neq(self):

        trans1 = Transaction(account_id=0,
                             date_bank=1,
                             date=2,
                             description=3,
                             amount=4,
                             type=5,
                             category=6)

        nb_attributes = 7
        for i in range(nb_attributes):
            current_array_errors = np.zeros((nb_attributes, 1))
            current_array_errors[i] = 1

            trans2 = Transaction(account_id=0+current_array_errors[0],
                                 date_bank=1+current_array_errors[1],
                                 date=2+current_array_errors[2],
                                 description=3+current_array_errors[3],
                                 amount=4+current_array_errors[4],
                                 type=5+current_array_errors[5],
                                 category=6++current_array_errors[6])

            self.assertNotEqual(trans1, trans2)
