import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme

from source.transactions.transaction_operations import check_duplicates_in_df, format_dataframe_to_datatable
from source.data_reader.bank_file_reader import BankTSVReader
from source.data_ingestion.exgest import TransactionExgest
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionDB

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
    df_display, columns = format_dataframe_to_datatable(df, show_new_data=True, show_category=False)

    dt_transactions = dt.DataTable(id='cell_new_import',
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
    assert len(current_account_id) == 1
    account_id = current_account_id[0]

    # Get the min/max date from the new df
    min_date = min(df['date_transaction_dt'])
    max_date = max(df['date_transaction_dt'])

    # Extract from the database the same dates
    my_connection = MongoDBConnection(db_connection)
    data_extractor = TransactionExgest(my_connection)
    data_extractor.set_search_criteria({"account_id": account_id,
                                        "date_transaction": [min_date, max_date]})
    db = data_extractor.exgest()

    # check duplicates
    check_duplicates_in_df(df, db)

    # Convert boolean to string (for dash datatable)
    df['duplicate'] = df['duplicate'].astype('str')

    return df, data_reader.get_account_info()


def create_status_message(connection_transaction, connection_metadata, df, account_info):

    db = TransactionDB(
        name_connection_metadata=connection_metadata,
        name_connection_transaction=connection_transaction,
        account_id=account_info['account_id'],
    )
    diff_nb_transaction, diff_balance = db.check(
        df_transactions=df,
        bank_info=account_info,
    )

    status_msg = "STATUS - Nombre de transactions: {}, Balance: {:.2f}€".format(diff_nb_transaction, diff_balance)

    return status_msg
