from source.definitions import DB_CONN_TRANSACTION
from source.transactions.exgest import TransactionExgest, exgest_with_pipeline


def get_data_for_graph(pipeline):

    # Extract data with defined pipeline
    df = exgest_with_pipeline(
        db_connection=DB_CONN_TRANSACTION,
        pipeline=pipeline,
    )

    # Transform df
    if len(df) > 0:
        if 'Année' in df.keys():
            df.sort_values(by='Année', inplace=True)

    # Reset index and remove index column
    df.reset_index(inplace=True)
    df.drop(columns=['index'], axis=1, inplace=True)

    return df


def get_list_years(name_db_connection):
    data_extractor = TransactionExgest(name_db_connection)
    distinct_years = data_extractor.get_distinct_years()

    dropdown_list_years = [
        {'label': str(year), 'value': year}
        for year in distinct_years
    ]

    return dropdown_list_years
