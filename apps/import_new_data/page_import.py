import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import Input, Output, State, callback_context
import dash_table as dt
from app import app
import pandas as pd
import json

from utils.text_operations import get_project_root
from utils.time_operations import convert_str_from_iso_format
from source.transactions.account_manager_db import AccountManagerDB
from apps.import_new_data.ind_operations import read_and_format_data, fig_indicators_new_transactions
from apps.tables import format_dataframe, df_to_datatable, InfoDisplay, sort_datatable
from source.definitions import DB_CONN_TRANSACTION, DB_CONN_ACCOUNT, DATA_FOLDER


layout = html.Div([

    html.H1('Importation de données',
            id='title_import_data_page',
            style={'textAlign': 'center'}),

    dcc.Upload(
        id='drag_upload_file',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a File')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        }),
    dbc.Button("Importer",
               outline=True,
               color="secondary",
               className="btn_import_database",
               id="btn_import_database",
               disabled=True,
               n_clicks=0,
               style={'width': '100%',
                      'margin-top': 10}
               ),
    html.Div(id="message_import"),
    dcc.Graph(id='fig_indicators_new_transactions',
              figure=fig_indicators_new_transactions(None, None, None, None)),
    html.Div(id="table_new_import"),
    dcc.Store(id='store_transactions_df'),
    dcc.Store(id='store_transactions_account_info'),
])


@app.callback(
    Output("store_transactions_df", 'data'),
    Output("store_transactions_account_info", 'data'),
    Input('drag_upload_file', 'contents'),
    State('drag_upload_file', 'filename'))
def upload_file(list_of_contents, filename):

    df_import = None
    account_info = None

    if list_of_contents is not None:
        # Read data
        df, account_info = read_and_format_data('/'.join([get_project_root(), DATA_FOLDER, filename]),
                                                db_connection=DB_CONN_TRANSACTION)

        # Format for Store component
        df_import = df.to_json(date_format='iso')

    return df_import, account_info


@app.callback(
    Output("fig_indicators_new_transactions", 'figure'),
    Output("table_new_import", 'children'),
    Output('btn_import_database', 'disabled'),
    Input('store_transactions_df', 'data'),
    Input('store_transactions_account_info', 'data'),
    State('btn_import_database', 'disabled'))
def display_transactions(jsonified_df_transactions, account_info, btn_disabled):

    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    # default outputs
    fig = fig_indicators_new_transactions(None, None, None, None)
    dt_transactions = dt.DataTable(id='cell_new_import')
    btn_import_state = btn_disabled

    # Set sub-category
    if (triggered_input == 'store_transactions_df') or (triggered_input == 'store_transactions_account_info'):
        if (jsonified_df_transactions is not None) and (account_info is not None):
            df = rebuild_df_from_json(jsonified_df_transactions)

            # Convert to dataTable
            df_display = format_dataframe(df, InfoDisplay.IMPORT)
            dt_transactions = df_to_datatable(
                df_display,
                table_id='cell_new_import',
                checkbox='multi',
                selected_rows=[int(i) for i, row in df_display.iterrows() if row['Duplicata'] == "Non"],
            )

            # Enable button
            btn_import_state = False

            # Create indicators
            fig = fig_indicators_new_transactions(
                connection_transaction=DB_CONN_TRANSACTION,
                connection_metadata=DB_CONN_ACCOUNT,
                df=df,
                account_info=account_info,
            )

    return fig, dt_transactions, btn_import_state


@app.callback(
    Output('message_import', 'children'),
    Input('btn_import_database', 'n_clicks'),
    State('store_transactions_df', 'data'),
    State('store_transactions_account_info', 'data'),
    State('cell_new_import', 'selected_rows'),
    prevent_initial_call=True)
def import_transactions_in_database(n_clicks, jsonified_df_transactions, account_info, selected_rows):

    message = None

    if n_clicks > 0:

        if (jsonified_df_transactions is not None) and (account_info is not None) and len(selected_rows) > 0:

            # Get data as dataframe
            df = rebuild_df_from_json(jsonified_df_transactions)
            account_info['date'] = convert_str_from_iso_format(account_info['date'])

            # Extract only required rows
            df_to_import = df.iloc[selected_rows]
            df_to_import.drop(columns=['duplicate'], inplace=True)

            # Database ingestion
            db = AccountManagerDB(
                name_connection_transaction=DB_CONN_TRANSACTION,
                name_connection_metadata=DB_CONN_ACCOUNT,
                account_id=account_info['account_id'])
            db.ingest(df_to_import, bank_info=account_info)

            message = "Transactions importées !"

    return message


@app.callback(
    Output('store_transaction_disabled', 'data'),
    [Input('cell_new_import', 'active_cell'),
     Input('cell_new_import', 'sort_by')],
    State('store_transactions_df', 'data'))
def store_disabled_transaction(cell_new_import, sort_by, jsonified_df_transactions):

    data = None

    if cell_new_import is not None:

        if jsonified_df_transactions is not None:

            # Get data as dataframe
            df = rebuild_df_from_json(jsonified_df_transactions)

            # Sorting
            if sort_by is not None and len(sort_by):
                sort_datatable(df, sort_by)

            selected_df = df.iloc[cell_new_import['row']]
            data = selected_df.to_json(date_format='iso')

    return data


def rebuild_df_from_json(json_data):
    parsed = json.loads(json_data)
    df = pd.DataFrame(parsed)

    df['date_dt'] = df.apply(lambda x: convert_str_from_iso_format(x.date_dt), axis=1)
    df['date_transaction_dt'] = df.apply(lambda x: convert_str_from_iso_format(x.date_transaction_dt), axis=1)

    return df
