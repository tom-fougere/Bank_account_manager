import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import Input, Output, State
import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme
from app import app

from source.data_reader.bank_file_reader import BankTSVReader
from utils.text_operations import get_project_root
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest

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


def create_datatable(df):

    df_display = df.copy()
    df_display = df_display[['date_transaction', 'amount', 'description', 'type_transaction', 'date']]
    df_display.rename(columns={'date': 'Date (banque)',
                               'amount': 'Montant (€)',
                               'description': 'Libelé',
                               'type_transaction': 'Type',
                               'date_transaction': 'Date'}, inplace=True)

    columns = [{"name": i, "id": i, } for i in df_display.columns]
    columns[1]['type'] = 'numeric'
    columns[1]['format'] = Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('€')

    dt_transactions = dt.DataTable(id='table_content',
                                   data=df_display.to_dict('records'),
                                   columns=columns,
                                   column_selectable="single",
                                   selected_columns=[],
                                   selected_rows=[],
                                   style_data_conditional=[
                                       {
                                           'if': {
                                               'column_id': 'Montant (€)',
                                               'filter_query': '{Montant (€)} > 0'
                                           },
                                           'backgroundColor': '#B5EEB6'
                                       },
                                   ],
                                   style_cell_conditional=style_cell_conditional,
                                   style_header={
                                       'backgroundColor': 'rgb(210, 210, 210)',
                                       'color': 'black',
                                       'fontWeight': 'bold'
                                   }
                                   )
    return dt_transactions


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
        data_reader = BankTSVReader('/'.join([get_project_root(), DATA_FOLDER, filename]))
        df = data_reader.get_dataframe()

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
        data_reader = BankTSVReader('/'.join([get_project_root(), DATA_FOLDER, filename]))
        df = data_reader.get_dataframe()

        # Create connection
        my_connection = MongoDBConnection(DB_CONNECTION)

        # Database ingestion
        ingestion = TransactionIngest(my_connection, transactions_df=df)
        ingestion.ingest()

        return 'The input value was and the button has been clicked {} times'.format(
            n_clicks
        )
    else:
        return None



