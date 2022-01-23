import re
from datetime import datetime
import numpy as np


def get_date_in_string(text, regex_date=r'\d{2}\.\d{2}\.\d{2}'):

    date_str = re.search(regex_date, text)
    if date_str is not None:
        date_str = date_str.group()
    else:
        date_str = np.nan
    return date_str


def remove_date_in_string(text, regex_date=r'\d{2}\.\d{2}\.\d{2}'):

    new_text = text
    date_str = re.search(regex_date, text)
    if date_str is not None:
        new_text = date_str.group()  # get the date (string format)
        new_text = text.replace(new_text, '')

    return new_text


def str_to_datetime(text, date_format='%d.%m.%Y'):
    return datetime.strptime(text, date_format)
