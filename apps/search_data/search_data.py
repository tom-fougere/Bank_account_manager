import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table as dt
import dash_daq as daq
from dash import Input, Output, State, callback_context
from app import app

from datetime import date
from apps.search_data.operations import search_transactions, create_datatable
from source.transactions.transaction_operations import get_categories, get_sub_categories, get_occasion
from source.definitions import DB_CONN_ACCOUNT, DB_CONN_TRANSACTION, ACCOUNT_ID,\
    CATEGORIES, OCCASIONS, TYPE_TRANSACTIONS

layout = html.Div([
    html.Div([
        html.Div([
            html.Div("Date de transaction:"),
            dcc.DatePickerRange(
                id='search_date',
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
                step=10,
                placeholder="Minimum",
                style={'width': '50%'}),
            dcc.Input(
                id='search_amount_max',
                type="number",
                debounce=True,
                step=10,
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
                options=[{'label': cat, 'value': cat} for cat in CATEGORIES.keys()],
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
                options=[{'label': occ, 'value': occ} for occ in OCCASIONS],
                # options=get_occasion(db_connection=DB_CONN_ACCOUNT,
                #                      account_id=ACCOUNT_ID),
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
                options=[{'label': tt, 'value': tt} for tt in TYPE_TRANSACTIONS],
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
    html.Button('Affiche',
                id='btn_search',
                n_clicks=0,
                style={'width': '100%',
                       'margin-top': 10}),
    html.Div(id="table_search",
             style={'margin-top': 10}),
    html.Div(id='msg'),
])


@app.callback(
    Output('table_search', 'children'),
    Input('btn_search', 'n_clicks'),
    [State('search_date', 'value'),
     State('search_description', 'value'),
     State('search_amount_min', 'value'),
     State('search_amount_max', 'value'),
     State('search_type', 'value'),
     State('search_category', 'value'),
     State('search_sub_category', 'value'),
     State('search_occasion', 'value'),
     State('search_note', 'value')]
)
def display_searched_transactions(n_clicks, date, description, amount_min, amount_max,
                        type, category, sub_category, occasion, note):
    dt_transactions = dt.DataTable()

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if 'btn_search' in changed_id:
        filter = {
            'account_id': ACCOUNT_ID,
            'date': date,
            'description': description,
            'amount': [amount_min, amount_max],
            'type': type,
            'category': category,
            'sub_category': sub_category,
            'occasion': occasion,
            'note': note
        }
        df_transaction = search_transactions(connection_name=DB_CONN_TRANSACTION, filter=filter)

        dt_transactions = create_datatable(df_transaction)

    return dt_transactions


@app.callback(
    Output('search_sub_category', 'options'),
    Input('search_category', 'value')
)
def update_sub_category(value):
    # Default value
    options = []

    if len(value) > 0:
        options = get_sub_categories(db_connection=DB_CONN_ACCOUNT,
                                     account_id=ACCOUNT_ID,
                                     categories=value)

    return options


@app.callback(
    Output('store_transaction_enabled', 'data'),
    [Input('cell_search', 'active_cell')],
    [State('search_date', 'value'),
     State('search_description', 'value'),
     State('search_amount_min', 'value'),
     State('search_amount_max', 'value'),
     State('search_type', 'value'),
     State('search_category', 'value'),
     State('search_sub_category', 'value'),
     State('search_occasion', 'value'),
     State('search_note', 'value')])
def store_enabled_transaction(cell_search,
                              date, description, amount_min, amount_max,
                              type, category, sub_category, occasion, note):

    if cell_search is not None:

        filter = {
            'account_id': ACCOUNT_ID,
            'date': date,
            'description': description,
            'amount': [amount_min, amount_max],
            'type': type,
            'category': category,
            'sub_category': sub_category,
            'occasion': occasion,
            'note': note
        }
        df = search_transactions(connection_name=DB_CONN_TRANSACTION, filter=filter)

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