import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from utils.time_operations import get_first_day_several_month_before
from apps.graphs.operations import get_data_for_graph
from apps.graphs.pipelines import p_positive_vs_negative_per_date, p_balance_category_per_date,\
    p_balance_occasion_per_date, p_savings_per_date, p_loan_per_date, p_salary_vs_other, p_expenses_category


def fig_indicators_revenue_expense_balance():
    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data from this year
    df_current_year = get_data_for_graph(p_salary_vs_other,
                                         date_range=(start_date, now))

    revenues_current_year = df_current_year['Revenues'].sum()
    expenses_current_year = -df_current_year['Expenses'].sum()

    # Get data from last year
    df_previous_year = get_data_for_graph(p_salary_vs_other,
                                          date_range=(start_date - relativedelta(years=1),
                                                      now - relativedelta(years=1)))
    if len(df_previous_year) > 0:
        revenues_previous_year = df_previous_year['Revenues'].sum()
        expenses_previous_year = -df_previous_year['Expenses'].sum()
    else:
        revenues_previous_year = 0
        expenses_previous_year = 0

    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=revenues_current_year,
        title={
            "text": "Revenus"},
        delta={'reference': revenues_previous_year, 'relative': True},
        domain={'row': 0, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=expenses_current_year,
        title={
            "text": "Dépenses"},
        delta={'reference': expenses_previous_year, 'relative': True},
        domain={'row': 0, 'column': 1}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=revenues_current_year - expenses_current_year,
        title={
            "text": "Gain"},
        delta={'reference': revenues_previous_year - expenses_previous_year, 'relative': True},
        domain={'row': 0, 'column': 2}))

    figure.update_layout(
        grid={'rows': 1, 'columns': 3, 'pattern': "independent"},
        height=250  # px
    )

    return figure


def fig_expenses_vs_revenue():

    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_salary_vs_other, date_range=(start_date, now))

    # Transform df
    df['Expenses'] = - df['Expenses']  # Negative becomes Positive
    df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

    # Figures
    figure = make_subplots(rows=2, cols=1, subplot_titles=('Revenus VS Dépenses', 'Gain'))
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Revenues'],
        name='Revenus'
        ),
        row=1, col=1)
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Expenses'],
        name='Dépenses'
        ),
        row=1, col=1)
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Balance'],
        name='Gain',
        marker_color=df['Color'],
        showlegend=False
        ),
        row=2, col=1)
    figure.add_trace(go.Scatter(
        x=df['date'],
        y=np.zeros(df['date'].shape),
        mode='lines',
        line=dict(dash='dash', color='black'),
        showlegend=False
        ),
        row=2, col=1)
    figure.update_layout(xaxis=dict(tickformat="%b \n%Y"))
    figure.update_layout(xaxis2=dict(tickformat="%b \n%Y"))

    return figure


def fig_expenses_vs_category():

    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_balance_category_per_date, date_range=(start_date, now))

    # Drop Revenue
    df = df[df['Categorie'] != 'Travail']

    # Inverse expenses sign
    df['Balance'] = -df['Balance']

    # Rename empty category by 'None'
    df.loc[df['Categorie'].isna(), 'Categorie'] = 'None'

    figure = px.bar(df, x='date', y='Balance', color='Categorie', text="Categorie")

    return figure


def fig_expenses_vs_occasion():

    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_balance_occasion_per_date, date_range=(start_date, now))

    # Inverse expenses sign
    df['Balance'] = -df['Balance']

    # Rename empty category by 'None'
    df.loc[df['Occasion'].isna(), 'Occasion'] = 'None'

    figure = px.bar(df, x='date', y='Balance', color='Occasion', text="Occasion")

    return figure


def fig_savings():

    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_savings_per_date, date_range=(start_date, now))

    # Figures
    if len(df) > 0:
        figure = px.line(df, x='date', y='Balance')
    else:
        figure = {}

    return figure


def fig_loan():

    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_loan_per_date, date_range=(start_date, now))
    
    # Inverse expenses sign
    df['Balance'] = -df['Balance']

    # Figures
    if len(df) > 0:
        # figure = px.line(df, x='date', y='Balance', markers=True)
        figure = go.Figure()
        figure.add_trace(
            go.Scatter(x=df['date'], y=df['Balance'], mode='lines+markers'))

        # Edit the layout
        figure.update_layout(
            title='Loyer / Prët',
            xaxis_title='Mois',
            yaxis_title='Euros')
    else:
        figure = {}

    return figure


def fig_categories():

    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_expenses_category, date_range=(start_date, now))

    # Adjust the data for the sunburst figure
    df.loc[df['Catégorie'].isna(), ['Catégorie', 'Sous-catégorie']] = 'None'
    df['Somme'] = -df['Somme']
    df['Somme'] = df['Somme'].round(1)

    # Filter positive amount and remove Salary to get only expenses
    df_filter = df.copy()
    df_filter = df_filter[(df_filter['Somme'] >= 0) & (df_filter['Catégorie'] != 'Salaire')]

    figure = px.sunburst(df_filter, path=['Catégorie', 'Sous-catégorie'], values='Somme')

    return figure


def fig_cum_balance():

    now = datetime.datetime.now()
    start_date = datetime.datetime(year=now.year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_salary_vs_other, date_range=(start_date, now))

    # Transform df
    df['CumulativeBalance'] = df['Balance'].cumsum()
    df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

    # Figures
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Balance'],
        name='Gain',
        marker_color=df['Color']
        ),
        secondary_y=False)
    figure.add_trace(go.Scatter(
        x=df['date'],
        y=df['CumulativeBalance'],
        mode='lines',
        line=dict(dash='dash', color='black'),
        name='Cumulative gain'
        ),
        secondary_y=True)

    # Set titles
    figure.update_layout(xaxis=dict(tickformat="%b \n%Y"))
    figure.update_yaxes(title_text="Balance", secondary_y=False)
    figure.update_yaxes(title_text="<b>Cumulative balance</b>", secondary_y=True)
    figure.update_layout(yaxis_showgrid=False)

    return figure


if __name__ == '__main__':
    fig_expenses_vs_category()
