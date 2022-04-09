import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import home
from apps.sidebar import sidebar
from apps.content import content
from apps.canvas.canvas import canvas
from apps.search_data import search_data
from apps.import_new_data import import_new_data
from apps.graphs import graphs

app.layout = html.Div([
    dcc.Location(id='url'),
    sidebar,
    content,
    canvas,
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return home.layout
    if pathname == '/import_data':
        return import_new_data.layout
    if pathname == '/search_data':
        return search_data.layout
    if pathname == '/stats_one_year':
        return graphs.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
