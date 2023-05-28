import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
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


def modify_date_str_format(original_date_str, current_format, new_format):
    date_dt = datetime.strptime(original_date_str, current_format)

    return date_dt.strftime(new_format)


def convert_str_from_iso_format(datetime_str):
    datetime_iso_format = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    # With python 3.11, no need to replace the Z char (same for the line 31)

    return datetime_iso_format


def get_first_day_several_month_before(date, nb_months):
    return date.replace(day=1) + relativedelta(months=-nb_months)
