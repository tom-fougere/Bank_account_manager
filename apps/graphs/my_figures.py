import numpy as np
import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.time_operations import get_first_day_several_month_before
from apps.graphs.operations import get_data_for_graph
from apps.graphs.pipelines import p_expenses_revenue_per_date, p_balance_category_per_date,\
    p_balance_occasion_per_date, p_savings_per_date, p_loan_per_date


def fig_expenses_vs_revenue():

    now = datetime.datetime.now()
    start_date = get_first_day_several_month_before(now, 6)  # 6 months before

    # Get data
    df = get_data_for_graph(p_expenses_revenue_per_date, date_range=(start_date, now))

    # Transform df
    df['Total_negative'] = - df['Total_negative']  # Negative becomes Positive
    df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

    # Figures
    figure = make_subplots(rows=2, cols=1, subplot_titles=('Revenus VS Dépenses', 'Gain'))
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Total_positive'],
        name='Revenus'
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
        name='Gain',
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

    # Drop Revenue
    df = df[df['Categorie'] != 'Travail']

    # Inverse expenses sign
    df['Balance'] = -df['Balance']

    # Rename empty category by 'None'
    df.loc[df['Categorie'].isna(), 'Categorie'] = 'None'

    figure = px.bar(df, x='date', y='Balance', color='Categorie')

    return figure


def fig_expenses_vs_occasion():

    # Get data
    df = get_data_for_graph(p_balance_occasion_per_date)

    # Inverse expenses sign
    df['Balance'] = -df['Balance']

    # Rename empty category by 'None'
    df.loc[df['Occasion'].isna(), 'Occasion'] = 'None'

    figure = px.bar(df, x='date', y='Balance', color='Occasion')

    return figure


def fig_indicators_revenue_expense_balance():

    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=450,
        title={
            "text": "Revenus"},
        delta={'reference': 400, 'relative': False},
        domain={'row': 0, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=450,
        title={
            "text": "Dépenses"},
        delta={'reference': 400, 'relative': False},
        domain={'row': 0, 'column': 1}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=450,
        title={
            "text": "Gain"},
        delta={'reference': 400, 'relative': False},
        domain={'row': 0, 'column': 2}))

    figure.update_layout(
        grid={'rows': 1, 'columns': 3, 'pattern': "independent"},
        height=250  # px
    )

    return figure


def fig_savings():

    # Get data
    df = get_data_for_graph(p_savings_per_date)

    # Figures
    if len(df) > 0:
        figure = px.line(df, x='date', y='Balance')
    else:
        figure = {}

    return figure


def fig_loan():

    # Get data
    df = get_data_for_graph(p_loan_per_date)

    # Figures
    if len(df) > 0:
        figure = px.line(df, x='date', y='Balance')
    else:
        figure = {}

    return figure


if __name__ == '__main__':
    fig_expenses_vs_category()
