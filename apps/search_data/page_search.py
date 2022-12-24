import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table as dt
import dash_daq as daq
from dash import Input, Output, State, callback_context
from app import app
import time

from datetime import date
from apps.search_data.sd_operations import search_transactions
from apps.tables import format_dataframe, df_to_datatable, InfoDisplay
from apps.components import get_sub_categories_for_dropdown_menu
from source.definitions import DB_CONN_ACCOUNT, DB_CONN_TRANSACTION, ACCOUNT_ID
from source.categories import OCCASIONS, TYPE_TRANSACTIONS, get_list_categories
from apps.components import (
    get_occasions_for_dropdown_menu,
    get_types_transaction_for_dropdown_menu,
)
from utils.time_operations import str_to_datetime

layout = html.Div([
    html.H1('Recherche de données',
            id='title_search_data_page',
            style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Div("Date de transaction:"),
            dcc.DatePickerRange(
                id='search_date',
                clearable=True,
                display_format='DD/MM/YYYY',
                end_date=date.today())
            ], style={'width': '50%'}),
        html.Div([
            html.Div([
                html.Div('Pointage:'),
                daq.BooleanSwitch(
                    id='bool_check',
                    on=False,
                    style={"margin-left": 10}),
                ],
                style={'margin-top': 10,
                       "display": 'flex'}),
            dcc.Dropdown(
                id='search_check',
                options=[{'label': 'Oui', 'value': 'True'},
                         {'label': 'Non', 'value': 'False'}],
                value='False',
                clearable=False,
                style={'width': '100%',
                       'margin-top': 10}
            ),

        ])
    ], style={'display': 'flex',
              'margin-top': 10}),
    html.Div([
        html.Div('Montant (€):'),
        daq.BooleanSwitch(
            id='bool_amount',
            on=False,
            style={"margin-left": 10}),
        ],
        style={'margin-top': 10,
               "display": 'flex'}),
    html.Div([
        html.Div([
            dcc.Input(
                id='search_amount_min',
                type="number",
                step=5,
                placeholder="Minimum",
                style={'width': '50%'}),
            dcc.Input(
                id='search_amount_max',
                type="number",
                debounce=True,
                step=5,
                placeholder="Maximum",
                style={'width': '50%'}),
            ])
        ],
        style={'margin-top': 10}),
    html.Div([
        html.Div('Catégorie:'),
        daq.BooleanSwitch(
            id='bool_category',
            on=False,
            style={"margin-left": 10}),
    ],
        style={'margin-top': 10,
               "display": 'flex'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='search_category',
                options=[{'label': cat, 'value': cat} for cat in get_list_categories()],
                # options=get_categories(db_connection=DB_CONN_ACCOUNT,
                #                        account_id=ACCOUNT_ID),
                value=[],
                multi=True,
                style={'width': '100%'}
            ),
            dcc.Dropdown(
                id='search_sub_category',
                options=[],
                value=[],
                multi=True,
                style={'width': '100%'}
            )],
            style={"display": 'flex'})
        ],
        style={'margin-top': 10}),
    html.Div([
        html.Div([
            html.Div([
                html.Div('Occasion:'),
                daq.BooleanSwitch(
                    id='bool_occasion',
                    on=False,
                    style={"margin-left": 10}),
            ],
                style={"display": 'flex'}),
            dcc.Dropdown(
                id='search_occasion',
                options=get_occasions_for_dropdown_menu(
                    db_connection=DB_CONN_ACCOUNT,
                    account_id=ACCOUNT_ID),
                value=[],
                multi=True,
                style={'margin-top': 10}
            )],
            style={'width': '50%'}),
        html.Div([
            html.Div([
                html.Div('Type transaction:'),
                daq.BooleanSwitch(
                    id='bool_type',
                    on=False,
                    style={"margin-left": 10}),
            ],
                style={"display": 'flex'}),
            dcc.Dropdown(
                id='search_type',
                options=get_types_transaction_for_dropdown_menu(
                    db_connection=DB_CONN_ACCOUNT,
                    account_id=ACCOUNT_ID,
                ),
                value=[],
                multi=True,
                style={'margin-top': 10}
            )],
            style={'width': '50%'})
        ],
        style={"display": 'flex',
               'margin-top': 10}),
    html.Div([
        html.Div([
            html.Div([
                html.Div('Libelé:'),
                daq.BooleanSwitch(
                    id='bool_description',
                    on=False,
                    style={"margin-left": 10}),
            ],
                style={"display": 'flex'}),
            dcc.Textarea(
                id='search_description',
                value=None,
                style={'width': '100%',
                       'height': 40,
                       'margin-top': 10}),
            ],
            style={'width': '50%'}),
        html.Div([
            html.Div([
                html.Div('Note:'),
                daq.BooleanSwitch(
                    id='bool_note',
                    on=False,
                    style={"margin-left": 10}),
                ],
                style={"display": 'flex'}),
            dcc.Textarea(
                id='search_note',
                value=None,
                style={'width': '100%',
                       'height': 40,
                       'margin-top': 10}),
            ],
            style={'width': '50%'})
        ],
        style={"display": 'flex',
               'margin-top': 10}),
    dbc.Button("Affiche",
               outline=True,
               color="secondary",
               className="btn_search",
               id="btn_search",
               style={'width': '100%',
                      'margin-top': 10}
               ),
    html.Div(id="table_search",
             style={'margin-top': 10}),
    html.Div(id='msg'),
])


