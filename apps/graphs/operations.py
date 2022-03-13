import datetime

from source.definitions import DB_CONN_TRANSACTION
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.exgest import TransactionExgest
from utils.mixed_utils import expand_columns_of_dataframe


def get_data_for_graph(pipeline, date_range=None):
    # Define DB connection
    connection = MongoDBConnection(DB_CONN_TRANSACTION)

    # Define pipeline
    if date_range:
        pipeline = add_date_condition_to_pipeline(
            pipeline,
            start_date=date_range[0],
            end_date=date_range[1])
    else:
        pipeline = pipeline

    # Extract data with defined pipeline
    transExgest = TransactionExgest(connection)
    transExgest.set_pipeline(pipeline)
    df = transExgest.exgest()

    # Transform df
    if len(df) > 0:
        df = expand_columns_of_dataframe(df, column='_id')  # Expand ID to get date
        df['date'] = [datetime.datetime(int(row['Année']), int(row['Mois']), 1) for _, row in df.iterrows()]  # convert in datetime
        df.sort_values(by='date', inplace=True)

    return df


def add_date_condition_to_pipeline(pipeline, start_date, end_date):

    date_condition = {
        '$match': {
            'date.dt': {
                '$gte': start_date,
                '$lte': end_date}
        },
    }
    pipeline.insert(0, date_condition)

    return pipeline

