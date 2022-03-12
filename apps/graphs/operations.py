import datetime

from source.definitions import DB_CONN_TRANSACTION
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.exgest import TransactionExgest
from utils.mixed_utils import expand_columns_of_dataframe


def get_data_for_graph(pipeline):
    # Define DB connection
    connection = MongoDBConnection(DB_CONN_TRANSACTION)

    # Extract data with defined pipeline
    pipeline = pipeline
    transExgest = TransactionExgest(connection)
    transExgest.set_pipeline(pipeline)
    df = transExgest.exgest()

    # Transform df
    df = expand_columns_of_dataframe(df, column='_id')  # Expand ID to get date
    df['date'] = [datetime.datetime(int(row['Année']), int(row['Mois']), 1) for _, row in df.iterrows()]  # convert in datetime
    df.sort_values(by='date', inplace=True)

    return df
