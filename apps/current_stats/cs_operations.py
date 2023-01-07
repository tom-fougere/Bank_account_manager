import datetime
from pandas import Categorical

from source.definitions import DB_CONN_TRANSACTION, MONTHS
from source.transactions.exgest import TransactionExgest
from utils.mixed_utils import expand_columns_of_dataframe


def get_data_for_graph(pipeline, date_range=None):

    # Define pipeline
    if date_range:
        pipeline = add_date_condition_to_pipeline(
            pipeline,
            start_date=date_range[0],
            end_date=date_range[1])
    else:
        pipeline = pipeline

    # Extract data with defined pipeline
    transExgest = TransactionExgest(DB_CONN_TRANSACTION)
    transExgest.set_pipeline(pipeline)
    df = transExgest.exgest()

    # Transform df
    if len(df) > 0:
        df = expand_columns_of_dataframe(df, column='_id')  # Expand ID to get date

        if ('Année' in df.keys()) and ('Mois' in df.keys()):
            df['date'] = [datetime.datetime(int(row['Année']), int(row['Mois']), 1) for _, row in df.iterrows()]  # convert in datetime
            df.sort_values(by='date', inplace=True)

    return df


def add_date_condition_to_pipeline(pipeline, start_date, end_date):

    pip = pipeline.copy()

    date_condition = {
        '$match': {
            'date.dt': {
                '$gte': start_date,
                '$lte': end_date}
        },
    }
    pip.insert(0, date_condition)

    return pip


def format_df_saving(df):

    # Change month index by its name
    df['Mois'] = df['Mois'].apply(lambda x: MONTHS[x - 1])

    # Add all others months to dataframe
    for mois in MONTHS:
        if mois not in df['Mois'].tolist():
            new_row = {
                'Balance': 0,
                'Mois': mois,
                'Année': None,
                'date': None,
            }
            df = df.append(new_row, ignore_index=True)

    # Sort dataframe by month
    df['Month_cat'] = Categorical(
        df['Mois'],
        categories=MONTHS,
        ordered=True
    )
    df.sort_values('Month_cat', inplace=True)
    df.drop(['Month_cat'], axis=1, inplace=True)

    return df
