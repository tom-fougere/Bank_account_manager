import numpy as np
import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from apps.current_stats.cs_operations import get_data_for_graph, format_df_saving, get_revenue_expences_savings_year
from apps.current_stats.cs_pipelines import (
    p_balance_category_per_date,
    p_balance_occasion_per_date,
    p_savings_per_date,
    p_loan_per_date,
    p_salary_vs_other,
    p_expenses_category,
    p_nb_transactions_per_category)
from source.definitions import MONTHS
from source.categories import OCCASIONS


def fig_indicators_revenue_expense_balance(year=datetime.datetime.now().year):

    # ##############
    # CURRENT YEAR
    # ##############
    start_date = datetime.datetime(year=year, month=1, day=1)
    end_date = datetime.datetime(year=year, month=12, day=31)

    # Get data from this year
    df_cy = get_data_for_graph(p_salary_vs_other,
                               date_range=(start_date, end_date))
    df_savings_cy = get_data_for_graph(p_savings_per_date,
                                       date_range=(start_date, end_date))

    # Get data from last year

    # ##############
    # PREVIOUS YEAR
    # ##############
    now = datetime.datetime.now()
    start_date_py = datetime.datetime(year=year-1, month=1, day=1)
    end_date_py = datetime.datetime(year=year-1, month=12, day=31)
    if year == now.year:
        end_date_py = datetime.datetime(year=year-1, month=now.month, day=now.day)

    df_py = get_data_for_graph(p_salary_vs_other,
                               date_range=(start_date_py, end_date_py))
    df_savings_py = get_data_for_graph(p_savings_per_date,
                                       date_range=(start_date_py, end_date_py))

    # Extract relevant data
    tmp_data = get_revenue_expences_savings_year(df_cy, df_py, df_savings_cy, df_savings_py)
    revenues_cy, expenses_cy, savings_cy, revenues_py, expenses_py, savings_py = tmp_data

    # ##############
    # INDICATORS
    # ##############
    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=revenues_cy,
        title={
            "text": "Revenus"},
        delta={'reference': revenues_py},
        domain={'row': 0, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=expenses_cy,
        title={
            "text": "Dépenses"},
        delta={'reference': expenses_py,
               "decreasing": {'color': 'green'},
               "increasing": {'color': 'red'}
               },
        domain={'row': 0, 'column': 1}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=revenues_cy - expenses_cy,
        title={
            "text": "Gain"},
        delta={'reference': revenues_py - expenses_py},
        domain={'row': 0, 'column': 2}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=savings_cy,
        title={
            "text": "Epargne"},
        delta={'reference': savings_py},
        domain={'row': 0, 'column': 3}))

    figure.update_layout(
        grid={'rows': 1, 'columns': 4, 'pattern': "independent"},
        height=250  # px
    )

    return figure


def fig_expenses_vs_revenue(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_salary_vs_other, date_range=(start_date, end_date))
    df_savings = get_data_for_graph(p_savings_per_date, date_range=(start_date, end_date))

    # Remove savings transaction in the expenses and update balance
    if len(df_savings) > 0:
        df_merged = pd.merge(
            left=df,
            right=df_savings[['Balance', 'Mois']],
            how='outer',
            on="Mois",
            suffixes=('', '_savings')).fillna(0.0)
        df['Expenses'] = df_merged['Expenses'] - df_merged['Balance_savings']
        df['Balance'] = df_merged['Balance'] - df_merged['Balance_savings']

    if len(df) > 0:
        # Transform df
        df['Expenses'] = - df['Expenses']  # Negative becomes Positive
        df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

        # Figures
        figure = go.Figure()
        figure.add_trace(go.Bar(
            x=[MONTHS[i-1] for i in df['Mois']],
            y=df['Salaries'],
            name='Salaires'
            ))
        figure.add_trace(go.Bar(
            x=[MONTHS[i-1] for i in df['Mois']],
            y=df['Expenses'],
            name='Dépenses'
            ))
        figure.update_layout(
            xaxis=dict(tickformat="%b \n%Y"),
            title='Salaires VS Dépenses')
    else:
        figure = {}

    return figure


