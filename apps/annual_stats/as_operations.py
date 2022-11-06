import datetime

from source.definitions import DB_CONN_TRANSACTION
from source.data_ingestion.exgest import TransactionExgest
from utils.mixed_utils import expand_columns_of_dataframe


def get_data_for_graph(pipeline):

    # Extract data with defined pipeline
    transExgest = TransactionExgest(DB_CONN_TRANSACTION)
    transExgest.set_pipeline(pipeline)
    df = transExgest.exgest()

    # Transform df
    if len(df) > 0:
        df = expand_columns_of_dataframe(df, column='_id')  # Expand ID to get date

    return df


def get_list_years(name_db_connection):
    data_extractor = TransactionExgest(name_db_connection)
    distinct_years = data_extractor.get_distinct_years()

    dropdown_list_years = [
        {'label': str(year), 'value': year}
        for year in distinct_years
    ]

    return dropdown_list_years
