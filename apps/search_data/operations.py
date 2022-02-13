import dash_table as dt

from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.metadata import MetadataDB
from source.data_ingestion.exgest import TransactionExgest
from source.transactions.transaction_operations import format_dataframe_to_datatable

style_cell_conditional = (
        [
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in ['Libelé', 'Type']
        ] +
        [
            {
                'if': {'column_id': c},
                'textAlign': 'center'
            } for c in ['Date', 'Date (banque)']
        ]
)

style_data_conditional = (
    [
        {
            'if': {
                'filter_query': '{Duplicata} eq "True"'
            },
            'backgroundColor': '#DAE8FE'
        },
        {
            'if': {
                'column_id': 'Montant (€)',
                'filter_query': '{Montant (€)} > 0'
            },
            'backgroundColor': '#B5EEB6'
        }
    ]
)


def search_transactions(connection_name, filter):
    db_connection = MongoDBConnection(connection_name)

    # Init
    searches = dict()

    # Keep only when it's not None and the list isn"t empty
    for key in filter:
        if isinstance(filter[key], list):
            if len(filter[key]) > 0 and all(x is not None for x in filter[key]):
                searches[key] = filter[key]
        elif filter[key] is not None:
            searches[key] = filter[key]

    data_extractor = TransactionExgest(db_connection, dict_searches=searches)
    return data_extractor.exgest()


def get_categories(db_connection, account_id):

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    categories = metadata_db.get_categories(account_id=account_id)

    list_categories = []
    for category in categories:
        list_categories.append({'label': category, 'value': category})

    return list_categories


def get_sub_categories(db_connection, account_id, categories):

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    list_sub_categories = []
    for category in categories:
        sub_categories = metadata_db.get_sub_categories(account_id=account_id, category=category)
        for sub_category in sub_categories:
            list_sub_categories.append({'label': f'{category}/{sub_category}',
                                        'value': f'{category}/{sub_category}'})

    return list_sub_categories


def get_occasion(db_connection, account_id):

    my_connection = MongoDBConnection(db_connection)
    metadata_db = MetadataDB(my_connection)

    occasions = metadata_db.get_occasions(account_id=account_id)

    list_occasions = []
    for occas in occasions:
        list_occasions.append({'label': occas, 'value': occas})

    return list_occasions


def create_datatable(df):
    df_display, columns = format_dataframe_to_datatable(df, show_new_data=True, show_category=False)

    dt_transactions = dt.DataTable(id='table_content',
                                   data=df_display.to_dict('records'),
                                   columns=columns,
                                   column_selectable="single",
                                   selected_columns=[],
                                   selected_rows=[],
                                   style_data_conditional=style_data_conditional,
                                   style_cell_conditional=style_cell_conditional,
                                   style_header={
                                       'backgroundColor': 'rgb(210, 210, 210)',
                                       'color': 'black',
                                       'fontWeight': 'bold'
                                   })
    return dt_transactions
