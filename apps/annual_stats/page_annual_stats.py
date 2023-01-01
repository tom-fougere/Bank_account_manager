import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash import Input, Output
from app import app
from apps.annual_stats.as_figures import (
    fig_indicators_revenue_expense_balance,
    fig_expenses_vs_revenue,
    fig_cum_balance,
    fig_expenses_vs_category,
    fig_expenses_vs_occasion,
    fig_savings,
    fig_loan,
    fig_nb_transactions_vs_category
)


layout = html.Div(
    [
        html.H1('Statistiques annuelles',
                id='title_year_graphs_page',
                style={'textAlign': 'center'}),
        dbc.Button("Refresh",
                   outline=True,
                   color="secondary",
                   className="btn_refresh_year_graphs",
                   id="btn_refresh_year_graphs",
                   style={'width': '100%',
                          'margin-top': 10}),
        dcc.Graph(id='fig_yg_indicators_revenue_expense_balance',
                  figure=fig_indicators_revenue_expense_balance(),
                  style={'margin-top': 10}),
        dcc.Graph(id='fig_yg_expenses_vs_revenue',
                  figure=fig_expenses_vs_revenue()),
        dcc.Graph(id='fig_yg_cum_balance',
                  figure=fig_cum_balance()),
        dcc.Graph(id='fig_yg_expenses_vs_category',
                  figure=fig_expenses_vs_category()),
        dcc.Graph(id='fig_yg_expenses_vs_occasion',
                  figure=fig_expenses_vs_occasion()),
        dcc.Graph(id='fig_nb_transactions',
                  figure=fig_nb_transactions_vs_category()),
        dcc.Graph(id='fig_yg_loan',
                  figure=fig_loan()),
        dcc.Graph(id='fig_yg_saving',
                  figure=fig_savings()),
    ]
)


@app.callback(
    [Output('fig_yg_indicators_revenue_expense_balance', 'figure'),
     Output('fig_yg_expenses_vs_revenue', 'figure'),
     Output('fig_yg_expenses_vs_category', 'figure'),
     Output('fig_yg_expenses_vs_occasion', 'figure'),
     Output('fig_yg_saving', 'figure'),
     Output('fig_yg_loan', 'figure'),
     Output('fig_yg_cum_balance', 'figure')],
    Input('btn_refresh', 'n_clicks'))
def refresh_page(n_click):
    outputs = \
        fig_indicators_revenue_expense_balance(),\
        fig_expenses_vs_revenue(),\
        fig_expenses_vs_category(),\
        fig_expenses_vs_occasion(),\
        fig_savings(),\
        fig_loan(),\
        fig_cum_balance(),\

    return outputs

