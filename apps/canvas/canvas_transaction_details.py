import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash import Input, Output, State
from datetime import date

from app import app
from utils.time_operations import str_to_datetime
from apps.import_new_data.operations import read_and_format_data
from utils.text_operations import get_project_root
from source.definitions import DATA_FOLDER, DB_CONN_TRANSACTION, DB_CONN_ACCOUNT
from source.transactions.transaction_operations import get_categories, get_sub_categories, get_occasion


def create_canvas_content_with_transaction_details(df, disabled=True):

    date_transaction = str_to_datetime(df.date_transaction_str, date_format='%d/%m/%Y')
    date_bank = str_to_datetime(df.date_str, date_format='%d/%m/%Y')

    layout = html.Div([
        html.Div([
            'Compte bancaire:',
            dcc.Input(
                id='sidebar_account_id',
                value=df.account_id,
                style={'width': '100%'},
                type='number',
                disabled=True),
            ],
            style={'margin-top': 10}),
        html.Div([
            html.Div([
                html.Div('Date Transaction:'),
                dcc.DatePickerSingle(
                    id='sidebar_date_transaction',
                    date=date(date_transaction.year,
                              date_transaction.month,
                              date_transaction.day),
                    disabled=disabled),
                ],
                style={'width': '50%'}),
            html.Div([
                html.Div('Date à la banque:'),
                dcc.DatePickerSingle(
                    id='sidebar_date',
                    date=date(date_bank.year,
                              date_bank.month,
                              date_bank.day),
                    disabled=disabled),
                ],
                style={'width': '50%'}
            )],
            style={"display": 'flex',
                   'margin-top': 10}),
        html.Div([
            'Libelé:',
            dcc.Textarea(
                id='sidebar_description',
                value=df.description,
                style={'width': '100%'},
                disabled=disabled),
            ],
            style={'margin-top': 10}),
         html.Div([
            'Montant (€):',
            dcc.Input(
                id='sidebar_amount',
                value=df.amount,
                style={'width': '100%'},
                type='number',
                step=10,
                disabled=disabled),
             ],
            style={'margin-top': 10}),
        html.Div([
            'Catégorie:',
            dcc.Dropdown(
                id='sidebar_category',
                options=get_categories(db_connection=DB_CONN_ACCOUNT,
                                       account_id=df.account_id),
                value=df.category,
                multi=False,
                style={'width': '100%'},
                disabled=disabled),
            dcc.Dropdown(
                id='sidebar_sub_category',
                options=get_categories(db_connection=DB_CONN_ACCOUNT,
                                       account_id=df.account_id),
                value=df.sub_category,
                multi=False,
                style={'width': '100%'},
                disabled=disabled),
            ],
            style={'margin-top': 10}),
        html.Div([
            'Occasion:',
            dcc.Dropdown(
                id='sidebar_occasion',
                options=get_occasion(db_connection=DB_CONN_ACCOUNT,
                                     account_id=df.account_id),
                value=df.occasion,
                multi=False,
                style={'width': '100%'},
                disabled=disabled),
            ],
            style={'margin-top': 10}),
        html.Div([
            html.Div('Type:'),
            dcc.Dropdown(
                id='sidebar_type',
                options=[],
                value=df.type_transaction,
                multi=False,
                style={'width': '100%'},
                disabled=disabled),
            ],
            style={'margin-top': 10}),
        html.Div([
            'Note:',
            dcc.Textarea(
                id='sidebar_note',
                value=df.note,
                style={'width': '100%'},
                disabled=disabled),
            ],
            style={'margin-top': 10}),
        html.Div([
            'Pointage:',
            daq.BooleanSwitch(
                id='sidebar_check',
                on=df.check,
                disabled=disabled),
            ],
            style={'margin-top': 10}),
        html.Button(
            'Enregistrer',
            id='save_trans_details',
            n_clicks=0,
            disabled=disabled,
            style={'width': '100%',
                   'margin-top': 10}),
    ])

    return layout


@app.callback(
    Output("off_canvas", "is_open"),
    Input('cell_new_import', 'active_cell'),
    State("off_canvas", "is_open"))
def open_canvas(cell_new_import, canvas_is_open):
    if cell_new_import is None:
        return canvas_is_open
    else:
        return not canvas_is_open


@app.callback(
    Output('canvas_disable_trans', 'children'),
    [Input('cell_new_import', 'active_cell')],
    [State('drag_upload_file', 'filename')])
def display_disabled_transaction(cell_new_import, filename):

    # Read data
    df, _ = read_and_format_data(full_filename='/'.join([get_project_root(), DATA_FOLDER, filename]),
                                 db_connection=DB_CONN_TRANSACTION)

    component = html.Div()

    if cell_new_import is not None:
        component = create_canvas_content_with_transaction_details(df.iloc[cell_new_import['row']], disabled=True)
    # elif cell_search is not None:
    #     print('ok')

    return component


@app.callback(
    Output('canvas_enabled_trans', 'children'),
    Input('cell_search', 'active_cell'))
def display_enabled_transaction(cell_search, canvas_is_open, filename):

    if cell_search is None:
        return canvas_is_open, html.Div()
    else:
        print('ok')
    # Read data
    # df, _ = read_and_format_data(full_filename='/'.join([get_project_root(), DATA_FOLDER, filename]),
    #                              db_connection=DB_CONN_TRANSACTION)
    #
    # if cell_search is None:
    #     return canvas_is_open, html.Div()
    # else:
    #     component = create_canvas_content_with_transaction_details(df.iloc[cell_search['row']], disabled=False)
    #     return (not canvas_is_open), component
