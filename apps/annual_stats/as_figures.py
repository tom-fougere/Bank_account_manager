import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from apps.annual_stats.as_operations import get_data_for_graph
from apps.annual_stats.as_pipelines import p_balance_category_per_date,\
    p_balance_occasion_per_date, p_savings_per_date, p_loan_per_date, p_salary_vs_other, p_expenses_category
from source.categories import OCCASIONS


def fig_indicators_revenue_expense_balance():

    # Get data
    df_current_year = get_data_for_graph(p_salary_vs_other)

    if len(df_current_year) > 0:
        revenues = df_current_year['Revenues'].sum()
        expenses = -df_current_year['Expenses'].sum()
    else:
        revenues = 0
        expenses = 0

    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number",
        value=revenues,
        title={
            "text": "Revenus"},
        domain={'row': 0, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number",
        value=expenses,
        title={
            "text": "Dépenses"},
        domain={'row': 0, 'column': 1}))
    figure.add_trace(go.Indicator(
        mode="number",
        value=revenues - expenses,
        title={
            "text": "Gain"},
        domain={'row': 0, 'column': 2}))

    figure.update_layout(
        grid={'rows': 1, 'columns': 3, 'pattern': "independent"},
        height=250  # px
    )

    return figure


def fig_expenses_vs_revenue():

    # Get data
    df = get_data_for_graph(p_salary_vs_other)

    if len(df) > 0:
        # Transform df
        df['Expenses'] = - df['Expenses']  # Negative becomes Positive
        df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

        # Figures
        figure = go.Figure()
        figure.add_trace(go.Bar(
            x=df['Année'],
            y=df['Revenues'],
            name='Revenus'
            ))
        figure.add_trace(go.Bar(
            x=df['Année'],
            y=df['Expenses'],
            name='Dépenses'
            ))
        figure.update_layout(
            title='Revenus VS Dépenses')
    else:
        figure = {}

    return figure


def fig_expenses_vs_category():

    # Get data
    df = get_data_for_graph(p_balance_category_per_date)

    # Drop Revenue
    df = df[df['Categorie'] != 'Travail']

    # Rename empty category by 'None'
    df.loc[df['Categorie'].isna(), 'Categorie'] = 'None'

    figure = go.Figure()
    for i_cat in df['Categorie'].unique():
        figure.add_trace(go.Bar(
            x=df[df['Categorie'] == i_cat]['Année'],
            y=df[df['Categorie'] == i_cat]['Balance'],
            name=i_cat,
            text=i_cat,
            hovertemplate='Catégorie: {}'.format(i_cat) +
                          '<br>Dépense: %{y:.2f}€<extra></extra>'
            ))

    figure.update_layout(barmode='relative', title_text='Dépenses vs catégories')
    figure.update_yaxes(autorange="reversed")
    figure.update_traces(textposition='inside')

    return figure


def fig_expenses_vs_occasion():

    # Get data
    df = get_data_for_graph(p_balance_occasion_per_date)

    # Rename empty category by 'None'
    df.loc[df['Occasion'].isna(), 'Occasion'] = 'None'

    figure = go.Figure()
    for i_occ in OCCASIONS:
        figure.add_trace(go.Bar(
            x=df[df['Occasion'] == i_occ]['Année'],
            y=df[df['Occasion'] == i_occ]['Balance'],
            name=i_occ,
            text=i_occ,
            hovertemplate='Occasion: {}'.format(i_occ) +
                          '<br>Dépense: %{y:.2f}€<extra></extra>'
        ))

    figure.update_layout(barmode='relative', title_text='Dépenses vs occasions')
    figure.update_yaxes(autorange="reversed")
    figure.update_traces(textposition='inside')

    return figure


def fig_savings():

    # Get data
    df = get_data_for_graph(p_savings_per_date)

    # Figures
    if len(df) > 0:

        # Transform df
        df['CumulativeBalance'] = df['Balance'].cumsum()
        df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign
        
        # Figures
        figure = make_subplots(specs=[[{"secondary_y": True}]])
        figure.add_trace(go.Bar(
            x=df['Année'],
            y=df['Balance'],
            name='Epargne',
            marker_color=df['Color']
        ),
            secondary_y=False)
        figure.add_trace(go.Scatter(
            x=df['Année'],
            y=df['CumulativeBalance'],
            mode='lines',
            line=dict(dash='dash', color='black'),
            name='Cumulative épargne'
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
        xaxis_title='Année',
        yaxis_title='Euros')

    return figure


def fig_loan():

    # Get data
    df = get_data_for_graph(p_loan_per_date)

    # Figures
    if len(df) > 0:

        # Inverse expenses sign
        df['Balance'] = -df['Balance']

        figure = go.Figure()
        figure.add_trace(
            go.Scatter(
                x=df['Année'],
                y=df['Balance'],
                mode='lines+markers'))

        # Edit the layout
        figure.update_layout(
            title='Loyer / Prêt',
            xaxis_title='Année',
            yaxis_title='Euros')
    else:
        figure = {}

    return figure


def fig_cum_balance():

    # Get data
    df = get_data_for_graph(p_salary_vs_other)

    # Transform df
    df['CumulativeBalance'] = df['Balance'].cumsum()
    df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign

    # Figures
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(go.Bar(
        x=df['Année'],
        y=df['Balance'],
        name='Gain',
        marker_color=df['Color']
        ),
        secondary_y=False)
    figure.add_trace(go.Scatter(
        x=df['Année'],
        y=df['CumulativeBalance'],
        mode='lines',
        line=dict(dash='dash', color='black'),
        name='Cumulative gain'
        ),
        secondary_y=True)

    # Set titles
    figure.update_layout(
        yaxis_showgrid=False,
        title='Balance cumulée'
    )
    figure.update_yaxes(title_text="Balance", secondary_y=False)
    figure.update_yaxes(title_text="<b>Cumulative balance</b>", secondary_y=True)

    return figure


if __name__ == '__main__':
    fig_expenses_vs_category()
