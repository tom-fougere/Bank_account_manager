import dash_core_components as dcc
import dash_html_components as html
from apps.graphs.my_figures import fig_expenses_vs_gain, fig_expenses_vs_category, fig_indicator_expense_in_month,\
    fig_savings, fig_loan

layout = html.Div(
    [
        html.H1('Mes statistiques',
                style={'textAlign': 'center'}),
        dcc.Graph(id='fig_indicator_expenses_month',
                  figure=fig_indicator_expense_in_month()),
        dcc.Graph(id='fig_expense_vs_revenue',
                  figure=fig_expenses_vs_gain()),
        dcc.Graph(id='fig_expense_vs_category',
                  figure=fig_expenses_vs_category()),
    ]
)