import dash_core_components as dcc
import dash_html_components as html


DB_CONNECTION = 'db_bank_connection'


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
        options=[
            {'label': 'New York City', 'value': 'NYC'},
            {'label': 'Montreal', 'value': 'MTL'},
            {'label': 'San Francisco', 'value': 'SF'}
        ],
        value=['MTL', 'NYC'],
        multi=True,
        style={'width': '100%'}),
    dcc.Input(
        id='search_sub_category',
        value=None,
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
    html.Div(id="table"),
])




