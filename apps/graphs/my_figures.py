import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

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
    df['Total_negative'] = - df['Total_negative']
    df = expand_columns_of_dataframe(df, column='_id')
    df['date'] = [datetime.datetime(int(row['Année']), int(row['Mois']), 1) for _, row in df.iterrows()]
    df.sort_values(by='date', inplace=True)

    figure = go.Figure()
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Total_positive'],
        name='Gains'
    ))
    figure.add_trace(go.Bar(
        x=df['date'],
        y=df['Total_negative'],
        name='Dépenses'
    ))
    figure.update_layout(xaxis=dict(tickformat="%b \n%Y"))

    return figure


if __name__ == '__main__':
    fig_expenses_vs_gain()
