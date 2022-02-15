import dash_html_components as html
import dash_bootstrap_components as dbc

canvas = dbc.Offcanvas(
    [html.Div(id='canvas_disable_trans'),
     html.Div(id='canvas_enable_trans')],
    id="off_canvas",
    title="Transaction",
    is_open=False,
)
