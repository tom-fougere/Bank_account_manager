import datetime
from pandas import Categorical

from source.definitions import DB_CONN_TRANSACTION, MONTHS
from source.transactions.exgest import exgest_with_pipeline


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
    df = exgest_with_pipeline(
        db_connection=DB_CONN_TRANSACTION,
        pipeline=pipeline,
    )

    # Transform df
    if len(df) > 0:
        if ('Année' in df.keys()) and ('Mois' in df.keys()):
            df['date'] = [datetime.datetime(int(row['Année']), int(row['Mois']), 1) for _, row in df.iterrows()]  # convert in datetime
            df.sort_values(by='date', inplace=True)

    # Reset index and remove index column
    df.reset_index(inplace=True)
    df.drop(columns=['index'], axis=1, inplace=True)

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


def get_revenue_expences_savings_year(
        df_current_year, df_previous_year, df_savings_current_year, df_savings_previous_year):

    # CURRENT YEAR
    if len(df_current_year) > 0:
        revenues_current_year = df_current_year['Salaries'].sum()
        expenses_current_year = -df_current_year['Expenses'].sum()
    else:
        revenues_current_year = 0
        expenses_current_year = 0

    if len(df_savings_current_year) > 0:
        savings_current_year = -df_savings_current_year['Balance'].sum()
    else:
        savings_current_year = 0

    # PREVIOUS YEAR
    if len(df_previous_year) > 0:
        revenues_previous_year = df_previous_year['Salaries'].sum()
        expenses_previous_year = -df_previous_year['Expenses'].sum()
    else:
        revenues_previous_year = 0
        expenses_previous_year = 0

    if len(df_savings_previous_year) > 0:
        savings_previous_year = -df_savings_previous_year['Balance'].sum()
    else:
        savings_previous_year = 0

    return (revenues_current_year, expenses_current_year, savings_current_year,
            revenues_previous_year, expenses_previous_year, savings_previous_year)