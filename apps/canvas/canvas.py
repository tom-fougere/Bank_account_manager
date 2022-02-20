import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output, State, callback_context
import dash_daq as daq
import pandas as pd
import json
from datetime import date
from apps.canvas.canvas_transaction_details import get_transaction_values
from source.transactions.transaction_operations import get_sub_categories, get_occasion, get_categories
from source.definitions import DB_CONN_ACCOUNT, ACCOUNT_ID

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
        html.Div([
            html.Div('Date Transaction:'),
            dcc.DatePickerSingle(
                id='canvas_date_transaction',
                disabled=True),
        ],
            style={'width': '50%'}),
        html.Div([
            html.Div('Date à la banque:'),
            dcc.DatePickerSingle(
                id='canvas_date',
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
            options=[],
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
            id='save_trans_details',
            n_clicks=0,
            disabled=True,
            style={'width': '100%',
                   'margin-top': 10}),
        dcc.Store(id='store_transaction_enabled'),
        dcc.Store(id='store_transaction_disabled')
        ]),
    id="off_canvas",
    title="Transaction",
    is_open=False,
)


@app.callback(
    [Output("canvas_account_id", "value"),
     Output("canvas_date_transaction", "date"),
     Output("canvas_date", "date"),
     Output("canvas_description", "value"),
     Output("canvas_amount", "value"),
     Output("canvas_category", "value"),
     Output("canvas_sub_category", "options"),
     Output("canvas_sub_category", "value"),
     Output("canvas_occasion", "value"),
     Output("canvas_type", "value"),
     Output("canvas_note", "value"),
     Output("canvas_check", "value")],
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
        transaction_values = (None,) * 12

    return transaction_values


@app.callback(
    [Output("save_trans_details", "disabled"),
     Output("canvas_date", "disabled"),
     Output("canvas_description", "disabled"),
     Output("canvas_amount", "disabled"),
     Output("canvas_category", "disabled"),
     Output("canvas_sub_category", "disabled"),
     Output("canvas_occasion", "disabled"),
     Output("canvas_type", "disabled"),
     Output("canvas_note", "disabled"),
     Output("canvas_check", "disabled")],
    [Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')])
def update_transaction_disable(jsonified_data_disabled_trans, jsonified_data_enabled_trans):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    nb_outputs = 9
    disabled = True
    if (triggered_input == 'store_transaction_disabled') and (jsonified_data_disabled_trans is not None):
        msg = (disabled,) * nb_outputs
        save_button = disabled
    elif (triggered_input == 'store_transaction_enabled') and (jsonified_data_enabled_trans is not None):
        msg = (not disabled,) * nb_outputs
        save_button = not disabled
    else:
        msg = (disabled,) * nb_outputs
        save_button = disabled
    return (save_button,) + msg


@app.callback(
    Output("off_canvas", "is_open"),
    [Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')],
    State("off_canvas", "is_open"))
def update_transaction_disable(data1, data2, canvas_is_open):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    canvas_new_update = canvas_is_open
    if (triggered_input == 'store_transaction_disabled') and (data1 is not None):
        canvas_new_update = not canvas_is_open
    elif (triggered_input == 'store_transaction_enabled') and (data2 is not None):
        canvas_new_update = not canvas_is_open

    return canvas_new_update


# @app.callback(
#     Output('canvas_sub_category', 'options'),
#     Input('canvas_category', 'value')
# )
# def update_sub_category(value):
#     # Default value
#     dropdown_sub_category = [{}]
#     changed_id = [p['prop_id'] for p in callback_context.triggered][0]
#
#     if value is not None and len(value) > 0:
#         dropdown_sub_category = get_sub_categories(
#             db_connection=DB_CONN_ACCOUNT,
#             account_id=ACCOUNT_ID,
#             categories=[value],
#             add_suffix_cat=False),
#
#     return dropdown_sub_category
