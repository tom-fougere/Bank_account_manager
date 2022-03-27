import dash_core_components as dcc
import dash_html_components as html
from apps.graphs.my_figures import \
    fig_indicators_revenue_expense_balance,\
    fig_expenses_vs_revenue, fig_expenses_vs_category, fig_expenses_vs_occasion, \
    fig_savings, fig_loan, fig_categories, fig_cum_balance

layout = html.Div(
    [
        html.H1('Mes statistiques',
                style={'textAlign': 'center'}),
        dcc.Dropdown(id='dropdown_year_stat',
                     options=[
                         {'label': '2021', 'value': '2021'},
                         {'label': '2022', 'value': '2022'},
                         {'label': '2023', 'value': '2023'},
                        ],
                     value='2021'),
        dcc.Graph(id='fig_indicators_revenue_expense_balance',
                  figure=fig_indicators_revenue_expense_balance()),
        dcc.Graph(id='fig_expenses_vs_revenue',
                  figure=fig_expenses_vs_revenue()),
        dcc.Graph(id='fig_expenses_vs_category',
                  figure=fig_expenses_vs_category()),
        dcc.Graph(id='fig_expenses_vs_occasion',
                  figure=fig_expenses_vs_occasion()),
        dcc.Graph(id='fig_saving',
                  figure=fig_savings()),
        dcc.Graph(id='fig_loan',
                  figure=fig_loan()),
        dcc.Graph(id='fig_categories',
                  figure=fig_categories()),
        dcc.Graph(id='fig_cum_balance',
                  figure=fig_cum_balance())
    ]
)