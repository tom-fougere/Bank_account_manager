import plotly.graph_objects as go

from source.transactions.transaction_operations import check_duplicates_in_df
from source.data_reader.bank_file_reader import BankTSVReader
from source.transactions.exgest import TransactionExgest
from source.transactions.account_manager_db import AccountManagerDB


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
    data_extractor = TransactionExgest(db_connection)
    data_extractor.set_search_criteria({"account_id": account_id,
                                        "date_transaction": [min_date, max_date]})
    db = data_extractor.exgest()

    # check duplicates
    check_duplicates_in_df(df, db)

    # Convert boolean to string (for dash datatable)
    df['duplicate'] = df['duplicate'].astype('str')

    return df, data_reader.get_account_info()


def fig_indicators_new_transactions(connection_transaction, connection_metadata, df, account_info):

    if df is not None:
        nb_transactions_in_file = len(df)
        df_new_transactions = df[df['duplicate'] == 'False']

        db = AccountManagerDB(
            name_connection_metadata=connection_metadata,
            name_connection_transaction=connection_transaction,
            account_id=account_info['account_id'],
        )
        data_comparison = db.check_with_new_transactions(
            df_transactions=df_new_transactions,
            bank_info=account_info,
        )

        figure = go.Figure()
        figure.add_trace(go.Indicator(
            mode="number+delta",
            value=nb_transactions_in_file,
            title={"text": "Nombre de transactions<br>" +
                   "<span style='font-size:0.8em;color:gray'>(dont nouvelles)</span>"},
            delta={'reference': nb_transactions_in_file - len(df_new_transactions),
                   'relative': False,
                   },
            domain={'row': 0, 'column': 0}))
        figure.add_trace(go.Indicator(
            mode="number",
            value=data_comparison['difference'],
            number={'suffix': "€", "valueformat": '.2f'},
            title={"text": "Différence de revenu<br>" +
                   "<span style='font-size:0.8em;color:gray'>(avec la somme à la banque)</span>"},
            domain={'row': 0, 'column': 1}))
        figure.update_layout(
            grid={'rows': 1, 'columns': 2, 'pattern': "independent"},
            height=250  # px
        )

    else:
        figure = {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
            }
        }

    return figure
