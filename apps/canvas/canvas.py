import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output, State
import pandas as pd
import json
from apps.canvas.canvas_transaction_details import create_canvas_content_with_transaction_details

from app import app

canvas = dbc.Offcanvas(
    html.Div([
        html.Div(id='canvas_transaction'),
        dcc.Store(id='store_transaction_enabled'),
        dcc.Store(id='store_transaction_disabled')
        ]),
    id="off_canvas",
    title="Transaction",
    is_open=False,
)


@app.callback(
    [Output("canvas_transaction", "children"),
     Output("off_canvas", "is_open")],
    Input('store_transaction_disabled', 'data'),
    Input('store_transaction_enabled', 'data'),
    State("off_canvas", "is_open"))
def open_canvas(jsonified_data_disabled_trans, jsonified_data_enabled_trans, canvas_is_open):

    if jsonified_data_disabled_trans is not None:
        parsed = json.loads(jsonified_data_disabled_trans)
        df = pd.Series(parsed)
        component = create_canvas_content_with_transaction_details(df, disabled=True)
        canvas_new_update = not canvas_is_open
    elif jsonified_data_enabled_trans is not None:
        parsed = json.loads(jsonified_data_enabled_trans)
        df = pd.Series(parsed)
        component = create_canvas_content_with_transaction_details(df, disabled=False)
        canvas_new_update = not canvas_is_open
    else:
        component = html.Div()
        canvas_new_update = canvas_is_open

    return component, canvas_new_update
