import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme

from source.transactions.transaction_operations import check_duplicates_in_df
from source.data_reader.bank_file_reader import BankTSVReader
from source.data_ingestion.exgest import TransactionExgest
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.metadata import MetadataDB


style_cell_conditional = (
    [
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['Libelé', 'Type']
    ] +
    [
        {
            'if': {'column_id': c},
            'textAlign': 'center'
        } for c in ['Date', 'Date (banque)']
    ]
)

style_data_conditional = (
    [
        {
            'if': {
                'filter_query': '{Duplicata} eq "True"'
            },
            'backgroundColor': '#DAE8FE'
        },
        {
            'if': {
               'column_id': 'Montant (€)',
               'filter_query': '{Montant (€)} > 0'
            },
            'backgroundColor': '#B5EEB6'
        }
    ]
)


def create_datatable(df):

    df_display = df.copy()
    df_display = df_display[['date_transaction_str', 'amount', 'description', 'type_transaction', 'date_str', 'duplicate']]
    df_display.rename(columns={'date_str': 'Date (banque)',
                               'amount': 'Montant (€)',
                               'description': 'Libelé',
                               'type_transaction': 'Type',
                               'date_transaction_str': 'Date',
                               'duplicate': 'Duplicata'}, inplace=True)

    columns = [{"name": i, "id": i, } for i in df_display.columns]
    columns[1]['type'] = 'numeric'
    columns[1]['format'] = Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('€')

    dt_transactions = dt.DataTable(id='table_content',
                                   data=df_display.to_dict('records'),
                                   columns=columns,
                                   column_selectable="single",
                                   selected_columns=[],
                                   selected_rows=[],
                                   style_data_conditional=style_data_conditional,
                                   style_cell_conditional=style_cell_conditional,
                                   style_header={
                                       'backgroundColor': 'rgb(210, 210, 210)',
                                       'color': 'black',
                                       'fontWeight': 'bold'
                                   })
    return dt_transactions


def read_and_format_data(full_filename, db_connection):
    # Read data
    data_reader = BankTSVReader(full_filename)
    df = data_reader.get_dataframe()

    # Check account ID is unique
    current_account_id = df['account_id'].unique()
    assert (len(current_account_id), 1)

    # Get the min/max date from the new df
    min_date = min(df['date_transaction_dt'])
    max_date = max(df['date_transaction_dt'])

    # Extract from the database the same dates
    my_connection = MongoDBConnection(db_connection)
    data_extractor = TransactionExgest(my_connection, {"account_id": current_account_id[0],
                                                       "date": [min_date, max_date]})
    db = data_extractor.exgest()

    # check duplicates
    check_duplicates_in_df(df, db)

    # Convert boolean to string (for dash datatable)
    df['duplicate'] = df['duplicate'].astype('str')

    return df, data_reader.get_account_info()


def update_db_account(account_info, df, db_connection):
    account_id = df['account_id'].unique()
    if len(account_id) > 1:
        ValueError('here')
    else:
        account_id = account_id[0]

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    metadata_db.update_date_balance_in_bank(account_id=account_id, date=account_info['date'])
    metadata_db.update_balance_in_bank(account_id=account_id, balance=account_info['balance'])

    # Update balance add the sum to the previous balance
    previous_balance = metadata_db.get_balance_in_db(account_id=account_id)
    new_balance = previous_balance + round(df['amount'].sum(), 2)
    metadata_db.update_balance_in_db(account_id=account_id, balance=new_balance)

    # Update date of import using the newest date
    newest_date = max(df['date_bank_dt'])
    metadata_db.update_date_last_import(account_id=account_id, date=max(df['']))


