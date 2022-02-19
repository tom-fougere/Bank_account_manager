import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from datetime import date

from utils.time_operations import str_to_datetime
from source.definitions import DB_CONN_ACCOUNT
from source.transactions.transaction_operations import get_categories, get_occasion


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
                    disabled=True),
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
    ])

    return layout

