import unittest
from datetime import datetime, timezone
from utils.time_operations import *


class TestTime(unittest.TestCase):
    def test_get_first_day_several_month_before(self):

        delay = 2

        current_time = datetime(2022, 4, 29)
        expected_time = current_time.replace(month=(current_time.month-delay), day=1)
        new_time = get_first_day_several_month_before(current_time, delay)

        self.assertEqual(expected_time, new_time)

    def test_convert_str_from_iso_format(self):
        date = convert_str_from_iso_format('2023-04-01T05:00:30.001000Z')
        self.assertEqual(datetime(2023, 4, 1, 5, 0, 30, 1000, timezone.utc), date)

    def test_get_date_in_string(self):

        date = get_date_in_string(text='Date inside text 12.05.01')  # r'\d{2}\.\d{2}\.\d{2}'
        self.assertEqual(date, '12.05.01')

        date = get_date_in_string(text='Date inside text 12/05/01', regex_date='\d{2}/\d{2}/\d{2}')
        self.assertEqual(date, '12/05/01')

    def test_remove_date_in_string(self):

        new_text = remove_date_in_string(text='Date inside text 12.05.01!')  # r'\d{2}\.\d{2}\.\d{2}'
        self.assertEqual(new_text, 'Date inside text !')

        new_text = remove_date_in_string(text='Date inside text 12/05/01!', regex_date='\d{2}/\d{2}/\d{2}')
        self.assertEqual(new_text, 'Date inside text !')

        return new_text

    def test_str_to_datetime(self):
        date = str_to_datetime('15.12.2024')  # '%d.%m.%Y'
        self.assertEqual(date, datetime(2024, 12, 15))
        date = str_to_datetime('12/15/24', date_format='%m/%d/%y')
        self.assertEqual(date, datetime(2024, 12, 15))

    def test_modify_date_str_format(self):

        date = modify_date_str_format(
            original_date_str='15.12.2024',
            current_format='%d.%m.%Y',
            new_format='%Y/%d/%m')
        self.assertEqual(date, '2024/15/12')
