import datetime
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output, State, callback_context
from app import app
from apps.graphs.my_figures import \
    fig_indicators_revenue_expense_balance,\
    fig_expenses_vs_revenue, fig_expenses_vs_category, fig_expenses_vs_occasion, \
    fig_savings, fig_loan, fig_categories, fig_cum_balance

now = datetime.datetime.now()

layout = html.Div(
    [
        html.H1('Mes statistiques',
                style={'textAlign': 'center'}),
        html.Div([
            dbc.Button("Refresh", outline=True, color="secondary", className="btn_refresh", id="btn_refresh"),
            dcc.Dropdown(id='dropdown_year_stat',
                         options=[
                             {'label': '2021', 'value': '2021'},
                             {'label': '2022', 'value': '2022'},
                             {'label': '2023', 'value': '2023'},
                            ],
                         value='2021',
                         style={'width': '100%',
                                'height': 40,
                                'margin-left': 2}
                         ),
        ], style={'display': 'flex'}
        ),
        html.Div(id='refresh_msg'),
        dcc.Graph(id='fig_indicators_revenue_expense_balance',
                  figure=fig_indicators_revenue_expense_balance(now.year),
                  style={'margin-top': 10}),
        dcc.Graph(id='fig_expenses_vs_revenue',
                  figure=fig_expenses_vs_revenue(now.year)),
        dcc.Graph(id='fig_expenses_vs_category',
                  figure=fig_expenses_vs_category(now.year)),
        dcc.Graph(id='fig_expenses_vs_occasion',
                  figure=fig_expenses_vs_occasion(now.year)),
        dcc.Graph(id='fig_saving',
                  figure=fig_savings(now.year)),
        dcc.Graph(id='fig_loan',
                  figure=fig_loan(now.year)),
        dcc.Graph(id='fig_categories',
                  figure=fig_categories(now.year)),
        dcc.Graph(id='fig_cum_balance',
                  figure=fig_cum_balance(now.year))
    ]
)


@app.callback(
    Output('refresh_msg', 'children'),
    Input('btn_refresh', 'n_clicks'))
def refresh_page(n_click):
    return str(n_click)

