import re
from datetime import datetime


def detect_date_in_string(text):
    try:
        date_str = re.search(r'\d{2}\.\d{2}\.\d{2}', text).group()
    except Exception as e:
        date_str = '01.01.00'
    return date_str


def str_to_datetime(text, date_format='%d.%m.%Y'):
    return datetime.strptime(text, date_format)
