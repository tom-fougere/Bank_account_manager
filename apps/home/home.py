from dash import html, dcc

from apps.home.operations import fig_indicators_balances


layout = html.Div([

    html.H1('Home page',
            id='title_home_page',
            style={'textAlign': 'center'}),
    dcc.Graph(id='fig_indicator_balance',
              figure=fig_indicators_balances(),
              style={'height': '90vh'}),
])
