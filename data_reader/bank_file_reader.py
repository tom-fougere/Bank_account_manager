import datetime

import pandas as pd
from utils.time_operations import detect_date_in_string, str_to_datetime
from utils.text_operations import find_substring_with_dict, remove_substring_with_list
from transactions import Transaction

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

        col_names = ['date_bank', 'description', 'amount_e', 'amount_f']
        self.data = pd.read_csv(self.file_path,
                                delimiter='\t', lineterminator='\r',
                                skiprows=self.header_lines + 1,
                                encoding="ISO-8859-1",
                                names=col_names,
                                header=None)
        self.data = self.data[:-1]

        self.format_date()

        # Remove amount in francs
        self.data.drop(['amount_f'], axis=1)

        # Manage type of transaction
        self.manage_transaction_type()

        # Manage transaction date
        self.manage_transaction_date()

        # Convert amount in float
        self.convert_amount_in_float()

        # Clean transaction
        self.clean_description()

    def format_date(self):

        # Remove '\n' character at the beginning of the string
        self.data['date_bank'] = self.data['date_bank'].apply(lambda x: x.replace('\n', ''))

        # Convert string to datetime
        self.data['date_bank'] = pd.to_datetime(self.data['date_bank'], format='%d/%m/%Y')

    def manage_transaction_type(self):

        # Find type of transaction
        self.data['type_transaction'] = self.data['description'].apply(
            lambda x: find_substring_with_dict(x, map_transaction_type))

        # Remove type of transaction from the description
        self.data['description'] = self.data['description'].apply(
            lambda x: remove_substring_with_list(x, list(map_transaction_type.keys())))

    def manage_transaction_date(self):

        # Search date of transaction in description and store it in a new column
        self.data['date_transaction'] = self.data['description'].apply(lambda x: detect_date_in_string(x))

        # Remove date from the description
        self.data['description'] = self.data.apply(lambda x: x.description.replace(x.date_transaction, ''), axis=1)

        # Convert transaction date from string to datetime
        self.data['date_transaction'] = pd.to_datetime(self.data['date_transaction'], format='%d.%m.%y')

    def convert_amount_in_float(self):
        self.data['amount_f'] = self.data['amount_f'].str.replace(',', '.').astype(float)
        self.data['amount_e'] = self.data['amount_e'].str.replace(',', '.').astype(float)

    def clean_description(self):

        # Remove continuous spaces
        self.data['description'] = self.data['description'].apply(lambda x: " ".join(x.split()))

        # Remove carte id
        self.data['description'] = self.data['description'].apply(lambda x: x.replace('CARTE NUMERO 569', ''))

        # Remove continuous spaces
        self.data['description'] = self.data['description'].apply(lambda x: " ".join(x.split()))


def create_list_transactions_from_file(file):
    # Read file
    file_reader = BankTSVReader(file_path=file)

    # Loop over the dataframe to build a list of Transactions
    list_transactions = []
    for idx, row in pd.DataFrame.iterrows(file_reader.data):
        trans = Transaction(account_id=file_reader.account_id,
                            date_bank=row['date_bank'],
                            date=row['date_transaction'],
                            description=row['description'],
                            amount=row['amount_e'],
                            type=row['type_transaction'])
        list_transactions.append(trans)

    return list_transactions




