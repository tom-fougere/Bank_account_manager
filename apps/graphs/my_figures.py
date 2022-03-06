import numpy as np
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from source.definitions import DB_CONN_TRANSACTION
from source.db_connection.db_access import MongoDBConnection
from apps.graphs.pipelines import p_expenses_gains_per_date
from source.data_ingestion.exgest import TransactionExgest
from utils.mixed_utils import expand_columns_of_dataframe


def fig_expenses_vs_gain():

    # Define DB connection
    connection = MongoDBConnection(DB_CONN_TRANSACTION)

    # Extract data with defined pipeline
    pipeline = p_expenses_gains_per_date
    transExgest = TransactionExgest(connection)
    transExgest.set_pipeline(pipeline)
    df = transExgest.exgest()

    # Transform df
    df = expand_columns_of_dataframe(df, column='_id')  # Expand ID to get date
    df['date'] = [datetime.datetime(int(row['Année']), int(row['Mois']), 1) for _, row in df.iterrows()]  # convert in datetime
    df['Total_negative'] = - df['Total_negative']  # Negative becomes Positive
    df["Color"] = np.where(df["Balance"] < 0, '#EF553B', '#636EFA')  # Change color following sign
    df.sort_values(by='date', inplace=True)

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


if __name__ == '__main__':
    fig_expenses_vs_gain()
