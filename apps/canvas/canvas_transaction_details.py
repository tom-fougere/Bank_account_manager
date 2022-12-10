import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from datetime import date

from utils.time_operations import str_to_datetime
from source.definitions import DB_CONN_ACCOUNT, DB_CONN_TRANSACTION, ACCOUNT_ID
from source.transactions.transaction_operations import get_categories_for_dropdown_menu,\
    get_sub_categories_for_dropdown_menu, get_occasion
from source.transactions.transactions_db import TransactionDB


def create_canvas_content_with_transaction_details(df, disabled=True):
    date_transaction = str_to_datetime(df.date_transaction_str, date_format='%d/%m/%Y')
    date_bank = str_to_datetime(df.date_str, date_format='%d/%m/%Y')
    if df.category is not None:
        sub_categories = get_sub_categories_for_dropdown_menu(
                        db_connection=DB_CONN_ACCOUNT,
                        account_id=df.account_id,
                        categories=[df.category],
                        add_suffix_cat=False)
    else:
        sub_categories = []

    layout = html.Div([
        html.Div([
            'Compte bancaire:',
            dcc.Input(
                id='canvas_account_id',
                value=df.account_id,
                style={'width': '100%'},
                disabled=True),
        ],
            style={'margin-top': 10}),
        html.Div([
            html.Div([
                html.Div('Date Transaction:'),
                dcc.DatePickerSingle(
                    id='canvas_date_transaction',
                    date=date(date_transaction.year,
                              date_transaction.month,
                              date_transaction.day),
                    disabled=disabled),
            ],
                style={'width': '50%'}),
            html.Div([
                html.Div('Date à la banque:'),
                dcc.DatePickerSingle(
                    id='canvas_date',
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
                id='canvas_description',
                value=df.description,
                style={'width': '100%'},
                disabled=disabled),
        ],
            style={'margin-top': 10}),
        html.Div([
            'Montant (€):',
            dcc.Input(
                id='canvas_amount',
                value=df.amount,
                style={'width': '100%'},
                type='number',
                disabled=disabled),
        ],
            style={'margin-top': 10}),
        html.Div([
            'Catégorie:',
            dcc.Dropdown(
                id='canvas_category',
                options=get_categories(db_connection=DB_CONN_ACCOUNT,
                                       account_id=df.account_id),
                # value=df.category,
                multi=False,
                style={'width': '100%'},
                disabled=disabled),
            dcc.Dropdown(
                id='canvas_sub_category',
                options=sub_categories,
                # value=df.sub_category,
                multi=False,
                style={'width': '100%'},
                disabled=disabled),
            # sub_cat_layout,
            ],
            style={'margin-top': 10}),
        html.Div([
            'Occasion:',
            dcc.Dropdown(
                id='canvas_occasion',
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
                id='canvas_type',
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
                id='canvas_note',
                value=df.note,
                style={'width': '100%'},
                disabled=disabled),
        ],
            style={'margin-top': 10}),
        html.Div([
            'Pointage:',
            daq.BooleanSwitch(
                id='canvas_check',
                on=df.check,
                disabled=disabled),
        ],
            style={'margin-top': 10}),
    ])

    return layout


def get_transaction_values(df):
    datetime_transaction = str_to_datetime(df.date_transaction_str, date_format='%d/%m/%Y')
    datetime_bank = str_to_datetime(df.date_str, date_format='%d/%m/%Y')

    account_id = df.account_id
    object_id = df['_id'] if '_id' in df.keys() else None
    date_transaction = date(datetime_transaction.year,
                            datetime_transaction.month,
                            datetime_transaction.day)
    date_bank = date(datetime_bank.year,
                     datetime_bank.month,
                     datetime_bank.day)
    description = df.description
    amount = df.amount
    category = df.category
    transaction_type = df.type_transaction
    note = df.note
    check = df.check

    return (account_id, object_id, date_transaction, date_bank, description, amount, category,
            transaction_type, note, check)


def get_sub_categories_dropdown(account_id, category):
    # default value
    sub_categories = []

    # get sub-category if category exists
    if category is not None and len(category) > 0:
        sub_categories = get_sub_categories_for_dropdown_menu(
            db_connection=DB_CONN_ACCOUNT,
            account_id=account_id,
            categories=[category],
            add_suffix_cat=False),
        sub_categories = sub_categories[0]

    return sub_categories


def update_transaction(df):

    # Instantiate the ingestion class
    db = TransactionDB(
        name_connection_metadata=DB_CONN_ACCOUNT,
        name_connection_transaction=DB_CONN_TRANSACTION,
        account_id=ACCOUNT_ID,
    )

    # Ingestion of transactions
    db.update(df)


def delete_transaction(df):

    # Instantiate the ingestion class
    db = TransactionDB(
        name_connection_metadata=DB_CONN_ACCOUNT,
        name_connection_transaction=DB_CONN_TRANSACTION,
        account_id=ACCOUNT_ID,
    )

    # Ingestion of transactions
    db.delete(df)