def fig_expenses_vs_category(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_balance_category_per_date, date_range=(start_date, end_date))

    if len(df) > 0:
        # Drop Revenue
        df = df[df['Categorie'] != 'Travail']

        # Rename empty category by 'None'
        df.loc[df['Categorie'].isna(), 'Categorie'] = 'None'

        # Rename months
        df['Mois'] = [MONTHS[i-1] for i in df['Mois']]

        figure = go.Figure()
        for i_cat in df['Categorie'].unique():
            figure.add_trace(go.Bar(
                x=df[df['Categorie'] == i_cat]['Mois'],
                y=df[df['Categorie'] == i_cat]['Balance'],
                name=i_cat,
                text=i_cat,
                hovertemplate='Catégorie: {}'.format(i_cat) +
                              '<br>Dépense: %{y:.2f}€' +
                              '<br>Mois: %{x}<extra></extra>'
                ))

        figure.update_layout(barmode='relative', title_text='Dépenses vs catégories')
        figure.update_yaxes(autorange="reversed")
        figure.update_traces(textposition='inside')
    else:
        figure = {}

    return figure


def fig_expenses_vs_occasion(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_balance_occasion_per_date, date_range=(start_date, end_date))

    if len(df) > 0:
        # Rename empty category by 'None'
        df.loc[df['Occasion'].isna(), 'Occasion'] = 'None'

        # Rename months
        df['Mois'] = [MONTHS[i-1] for i in df['Mois']]

        figure = go.Figure()
        for i_occ in OCCASIONS:
            figure.add_trace(go.Bar(
                x=df[df['Occasion'] == i_occ]['Mois'],
                y=df[df['Occasion'] == i_occ]['Balance'],
                name=i_occ,
                text=i_occ,
                hovertemplate='Occasion: {}'.format(i_occ) +
                              '<br>Dépense: %{y:.2f}€' +
                              '<br>Mois: %{x}<extra></extra>'
            ))

        figure.update_layout(barmode='relative', title_text='Dépenses vs occasions')
        figure.update_yaxes(autorange="reversed")
        figure.update_traces(textposition='inside')
    else:
        figure = {}

    return figure


def fig_savings(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_savings_per_date, date_range=(start_date, end_date))

    # Figures
    if len(df) > 0:

        # Format dataframe, rename month and sort by month
        df = format_df_saving(df)

        # Transform df
        df['Balance'] = -df['Balance']
        df['CumulativeBalance'] = df['Balance'].cumsum()
        df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign
        
        # Figures
        figure = make_subplots(specs=[[{"secondary_y": True}]])
        figure.add_trace(go.Bar(
            x=df['Mois'],
            y=df['Balance'],
            name='Epargne',
            marker_color=df['Color']
        ),
            secondary_y=False)
        figure.add_trace(go.Scatter(
            x=df['Mois'],
            y=df['CumulativeBalance'],
            mode='lines',
            line=dict(dash='dash', color='black'),
            name='Cumul.'
        ),
            secondary_y=True)

        figure.update_yaxes(title_text="Epargne", secondary_y=False)
        figure.update_yaxes(title_text="<b>Cumulative épargne</b>", secondary_y=True)
    else:
        figure = go.Figure()

    # Edit the layout
    figure.update_layout(
        title='Epargne',
        yaxis_showgrid=False,
        xaxis_title='Mois',
        yaxis_title='Euros')

    return figure


def fig_loan(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_loan_per_date, date_range=(start_date, end_date))

    # Figures
    if len(df) > 0:

        # Inverse expenses sign
        df['Balance'] = -df['Balance']

        # figure = px.line(df, x='date', y='Balance', markers=True)
        figure = go.Figure()
        figure.add_trace(
            go.Scatter(
                x=[MONTHS[i-1] for i in df['Mois']],
                y=df['Balance'],
                mode='lines+markers'))

        # Edit the layout
        figure.update_layout(
            title='Loyer / Prêt',
            xaxis_title='Mois',
            yaxis_title='Euros')
    else:
        figure = {}

    return figure


