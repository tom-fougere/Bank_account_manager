import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output, State, callback_context
import dash_daq as daq
import pandas as pd
import json
from apps.canvas.canvas_transaction_details import get_transaction_values,\
    get_sub_categories_dropdown, update_transaction
from source.transactions.transaction_operations import get_occasion, get_categories, get_types_transaction
from source.definitions import DB_CONN_ACCOUNT, ACCOUNT_ID, DEFAULT_OCCASION_FOR_CAT

from app import app


transaction_details_layout = html.Div([
    html.Div([
        'Compte bancaire:',
        dcc.Input(
            id='canvas_account_id',
            style={'width': '100%'},
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        'ObjectID:',
        dcc.Input(
            id='canvas_object_id',
            style={'width': '100%'},
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        html.Div([
            html.Div('Date à la banque:'),
            dcc.DatePickerSingle(
                id='canvas_date',
                disabled=True),
        ],
            style={'width': '50%'}),
        html.Div([
            html.Div('Date Transaction:'),
            dcc.DatePickerSingle(
                id='canvas_date_transaction',
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
            style={'width': '100%'},
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        'Montant (€):',
        dcc.Input(
            id='canvas_amount',
            style={'width': '100%'},
            type='number',
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        'Catégorie:',
        dcc.Dropdown(
            id='canvas_category',
            options=get_categories(db_connection=DB_CONN_ACCOUNT,
                                   account_id=ACCOUNT_ID),
            # value=df.category,
            multi=False,
            style={'width': '100%'},
            disabled=True),
        dcc.Dropdown(
            id='canvas_sub_category',
            options=None,
            multi=False,
            style={'width': '100%'},
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        'Occasion:',
        dcc.Dropdown(
            id='canvas_occasion',
            options=get_occasion(db_connection=DB_CONN_ACCOUNT,
                                 account_id=ACCOUNT_ID),
            multi=False,
            style={'width': '100%'},
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        html.Div('Type:'),
        dcc.Dropdown(
            id='canvas_type',
            options=get_types_transaction(db_connection=DB_CONN_ACCOUNT,
                                          account_id=ACCOUNT_ID),
            multi=False,
            style={'width': '100%'},
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        'Note:',
        dcc.Textarea(
            id='canvas_note',
            style={'width': '100%'},
            disabled=True),
    ],
        style={'margin-top': 10}),
    html.Div([
        'Pointage:',
        daq.BooleanSwitch(
            id='canvas_check',
            disabled=True),
    ],
        style={'margin-top': 10}),
])


canvas = dbc.Offcanvas(
    html.Div([
        transaction_details_layout,
        html.Button(
            'Enregistrer',
            id='btn_update_transaction',
            n_clicks=0,
            disabled=True,
            style={'width': '100%',
                   'margin-top': 10}),
        dcc.Store(id='store_transaction_enabled'),
        dcc.Store(id='store_transaction_disabled'),
        html.Div(id='msg_update_transaction')
        ]),
    id="off_canvas",
    title="Transaction",
    is_open=False,
)


@app.callback(
    [Output("canvas_account_id", "value"),
     Output("canvas_object_id", "value"),
     Output("canvas_date_transaction", "date"),
     Output("canvas_date", "date"),
     Output("canvas_description", "value"),
     Output("canvas_amount", "value"),
     Output("canvas_category", "value"),
     Output("canvas_type", "value"),
     Output("canvas_note", "value"),
     Output("canvas_check", "on")],
    [Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')])
def update_transaction_values(jsonified_data_disabled_trans, jsonified_data_enabled_trans):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    if (triggered_input == 'store_transaction_disabled') and (jsonified_data_disabled_trans is not None):
        parsed = json.loads(jsonified_data_disabled_trans)
        df = pd.Series(parsed)
        transaction_values = get_transaction_values(df)
    elif (triggered_input == 'store_transaction_enabled') and (jsonified_data_enabled_trans is not None):
        parsed = json.loads(jsonified_data_enabled_trans)
        df = pd.Series(parsed)
        transaction_values = get_transaction_values(df)
    else:
        transaction_values = (None,) * 10

    return transaction_values


@app.callback(
    [Output("btn_update_transaction", "disabled"),
     Output("canvas_date", "disabled"),
     Output("canvas_category", "disabled"),
     Output("canvas_sub_category", "disabled"),
     Output("canvas_occasion", "disabled"),
     Output("canvas_note", "disabled"),
     Output("canvas_check", "disabled")],
    [Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')])
def enable_disable_canvas_components(jsonified_data_disabled_trans, jsonified_data_enabled_trans):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    nb_outputs = 6
    disabled = True
    if (triggered_input == 'store_transaction_disabled') and (jsonified_data_disabled_trans is not None):
        disable_options = (disabled,) * nb_outputs
        save_button = disabled

    elif (triggered_input == 'store_transaction_enabled') and (jsonified_data_enabled_trans is not None):
        disable_options = (not disabled,) * nb_outputs
        save_button = not disabled
    else:
        disable_options = (disabled,) * nb_outputs
        save_button = disabled

    return (save_button,) + disable_options


@app.callback(
    Output("canvas_type", "disabled"),
    [Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')])
def enable_type_transaction(jsonified_data_disabled_trans, jsonified_data_enabled_trans):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    disable = True
    if (triggered_input == 'store_transaction_disabled') and (jsonified_data_disabled_trans is not None):
        disable = True
    elif (triggered_input == 'store_transaction_enabled') and (jsonified_data_enabled_trans is not None):
        parsed = json.loads(jsonified_data_enabled_trans)
        df = pd.Series(parsed)
        type_transaction = df['type_transaction']
        if type_transaction is None:
            disable = False
        else:
            disable = True

    return disable


@app.callback(
    [Output('canvas_sub_category', 'options'),
     Output('canvas_sub_category', 'value')],
    [Input('canvas_category', 'value'),
     Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')],
)
def update_sub_category(canvas_category, jsonified_data_disabled_trans, jsonified_data_enabled_trans):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    # Default value
    dropdown_sub_category = []
    value_sub_category = None

    # get sub-categories
    if canvas_category is not None:
        dropdown_sub_category = get_sub_categories_dropdown(
            account_id=ACCOUNT_ID,
            category=canvas_category)

    # Set sub-category
    if (triggered_input == 'store_transaction_disabled') and (jsonified_data_disabled_trans is not None):
        parsed = json.loads(jsonified_data_disabled_trans)
        df = pd.Series(parsed)
        value_sub_category = df['sub_category']
    elif (triggered_input == 'store_transaction_enabled') and (jsonified_data_enabled_trans is not None):
        parsed = json.loads(jsonified_data_enabled_trans)
        df = pd.Series(parsed)
        value_sub_category = df['sub_category']

    return dropdown_sub_category, value_sub_category


@app.callback(
    Output('canvas_occasion', 'value'),
    [Input('canvas_category', 'value'),
     Input('canvas_sub_category', 'value'),
     Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')],
    State('canvas_occasion', 'value')
)
def update_occasion(canvas_category, canvas_sub_category, jsonified_data_disabled_trans, jsonified_data_enabled_trans,
                    current_occasion):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    # Default value
    value_occasion = current_occasion

    # Set sub-category
    if (triggered_input == 'store_transaction_disabled') and (jsonified_data_disabled_trans is not None):
        parsed = json.loads(jsonified_data_disabled_trans)
        df = pd.Series(parsed)
        value_occasion = df['occasion']
    elif (triggered_input == 'store_transaction_enabled') and (jsonified_data_enabled_trans is not None):
        parsed = json.loads(jsonified_data_enabled_trans)
        df = pd.Series(parsed)
        value_occasion = df['occasion']
    elif triggered_input == 'canvas_category':
        if not isinstance(DEFAULT_OCCASION_FOR_CAT[canvas_category], dict):
            value_occasion = DEFAULT_OCCASION_FOR_CAT[canvas_category]
    elif triggered_input == 'canvas_sub_category':
        if isinstance(DEFAULT_OCCASION_FOR_CAT[canvas_category], dict):
            value_occasion = DEFAULT_OCCASION_FOR_CAT[canvas_category][canvas_sub_category]

    return value_occasion


@app.callback(
    Output("off_canvas", "is_open"),
    [Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')],
    State("off_canvas", "is_open"))
def open_close_canvas(data1, data2, canvas_is_open):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    canvas_new_update = canvas_is_open
    if (triggered_input == 'store_transaction_disabled') and (data1 is not None):
        canvas_new_update = not canvas_is_open
    elif (triggered_input == 'store_transaction_enabled') and (data2 is not None):
        canvas_new_update = not canvas_is_open

    return canvas_new_update


@app.callback(
    Output("msg_update_transaction", "children"),
    [Input('btn_update_transaction', 'n_clicks'),
     Input("off_canvas", "is_open")],
    [State("canvas_account_id", "value"),
     State("canvas_object_id", "value"),
     State("canvas_date_transaction", "date"),
     State("canvas_date", "date"),
     State("canvas_description", "value"),
     State("canvas_amount", "value"),
     State("canvas_category", "value"),
     State("canvas_sub_category", "value"),
     State("canvas_occasion", "value"),
     State("canvas_type", "value"),
     State("canvas_note", "value"),
     State("canvas_check", "on")],
)
def update_transaction_values(click, off_canvas,
                              account_id, object_id, date_transaction, date_bank, description, amount, category,
                              sub_category, occasion, transaction_type, note, check):

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    # default value
    update_msg = ''

    if 'btn_update_transaction' in changed_id:

        # Transaction with new values
        new_trans_dict = {
            '_id': object_id,
            'account_id': account_id,
            'date_transaction_str': date_transaction,
            'date_str': date_bank,
            'description': description,
            'amount': amount,
            'category': category,
            'sub_category': sub_category,
            'occasion': occasion,
            'transaction_type': transaction_type,
            'note': note,
            'check': check,
        }
        new_transaction = pd.DataFrame([new_trans_dict])

        # Update transaction in DB
        update_transaction(new_transaction)

        update_msg = 'Transaction mise à jour !'

    return update_msg
