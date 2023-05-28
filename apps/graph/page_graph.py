import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output, State, callback_context
from app import app


from apps.graph.g_figures import custom_fig, get_data_label

layout_axes = html.Div(
    [
        html.Div(
            [
                html.Div('Donnée X:'),
                dcc.Dropdown(
                    id='menu_x',
                    options=[{'label': label, 'value': label} for label in get_data_label()],
                    clearable=False
                ),
            ],
        ),
        html.Div(
            [
                html.Div('Donnée Y:'),
                dcc.Dropdown(
                    id='menu_y',
                    options=[{'label': label, 'value': label} for label in get_data_label()],
                    clearable=False
                ),
            ],
        ),
    ]
)

layout = html.Div(
    [
        html.H4("Graphique personnalisé"),
        layout_axes,
        dcc.Graph(id='fig_custom_graph',
                  figure=custom_fig(x_data_str=None, y_data_str=None),
                  style={'margin-top': 10}),
    ]
)


@app.callback(
    Output('fig_custom_graph', 'figure'),
    Input('menu_x', 'value'),
    Input('menu_y', 'value'),
)
def refresh_page(menu_x, menu_y):
    figure = custom_fig(x_data_str=menu_x, y_data_str=menu_y)

    return figure
