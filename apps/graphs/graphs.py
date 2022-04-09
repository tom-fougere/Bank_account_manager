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
from apps.graphs.operations import get_list_years
from source.definitions import DB_CONN_TRANSACTION

now = datetime.datetime.now()

layout = html.Div(
    [
        html.H1('Statistiques ' + str(now.year),
                id='title_stat_page',
                style={'textAlign': 'center'}),
        html.Div([
            dbc.Button("Refresh", outline=True, color="secondary", className="btn_refresh", id="btn_refresh"),
            dcc.Dropdown(id='dropdown_year_stat',
                         options=get_list_years(DB_CONN_TRANSACTION),
                         value=now.year,
                         style={'width': '100%',
                                'height': 40,
                                'margin-left': 2}
                         ),
        ], style={'display': 'flex'}
        ),
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
    [Output('title_stat_page', 'children'),
     Output('fig_indicators_revenue_expense_balance', 'figure'),
     Output('fig_expenses_vs_revenue', 'figure'),
     Output('fig_expenses_vs_category', 'figure'),
     Output('fig_expenses_vs_occasion', 'figure'),
     Output('fig_saving', 'figure'),
     Output('fig_loan', 'figure'),
     Output('fig_categories', 'figure'),
     Output('fig_cum_balance', 'figure'),
     Output('dropdown_year_stat', 'options')],
    [Input('btn_refresh', 'n_clicks'),
     Input('dropdown_year_stat', 'value')])
def refresh_page(n_click, selected_year):
    outputs = \
        ' '.join(['Statistiques', str(selected_year)]), \
        fig_indicators_revenue_expense_balance(selected_year),\
        fig_expenses_vs_revenue(selected_year),\
        fig_expenses_vs_category(selected_year),\
        fig_expenses_vs_occasion(selected_year),\
        fig_savings(selected_year),\
        fig_loan(selected_year),\
        fig_categories(selected_year),\
        fig_cum_balance(selected_year),\

    outputs = outputs + (get_list_years(DB_CONN_TRANSACTION),)

    return outputs

