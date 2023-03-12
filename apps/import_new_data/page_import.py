import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash import Input, Output, State
import dash_table as dt
from app import app

from utils.text_operations import get_project_root
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
])


@app.callback(
    Output("fig_indicators_new_transactions", 'figure'),
    Output("table_new_import", 'children'),
    Output('btn_import_database', 'disabled'),
    Input('drag_upload_file', 'contents'),
    State('drag_upload_file', 'filename'),
    State('btn_import_database', 'disabled'))
def upload_file(list_of_contents, filename, btn_disabled):

    # default outputs
    fig = fig_indicators_new_transactions(None, None, None, None)
    dt_transactions = dt.DataTable()
    btn_import_state = btn_disabled

    if list_of_contents is not None:
        # Read data
        df, account_info = read_and_format_data('/'.join([get_project_root(), DATA_FOLDER, filename]),
                                                db_connection=DB_CONN_TRANSACTION)

        # Convert to dataTable
        df_display = format_dataframe(df, InfoDisplay.IMPORT)
        dt_transactions = df_to_datatable(df_display, table_id='cell_new_import')

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
    State('drag_upload_file', 'filename'),
    State('btn_import_database', 'disabled'))
def import_transactions_in_database(n_clicks, filename, btn_disabled):
    if n_clicks > 0:

        full_path_filename = '/'.join([get_project_root(), DATA_FOLDER, filename])

        # Read data
        df, account_info = read_and_format_data(full_path_filename,
                                                db_connection=DB_CONN_TRANSACTION)
        df_new = df[df['duplicate'] == 'False']
        df_new.drop(columns=['duplicate'])

        # Database ingestion
        db = AccountManagerDB(
            name_connection_transaction=DB_CONN_TRANSACTION,
            name_connection_metadata=DB_CONN_ACCOUNT,
            account_id=account_info['account_id'])
        db.ingest(df_new, bank_info=account_info)

        upload_file(True, full_path_filename, btn_disabled)

        return "Transactions importées !"
    else:
        return None


@app.callback(
    Output('store_transaction_disabled', 'data'),
    [Input('cell_new_import', 'active_cell'),
     Input('cell_new_import', 'sort_by')],
    [State('drag_upload_file', 'filename')])
def store_disabled_transaction(cell_new_import, sort_by, filename):

    # Read data
    df, _ = read_and_format_data(full_filename='/'.join([get_project_root(), DATA_FOLDER, filename]),
                                 db_connection=DB_CONN_TRANSACTION)

    # Sorting
    if sort_by is not None and len(sort_by):
        sort_datatable(df, sort_by)

    data = None

    if cell_new_import is not None:
        selected_df = df.iloc[cell_new_import['row']]
        data = selected_df.to_json(date_format='iso')

    return data
