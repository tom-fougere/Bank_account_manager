import datetime

import pandas as pd
from utils.time_operations import get_date_in_string, remove_date_in_string
from utils.text_operations import find_substring_with_dict, remove_substring_with_list

names_account_id = ['numero compte', 'numéro compte']
names_balance = ['solde (euros)']
names_date = ['date']
map_transaction_type = {'VIREMENT DE ': 'VIREMENT',
                        'VIREMENT POUR ': 'VIREMENT',
                        'ACHAT CB ': 'ACHAT',
                        'CREDIT ': 'CREDIT',
                        'PRELEVEMENT DE ': 'PRELEVEMENT'}


class BankTSVReader:
    def __init__(self, file_path):
        self.file_path = ''
        self.data = pd.DataFrame()
        self.header_lines = 0
        self.account_id = ''
        self.date = None
        self.balance = 0.

        self.file_path = file_path

        self.read_header()
        self.read_raw_data()

    def read_header(self):

        self.header_lines = 0

        # Open file
        file = open(self.file_path, 'r')

        while True:
            self.header_lines += 1

            # Get next line from file
            line = file.readline()
            self.parse_header_data(line)

            # Break when the line there is a line jump (between header and raw_data)
            if line == '\n':
                break

        # Close file
        file.close()

    def parse_header_data(self, line):

        # Remove carriage return
        line = line[:-1]

        line_split = line.split('\t')
        key = line_split[0].lower().strip()

        if key in names_account_id:
            self.account_id = line_split[1]
        elif key in names_date:
            self.date = datetime.datetime.strptime(line_split[1], '%d/%m/%Y')
        elif key in names_balance:
            self.balance = float(line_split[1].replace(',', '.'))

    def read_raw_data(self):

        col_names = ['date_str', 'description', 'amount', 'amount_f']
        self.data = pd.read_csv(self.file_path,
                                delimiter='\t', lineterminator='\r',
                                skiprows=self.header_lines + 1,
                                encoding="ISO-8859-1",
                                names=col_names,
                                header=None)
        self.data = self.data[:-1]

        # Format the date
        self.format_date()

        # Manage type of transaction
        self.manage_transaction_type()

        # Manage transaction date
        self.manage_transaction_date()

        # Convert amount in float
        self.convert_amount_in_float()

        # Clean transaction
        self.clean_description()

        # Format data
        self.format_dataframe()

    def format_date(self):

        # Remove '\n' character at the beginning of the string
        self.data['date_str'] = self.data['date_str'].apply(lambda x: x.replace('\n', ''))

        # Convert string to datetime
        self.data['date_dt'] = pd.to_datetime(self.data['date_str'], format='%d/%m/%Y')

    def manage_transaction_type(self):

        # Find type of transaction
        self.data['type_transaction'] = self.data['description'].apply(
            lambda x: find_substring_with_dict(x, map_transaction_type))

        # Remove type of transaction from the description
        self.data['description'] = self.data['description'].apply(
            lambda x: remove_substring_with_list(x, list(map_transaction_type.keys())))

    def manage_transaction_date(self):

        # Search date of transaction in description and store it in a new column
        self.data['date_transaction_str'] = self.data['description'].apply(lambda x: get_date_in_string(x))

        # Remove date from the description
        self.data['description'] = self.data['description'].apply(lambda x: remove_date_in_string(x))

        # Get when the date is available
        df = self.data.loc[self.data['date_transaction_str'].notna(), 'date_transaction_str']

        # Change the format of the date
        df = pd.to_datetime(df, format='%d.%m.%y')
        df = df.dt.strftime('%d/%m/%Y')

        # Insert new format to the original dataframe
        self.data.loc[self.data['date_transaction_str'].notna(), 'date_transaction_str'] = df

        # Replace unavailable transaction date by the bank date
        self.data.loc[self.data['date_transaction_str'].isna(), 'date_transaction_str'] =\
            self.data.loc[self.data['date_transaction_str'].isna(), 'date_str']

        # Convert string to datetime
        self.data['date_transaction_dt'] = pd.to_datetime(self.data['date_transaction_str'], format='%d/%m/%Y')

    def convert_amount_in_float(self):
        self.data['amount'] = self.data['amount'].str.replace(',', '.').astype(float)

    def clean_description(self):

        # Remove continuous spaces
        self.data['description'] = self.data['description'].apply(lambda x: " ".join(x.split()))

        # Remove carte id
        self.data['description'] = self.data['description'].apply(lambda x: x.replace('CARTE NUMERO 569', ''))

        # Remove continuous spaces
        self.data['description'] = self.data['description'].apply(lambda x: " ".join(x.split()))

    def format_dataframe(self):

        # Drop useless columns
        self.data.drop(['amount_f'], axis=1, inplace=True)

        # Add empty columns for other attributes
        self.data['account_id'] = self.account_id
        self.data['category'] = None
        self.data['sub_category'] = None
        self.data['occasion'] = None
        self.data['note'] = None
        self.data['check'] = False

    def get_dataframe(self):
        return self.data

    def get_account_info(self):

        info = {'account_id': self.account_id,
                'date': self.date,
                'balance': self.balance}

        return info
