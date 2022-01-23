import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import Input, Output, State
import dash_table as dt
import dash_daq as daq
from dash_table.Format import Format, Symbol, Scheme
from app import app
from datetime import date

from source.data_reader.bank_file_reader import BankTSVReader
from utils.text_operations import get_project_root
from utils.time_operations import str_to_datetime

DATA_FOLDER = 'raw_data'


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


def create_sidebar_transaction_details(df):

    date_transaction = str_to_datetime(df.date_transaction, date_format='%d/%m/%Y')
    date_bank = str_to_datetime(df.date, date_format='%d/%m/%Y')

    component = html.Div([
        html.Div('Compte bancaire:'),
        dcc.Input(
            value=df.account_id,
            style={'width': '100%'},
            type='number',
            disabled=True),
        html.Div('Date Transaction'),
        dcc.DatePickerSingle(
            id='date-picker',
            date=date(date_transaction.year, date_transaction.month, date_transaction.day),
            disabled=True),
        html.Div('Libelé'),
        dcc.Textarea(
            value=df.description,
            style={'width': '100%'},
            disabled=True),
        html.Div('Montant (€)'),
        dcc.Input(
            value=df.amount,
            style={'width': '100%'},
            type='number',
            disabled=True),
        html.Div('Type:'),
        dcc.Input(
            value=df.type_transaction,
            style={'width': '100%'},
            disabled=True),
        html.Div('Catégorie:'),
        dcc.Input(
            value=df.category,
            style={'width': '100%'},
            disabled=True),
        dcc.Input(
            value=df.sub_category,
            style={'width': '100%'},
            disabled=True),
        html.Div('Occasion:'),
        dcc.Input(
            value=df.occasion,
            style={'width': '100%'},
            disabled=True),
        html.Div('Date à la banque:'),
        dcc.DatePickerSingle(
            id='date-picker',
            date=date(date_bank.year, date_bank.month, date_bank.day),
            disabled=True),
        html.Div('Note:'),
        dcc.Textarea(
            value=df.note,
            style={'width': '100%'},
            disabled=True),
        html.Div('Pointage:'),
        daq.BooleanSwitch(
            on=df.check,
            disabled=True),
    ])

    return component


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
        df = data_reader.data

        # Create message
        msg = 'New transactions = {}'.format(len(df))

        # Convert to dataTable
        dt_transactions = create_datatable(df)

        # Enable button
        btn_import_state = False

    return html.Div(msg), dt_transactions, btn_import_state


@app.callback(
    [Output("off_canvas", "is_open"),
     Output('canvas_trans_details', 'children')],
    Input('table_content', 'active_cell'),
    [State("off_canvas", "is_open"),
     State('drag_upload_file', 'filename')])
def display_one_transaction(active_cell, canvas_is_open, filename):

    # Read data
    data_reader = BankTSVReader('/'.join([get_project_root(), DATA_FOLDER, filename]))
    df = data_reader.data

    if active_cell is None:
        return canvas_is_open, html.Div()
    else:
        component = create_sidebar_transaction_details(df.iloc[active_cell['row']])
        return (not canvas_is_open), component


@app.callback(
    Output('btn_click', 'children'),
    Input('btn_import_database', 'n_clicks'))
def import_transactions_in_database(n_clicks):
    if n_clicks > 0:
        return 'The input value was and the button has been clicked {} times'.format(
            n_clicks
        )
    else:
        return None



