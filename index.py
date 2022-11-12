import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps.home import home
from apps.sidebar import sidebar
from apps.content import content
from apps.canvas.canvas import canvas
from apps.search_data import page_search
from apps.import_new_data import page_import
from apps.current_stats import page_current_stats
from apps.annual_stats import page_annual_stats
from apps.params_category import page_category

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
        return page_import.layout
    if pathname == '/search_data':
        return page_search.layout
    if pathname == '/current_stats':
        return page_current_stats.layout
    if pathname == '/annual_stats':
        return page_annual_stats.layout
    if pathname == '/params_category':
        return page_category.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
