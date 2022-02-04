import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import Input, Output, State
import dash_table as dt
from app import app

from utils.text_operations import get_project_root
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest
from apps.import_new_data.operations import create_datatable, read_and_format_data
from apps.canvas.canvas_transaction_details import display_one_transaction

DATA_FOLDER = 'raw_data'
DB_CONNECTION = 'db_bank_connection'


layout = html.Div([

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
    html.Div(id="table"),
    dbc.Offcanvas(
            [html.P("Transaction"
                    "Details"),
             html.Div(id='canvas_trans_details')],
            id="off_canvas",
            title="Title",
            is_open=False,
        ),

])


@app.callback(
    Output("new_transaction_msg", 'children'),
    Output("table", 'children'),
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
        df = read_and_format_data('/'.join([get_project_root(), DATA_FOLDER, filename]), db_connection=DB_CONNECTION)

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
        df = read_and_format_data('/'.join([get_project_root(), DATA_FOLDER, filename]), db_connection=DB_CONNECTION)

        # Create connection
        my_connection = MongoDBConnection(DB_CONNECTION)

        # Database ingestion
        ingestion = TransactionIngest(my_connection, transactions_df=df[df['duplicate'] is True])
        ingestion.ingest()

        return 'The input value was and the button has been clicked {} times'.format(
            n_clicks
        )
    else:
        return None