def fig_categories(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_expenses_category, date_range=(start_date, end_date))

    if len(df) > 0:
        # Adjust the data for the sunburst figure
        df['Somme'] = -df['Somme']
        df['Somme'] = df['Somme'].round(1)

        # Filter positive amount and remove Salary to get only expenses
        df_filter = df.copy()
        df_filter = df_filter[(df_filter['Somme'] >= 0) & (df_filter['Catégorie'] != 'Salaire')]
        # df_filter.loc[df['Sous-catégorie'] == "Internet/TV/Tel", ['Sous-catégorie']] = 'test'

        figure = px.sunburst(df_filter,
                             path=['Catégorie', 'Sous-catégorie'],
                             values='Somme',
                             title='Catégories')
        figure.update_traces(textinfo="label+percent entry",
                             hovertemplate="Labels=%{label}"
                                           "<br>Somme=%{value:.1}€"
                                           "<br>Parent=%{parent}"
                                           "<br>Percent=%{percentRoot:.0%}"
                             )
    else:
        figure = {}

    return figure


def fig_cum_balance(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_salary_vs_other, date_range=(start_date, end_date))
    df_savings = get_data_for_graph(p_savings_per_date, date_range=(start_date, end_date))

    # Remove savings transaction in the expenses and update balance
    if len(df_savings) > 0:
        df_merged = pd.merge(
            left=df,
            right=df_savings[['Balance', 'Mois']],
            how='outer',
            on="Mois",
            suffixes=('', '_savings')).fillna(0.0)
        df['Expenses'] = df_merged['Expenses'] - df_merged['Balance_savings']
        df['Balance'] = df_merged['Balance'] - df_merged['Balance_savings']

    if len(df) > 0:
        # Transform df
        df['CumulativeBalance'] = df['Balance'].cumsum()
        df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

        # Figures
        figure = make_subplots(specs=[[{"secondary_y": True}]])
        figure.add_trace(go.Bar(
            x=[MONTHS[i-1] for i in df['Mois']],
            y=df['Balance'],
            name='Gain',
            marker_color=df['Color']
            ),
            secondary_y=False)
        figure.add_trace(go.Scatter(
            x=[MONTHS[i-1] for i in df['Mois']],
            y=df['CumulativeBalance'],
            mode='lines',
            line=dict(dash='dash', color='black'),
            name='Cumul.'
            ),
            secondary_y=True)

        # Set titles
        figure.update_layout(
            xaxis=dict(tickformat="%b \n%Y"),
            yaxis_showgrid=False,
            title='Balance cumulée'
        )
        figure.update_yaxes(title_text="Balance", secondary_y=False)
        figure.update_yaxes(title_text="<b>Cumulative balance</b>", secondary_y=True)

    else:
        figure = {}

    return figure


def fig_nb_transactions_vs_category(year=datetime.datetime.now().year):

    end_date = datetime.datetime(year=year, month=12, day=31)
    start_date = datetime.datetime(year=year, month=1, day=1)

    # Get data
    df = get_data_for_graph(p_nb_transactions_per_category, date_range=(start_date, end_date))

    if len(df) > 0:

        # Rename empty category by 'None'
        df.loc[df['Categorie'].isna(), 'Categorie'] = 'None'

        # Sort by month
        df = df.sort_values(by=['Mois'])

        # Rename months
        df['Mois'] = [MONTHS[i-1] for i in df['Mois']]

        figure = go.Figure()
        for i_cat in df['Categorie'].unique():
            figure.add_trace(go.Bar(
                x=df[df['Categorie'] == i_cat]['Mois'],
                y=df[df['Categorie'] == i_cat]['nb_transactions'],
                name=i_cat,
                text=i_cat,
                hovertemplate='Catégorie: {}'.format(i_cat) +
                              '<br>Nombre: %{y}' +
                              '<br>Mois: %{x}<extra></extra>'
                ))

        figure.update_layout(barmode='relative', title_text='Nombre de transactions')
        figure.update_traces(textposition='inside')
    else:
        figure = {}

    return figure


if __name__ == '__main__':
    fig_expenses_vs_category()
