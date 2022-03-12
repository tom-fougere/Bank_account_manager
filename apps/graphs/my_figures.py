import numpy as np
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from apps.graphs.operations import get_data_for_graph
from apps.graphs.pipelines import p_expenses_gains_per_date, p_balance_category_per_date,\
    p_savings_per_date, p_loan_per_date


def fig_expenses_vs_gain():

    # Get data
    df = get_data_for_graph(p_expenses_gains_per_date)

    # Transform df
    df['Total_negative'] = - df['Total_negative']  # Negative becomes Positive
    df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

    # Figures
    figure = make_subplots(rows=2, cols=1)
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Total_positive'],
        name='Gains'
        ),
        row=1, col=1)
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Total_negative'],
        name='Dépenses'
        ),
        row=1, col=1)
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Balance'],
        name='Balance',
        marker_color=df['Color']
        ),
        row=2, col=1)
    figure.add_trace(go.Scatter(
        x=df['date'],
        y=np.zeros(df['date'].shape),
        mode='lines',
        line=dict(dash='dash', color='black')
        ),
        row=2, col=1)
    figure.update_layout(xaxis=dict(tickformat="%b \n%Y"))
    figure.update_layout(xaxis2=dict(tickformat="%b \n%Y"))

    return figure


def fig_expenses_vs_category():

    # Get data
    df = get_data_for_graph(p_balance_category_per_date)

    # Figures
    figure = go.Figure(data=[
        go.Bar(x=df['date'], y=df['Balance'])
    ])
    figure.update_layout(barmode='stack')

    return figure


def fig_indicator_expense_in_month():

    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=450,
        title={
            "text": "Dépenses"},
        delta={'reference': 400, 'relative': False},
        domain={'x': [0.6, 1], 'y': [0, 1]}))

    return figure

if __name__ == '__main__':
    fig_expenses_vs_category()
