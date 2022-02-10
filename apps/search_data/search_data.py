import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash import Input, Output, State, callback_context
from app import app

from apps.search_data.operations import get_categories, get_sub_categories, search_transactions, create_datatable
from source.definitions import DB_CONN_ACCOUNT, DB_CONN_TRANSACTION, ACCOUNT_ID


layout = html.Div([
    html.Div('Compte bancaire:'),
    dcc.Input(
        id='search_account_id',
        value=None,
        style={'width': '100%'},
        type='number'),
    html.Div('Date Transaction'),
    dcc.DatePickerRange(
        id='search_date'
    ),
    html.Div('Libelé'),
    dcc.Textarea(
        id='search_description',
        value=None,
        style={'width': '100%'}),
    html.Div('Montant (€)'),
    dcc.Input(
        id='search_amount_min',
        type="number",
        placeholder="Minimum",
        style={'width': '50%'}),
    dcc.Input(
        id='search_amount_max',
        type="number",
        debounce=True,
        placeholder="Maximum",
        style={'width': '50%'}),
    html.Div('Type:'),
    dcc.Input(
        id='search_type',
        value=None,
        style={'width': '100%'}),
    html.Div('Catégorie:'),
    dcc.Dropdown(
        id='search_category',
        options=get_categories(db_connection=DB_CONN_ACCOUNT,
                               account_id=ACCOUNT_ID),
        value=[],
        multi=True,
        style={'width': '100%'}),
    dcc.Dropdown(
        id='search_sub_category',
        options=get_sub_categories(db_connection=DB_CONN_ACCOUNT,
                                   account_id=ACCOUNT_ID,
                                   categories=[]),
        value=[],
        multi=True,
        style={'width': '100%'}),
    html.Div('Occasion:'),
    dcc.Input(
        id='search_occasion',
        value=None,
        style={'width': '100%'}),
    html.Div('Note:'),
    dcc.Textarea(
        id='search_note',
        value=None,
        style={'width': '100%'}),
    html.Button('Affiche',
                id='btn_search',
                n_clicks=0),
    html.Div(id="table_searched"),
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





