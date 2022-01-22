import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import home
from apps.sidebar import sidebar
from apps.content import content
from apps import new_data_page


app.layout = html.Div([
    dcc.Location(id='url'),
    sidebar,
    content
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return home.layout
    if pathname == '/new_data_page':
        return new_data_page.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
