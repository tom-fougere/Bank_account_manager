import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash import Input, Output, State
from datetime import date

from app import app
from utils.time_operations import str_to_datetime
from source.data_reader.bank_file_reader import BankTSVReader
from utils.text_operations import get_project_root

DATA_FOLDER = 'raw_data'


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
