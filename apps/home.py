import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

df = pd.read_csv('https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Bootstrap/Side-Bar/iranian_students.csv')

layout = html.Div(
    [
        html.H1('Synthèse',
                style={'textAlign': 'center'}),
        dcc.Graph(id='bargraph',
                  figure=px.bar(df, barmode='group', x='Years',
                                y=['Girls Kindergarten', 'Boys Kindergarten']))
    ]
)
