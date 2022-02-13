import dash_html_components as html
import dash_bootstrap_components as dbc

canvas = dbc.Offcanvas(
    [html.Div(id='canvas_trans_details')],
    id="off_canvas",
    title="Transaction",
    is_open=False,
)