@app.callback(
    Output('table_search', 'children'),
    [Input('btn_search', 'n_clicks'),
     Input('btn_update_transaction', 'n_clicks')],
    [State('search_date', 'start_date'),
     State('search_date', 'end_date'),
     State('search_description', 'value'),
     State('search_amount_min', 'value'),
     State('search_amount_max', 'value'),
     State('search_type', 'value'),
     State('search_category', 'value'),
     State('search_sub_category', 'value'),
     State('search_occasion', 'value'),
     State('search_note', 'value'),
     State('search_check', 'value'),
     State('bool_description', 'on'),
     State('bool_amount', 'on'),
     State('bool_type', 'on'),
     State('bool_category', 'on'),
     State('bool_occasion', 'on'),
     State('bool_note', 'on'),
     State('bool_check', 'on')
     ]
)
def display_searched_transactions(n_clicks_search, n_clicks_save_transaction,
                                  start_date, end_date, description, amount_min, amount_max,
                                  type, category, sub_category, occasion, note, check,
                                  bool_description, bool_amount, bool_type, bool_category,
                                  bool_occasion, bool_note, bool_check):
    dt_transactions = dt.DataTable()

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if ('btn_search' in changed_id) or ('btn_update_transaction' in changed_id):

        time.sleep(0.5)

        filters = {
            'account_id': (True, ACCOUNT_ID),
            'date_transaction': (True, [
                str_to_datetime(start_date, date_format='%Y-%m-%d') if start_date else start_date,
                str_to_datetime(end_date, date_format='%Y-%m-%d') if end_date else end_date]),
            'description': (bool_description, description),
            'amount': (bool_amount, [amount_min, amount_max]),
            'type_transaction': (bool_type, type),
            'category': (bool_category, category),
            'sub_category': (bool_category, sub_category),
            'occasion': (bool_occasion, occasion),
            'note': (bool_note, note),
            'check': (bool_check, eval(check))
        }
        df_transaction = search_transactions(connection_name=DB_CONN_TRANSACTION, filters=filters)

        df_display = format_dataframe(df_transaction, InfoDisplay.SEARCH)
        dt_transactions = df_to_datatable(df_display, table_id='cell_search')

    return dt_transactions


@app.callback(
    Output('search_sub_category', 'options'),
    Input('search_category', 'value')
)
def update_sub_category(value):
    # Default value
    options = []

    if len(value) > 0:
        options = get_sub_categories_for_dropdown_menu(
            db_connection=DB_CONN_ACCOUNT,
            account_id=ACCOUNT_ID,
            categories=value)

    return options


@app.callback(
    Output('store_transaction_enabled', 'data'),
    [Input('cell_search', 'active_cell')],
    [State('search_date', 'start_date'),
     State('search_date', 'end_date'),
     State('search_description', 'value'),
     State('search_amount_min', 'value'),
     State('search_amount_max', 'value'),
     State('search_type', 'value'),
     State('search_category', 'value'),
     State('search_sub_category', 'value'),
     State('search_occasion', 'value'),
     State('search_note', 'value'),
     State('search_check', 'value'),
     State('bool_description', 'on'),
     State('bool_amount', 'on'),
     State('bool_type', 'on'),
     State('bool_category', 'on'),
     State('bool_occasion', 'on'),
     State('bool_note', 'on'),
     State('bool_check', 'on')])
def store_enabled_transaction(cell_search,
                              start_date, end_date, description, amount_min, amount_max,
                              type, category, sub_category, occasion, note, check,
                              bool_description, bool_amount, bool_type, bool_category,
                              bool_occasion, bool_note, bool_check):

    if cell_search is not None:

        filters = {
            'account_id': (True, ACCOUNT_ID),
            'date_transaction': (True, [
                str_to_datetime(start_date, date_format='%Y-%m-%d') if start_date else start_date,
                str_to_datetime(end_date, date_format='%Y-%m-%d') if end_date else end_date]),
            'description': (bool_description, description),
            'amount': (bool_amount, [amount_min, amount_max]),
            'type_transaction': (bool_type, type),
            'category': (bool_category, category),
            'sub_category': (bool_category, sub_category),
            'occasion': (bool_occasion, occasion),
            'note': (bool_note, note),
            'check': (bool_check, eval(check))
        }
        df = search_transactions(connection_name=DB_CONN_TRANSACTION, filters=filters)

        selected_df = df.iloc[cell_search['row']]

        # Convert objectID into string
        replace_object_id(selected_df)

        data = selected_df.to_json(date_format='iso')
    else:
        data = None

    return data


@app.callback(
    [Output('search_amount_min', 'disabled'),
     Output('search_amount_max', 'disabled'),
     Output('search_type', 'disabled'),
     Output('search_category', 'disabled'),
     Output('search_sub_category', 'disabled'),
     Output('search_occasion', 'disabled'),
     Output('search_description', 'disabled'),
     Output('search_note', 'disabled'),
     Output('search_check', 'disabled')],
    [Input('bool_amount', 'on'),
     Input('bool_category', 'on'),
     Input('bool_type', 'on'),
     Input('bool_occasion', 'on'),
     Input('bool_description', 'on'),
     Input('bool_note', 'on'),
     Input('bool_check', 'on')])
def disable_enable_search_components(bool_amount, bool_category, bool_type, bool_occasion, bool_description, bool_note,
                                     bool_check):

    list_enabled_components = [not bool_amount, not bool_amount,
                               not bool_type,
                               not bool_category, not bool_category,
                               not bool_occasion,
                               not bool_description,
                               not bool_note,
                               not bool_check]

    return list_enabled_components


def replace_object_id(df):
    df['_id'] = str(df['_id'])
