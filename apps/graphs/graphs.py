import dash_core_components as dcc
import dash_html_components as html
from apps.graphs.my_figures import fig_expenses_vs_gain

layout = html.Div(
    [
        html.H1('Mes statistiques',
                style={'textAlign': 'center'}),
        dcc.Graph(id='bargraph',
                  figure=fig_expenses_vs_gain())
    ]
)