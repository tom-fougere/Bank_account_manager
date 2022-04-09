import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output, State
import dash_table as dt
from app import app

from utils.text_operations import get_project_root
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest
from apps.import_new_data.operations import create_datatable, read_and_format_data, update_db_account
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

    html.Button('Import', id='btn_import_database', n_clicks=0, disabled=True),
    html.Div(id="btn_click"),
    html.Div(id="new_transaction_msg"),
    html.Div(id="table_new_import"),
])


@app.callback(
    Output("new_transaction_msg", 'children'),
    Output("table_new_import", 'children'),
    Output('btn_import_database', 'disabled'),
    Input('drag_upload_file', 'contents'),
    State('drag_upload_file', 'filename'),
    State('btn_import_database', 'disabled'))
def upload_file(list_of_contents, filename, btn_disabled):

    # default outputs
    msg = ''
    dt_transactions = dt.DataTable()
    btn_import_state = btn_disabled

    if list_of_contents is not None:
        # Read data
        df, account_info = read_and_format_data('/'.join([get_project_root(), DATA_FOLDER, filename]),
                                                db_connection=DB_CONN_TRANSACTION)

        # Create message
        msg = 'New transactions = {}'.format(len(df))

        # Convert to dataTable
        dt_transactions = create_datatable(df)

        # Enable button
        btn_import_state = False

    return html.Div(msg), dt_transactions, btn_import_state


@app.callback(
    Output('btn_click', 'children'),
    Input('btn_import_database', 'n_clicks'),
    State('drag_upload_file', 'filename'))
def import_transactions_in_database(n_clicks, filename):
    if n_clicks > 0:

        # Read data
        df, account_info = read_and_format_data('/'.join([get_project_root(), DATA_FOLDER, filename]),
                                                db_connection=DB_CONN_TRANSACTION)
        df_new = df[df['duplicate'] == 'False']
        df_new.drop(columns=['duplicate'])

        update_db_account(account_info=account_info,
                          df=df_new,
                          db_connection=DB_CONN_ACCOUNT)

        # Create connection
        con_transaction = MongoDBConnection(DB_CONN_TRANSACTION)

        # Database ingestion
        ingestion = TransactionIngest(con_transaction, transactions_df=df_new)
        ingestion.ingest()

        return 'The input value was and the button has been clicked {} times'.format(
            n_clicks
        )
    else:
        return None


@app.callback(
    Output('store_transaction_disabled', 'data'),
    [Input('cell_new_import', 'active_cell')],
    [State('drag_upload_file', 'filename')])
def store_disabled_transaction(cell_new_import, filename):

    # Read data
    df, _ = read_and_format_data(full_filename='/'.join([get_project_root(), DATA_FOLDER, filename]),
                                 db_connection=DB_CONN_TRANSACTION)

    data = None

    if cell_new_import is not None:
        selected_df = df.iloc[cell_new_import['row']]
        data = selected_df.to_json(date_format='iso')

    return data
