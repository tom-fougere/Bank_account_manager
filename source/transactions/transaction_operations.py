import pandas as pd
from dash_table.Format import Format, Symbol, Scheme
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.metadata import MetadataDB

MANDATORY_COLUMNS = ['date_str', 'amount', 'description', 'type_transaction', 'date_transaction_str']
OPTIONAL_COLUMNS = {'new_data': ['duplicate'],
                    'category': ['category', 'sub_category']}
COLUMNS_RENAMING = {'date_str': 'Date (banque)',
                    'amount': 'Montant (€)',
                    'description': 'Libelé',
                    'type_transaction': 'Type',
                    'date_transaction_str': 'Date',
                    'duplicate': 'Duplicata',
                    'category': 'Catégorie',
                    'sub_category': 'Sous-catégorie'}


def check_duplicates_in_df(df1, df2):

    # Init duplicate column to False
    df1['duplicate'] = False

    if len(df2) > 0:
        for index, row in df1.iterrows():
            # Check if the same transaction exists
            df2_same = df2.loc[(df2['account_id'] == row['account_id']) &
                               (df2['amount'] == row['amount']) &
                               (df2['date_str'] == row['date_str']) &
                               (df2['date_transaction_str'] == row['date_transaction_str']) &
                               (df2['description'] == row['description'])].reset_index()

            # If transaction exists, replace values of some columns and set 'duplicate' to True
            if len(df2_same) == 1:
                column_to_copy = ['category', 'sub_category', 'occasion', 'note', 'check', 'type_transaction']
                for column in column_to_copy:
                    df1.loc[index, column] = df2_same[column][0]
                df1.loc[index, 'duplicate'] = True
            elif len(df2_same) > 1:
                raise ValueError('WARNING')


def format_dataframe_to_datatable(df, show_new_data=False, show_category=False):
    # keep selected columns
    df_display = keep_selected_columns(df, show_new_data, show_category)

    # rename columns
    rename_columns(df_display)

    # Format to numeric the amount
    columns = [{"name": i, "id": i, } for i in df_display.columns]
    for idx, column in enumerate(columns):
        if column['name'] == 'Montant (€)':
            columns[idx]['type'] = 'numeric'
            columns[idx]['format'] = Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('€')

    return df_display, columns


def keep_selected_columns(df, show_new_data=False, show_category=False):

    new_df = pd.DataFrame()

    columns_to_keep = MANDATORY_COLUMNS.copy()
    if show_new_data:
        columns_to_keep += OPTIONAL_COLUMNS['new_data'].copy()
    if show_category:
        columns_to_keep += OPTIONAL_COLUMNS['category'].copy()

    keys = df.keys()
    for column in columns_to_keep:
        if column in keys:
            new_df[column] = df[column].copy()

    return new_df


def rename_columns(df):

    df_keys = df.keys()
    for key in COLUMNS_RENAMING:
        if key in df_keys:
            df.rename(columns={key: COLUMNS_RENAMING[key]}, inplace=True)


def get_categories(db_connection, account_id):

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    categories = metadata_db.get_categories(account_id=account_id)

    list_categories = []
    for category in categories:
        list_categories.append({'label': category, 'value': category})

    return list_categories


def get_sub_categories(db_connection, account_id, categories, add_suffix_cat=True):

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    list_sub_categories = []
    for category in categories:
        sub_categories = metadata_db.get_sub_categories(account_id=account_id, category=category)
        for sub_category in sub_categories:
            if add_suffix_cat:
                list_sub_categories.append({'label': f'{category}/{sub_category}',
                                            'value': f'{category}/{sub_category}'})
            else:
                list_sub_categories.append({'label': f'{sub_category}',
                                            'value': f'{sub_category}'})

    return list_sub_categories


def get_occasion(db_connection, account_id):

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    occasions = metadata_db.get_occasions(account_id=account_id)

    list_occasions = []
    for occas in occasions:
        list_occasions.append({'label': occas, 'value': occas})

    return list_occasions


def get_type_transaction(db_connection, account_id):

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    types = metadata_db.get_types_transaction(account_id=account_id)

    list_types = []
    for type in types:
        list_types.append({'label': type, 'value': type})

    return list_types