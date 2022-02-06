import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash import Input, Output, State
from datetime import date

from app import app
from utils.time_operations import str_to_datetime
from apps.import_new_data.operations import read_and_format_data
from utils.text_operations import get_project_root
from source.definitions import DATA_FOLDER, DB_CONN_TRANSACTION


def create_sidebar_transaction_details(df, disabled=True):

    date_transaction = str_to_datetime(df.date_transaction_str, date_format='%d/%m/%Y')
    date_bank = str_to_datetime(df.date_str, date_format='%d/%m/%Y')

    component = html.Div([
        html.Div('Compte bancaire:'),
        dcc.Input(
            id='sidebar_account_id',
            value=df.account_id,
            style={'width': '100%'},
            type='number',
            disabled=disabled),
        html.Div('Date Transaction'),
        dcc.DatePickerSingle(
            id='sidebar_date_transaction',
            date=date(date_transaction.year, date_transaction.month, date_transaction.day),
            disabled=disabled),
        html.Div('Libelé'),
        dcc.Textarea(
            id='sidebar_description',
            value=df.description,
            style={'width': '100%'},
            disabled=disabled),
        html.Div('Montant (€)'),
        dcc.Input(
            id='sidebar_amount',
            value=df.amount,
            style={'width': '100%'},
            type='number',
            disabled=disabled),
        html.Div('Type:'),
        dcc.Input(
            id='sidebar_type',
            value=df.type_transaction,
            style={'width': '100%'},
            disabled=disabled),
        html.Div('Catégorie:'),
        dcc.Input(
            id='sidebar_category',
            value=df.category,
            style={'width': '100%'},
            disabled=disabled),
        dcc.Input(
            id='sidebar_sub_category',
            value=df.sub_category,
            style={'width': '100%'},
            disabled=disabled),
        html.Div('Occasion:'),
        dcc.Input(
            id='sidebar_occasion',
            value=df.occasion,
            style={'width': '100%'},
            disabled=disabled),
        html.Div('Date à la banque:'),
        dcc.DatePickerSingle(
            id='sidebar_date',
            date=date(date_bank.year, date_bank.month, date_bank.day),
            disabled=disabled),
        html.Div('Note:'),
        dcc.Textarea(
            id='sidebar_note',
            value=df.note,
            style={'width': '100%'},
            disabled=disabled),
        html.Div('Pointage:'),
        daq.BooleanSwitch(
            id='sidebar_check',
            on=df.check,
            disabled=disabled),
        html.Button(
            'Enregistrer',
            id='save_trans_details',
            n_clicks=0,
            disabled=disabled),
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
    df, _ = read_and_format_data(full_filename='/'.join([get_project_root(), DATA_FOLDER, filename]),
                                 db_connection=DB_CONN_TRANSACTION)

    if active_cell is None:
        return canvas_is_open, html.Div()
    else:
        component = create_sidebar_transaction_details(df.iloc[active_cell['row']])
        return (not canvas_is_open), component
