import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output, State, callback_context
import pandas as pd
import json
from apps.canvas.canvas_transaction_details import create_canvas_content_with_transaction_details

from app import app

canvas = dbc.Offcanvas(
    html.Div([
        html.Div(id='canvas_transaction'),
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
    [Output("canvas_transaction", "children"),
     Output("save_trans_details", "disabled"),
     Output("off_canvas", "is_open")],
    [Input('store_transaction_disabled', 'data'),
     Input('store_transaction_enabled', 'data')],
    State("off_canvas", "is_open"))
def open_canvas(jsonified_data_disabled_trans, jsonified_data_enabled_trans, canvas_is_open):

    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    if (triggered_input == 'store_transaction_disabled') and (jsonified_data_disabled_trans is not None):
        parsed = json.loads(jsonified_data_disabled_trans)
        df = pd.Series(parsed)
        component = create_canvas_content_with_transaction_details(df, disabled=True)
        save_button_disable = True
        canvas_new_update = not canvas_is_open
    elif (triggered_input == 'store_transaction_enabled') and (jsonified_data_enabled_trans is not None):
        parsed = json.loads(jsonified_data_enabled_trans)
        df = pd.Series(parsed)
        component = create_canvas_content_with_transaction_details(df, disabled=False)
        save_button_disable = False
        canvas_new_update = not canvas_is_open
    else:
        component = html.Div()
        save_button_disable = True
        canvas_new_update = canvas_is_open

    clear_data = True

    return component, save_button_disable, canvas_new_update
