import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash import Input, Output, State, callback_context
from app import app

from apps.search_data.operations import get_categories, get_sub_categories, get_occasion, \
    search_transactions, create_datatable
from source.definitions import DB_CONN_ACCOUNT, DB_CONN_TRANSACTION, ACCOUNT_ID

layout = html.Div([
    html.Div([
        html.Div("Date de transaction:"),
        dcc.DatePickerRange(
            id='search_date'),
        ]),
    html.Div([
        'Montant (€):',
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
        "Catégorie:",
        html.Div([
            dcc.Dropdown(
                id='search_category',
                options=get_categories(db_connection=DB_CONN_ACCOUNT,
                                       account_id=ACCOUNT_ID),
                value=[],
                multi=True,
                style={'width': '100%'}
            ),
            html.Div(id='search_sub_category',
                     style={'width': '100%'})],  # Dropdown for sub-categories
            style={"display": 'flex'})
        ],
        style={'margin-top': 10}),
    html.Div([
        html.Div([
            'Occasion:',
            dcc.Dropdown(
                id='search_occasion',
                options=get_occasion(db_connection=DB_CONN_ACCOUNT,
                                     account_id=ACCOUNT_ID),
                value=[],
                multi=True,
            )],
            style={'width': '50%'}),
        html.Div([
            "Type transaction:",
            dcc.Dropdown(
                id='search_type',
                options=[],
                value=[],
                multi=True,
            )],
            style={'width': '50%'})
        ],
        style={"display": 'flex',
               'margin-top': 10}),
    html.Div([
        html.Div([
            html.Div("Libelé:"),
            dcc.Textarea(
                id='search_description',
                value=None,
                style={'width': '100%',
                       'height': 40}),
            ],
            style={'width': '50%'}),
        html.Div([
            html.Div("Note:"),
            dcc.Textarea(
                id='search_note',
                value=None,
                style={'width': '100%',
                       'height': 40}),
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
    html.Div(id="table_searched",
             style={'margin-top': 10}),
    html.Div(id='msg')
])


@app.callback(
    Output('table_searched', 'children'),
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
def upload_file(n_clicks, date, description, amount_min, amount_max,
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
    Output('search_sub_category', 'children'),
    Input('search_category', 'value')
)
def update_sub_category(value):
    # Default value
    dropdown_sub_category = dcc.Dropdown(
        value=[],
        multi=True,
        style={'width': '100%'}
    )

    if len(value) > 0:
        dropdown_sub_category = dcc.Dropdown(
            options=get_sub_categories(db_connection=DB_CONN_ACCOUNT,
                                       account_id=ACCOUNT_ID,
                                       categories=value),
            value=[],
            multi=True,
            style={'width': '100%'})

    return dropdown_sub_category
