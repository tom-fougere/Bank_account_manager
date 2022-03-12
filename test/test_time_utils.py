import unittest
from datetime import datetime
from utils.time_operations import get_first_day_several_month_before


class TestTime(unittest.TestCase):
    def test_get_first_day_several_month_before(self):

        delay = 2

        current_time = datetime(2022, 4, 29)
        expected_time = current_time.replace(month=(current_time.month-delay), day=1)
        new_time = get_first_day_several_month_before(current_time, delay)

        self.assertEqual(expected_time, new_time)
