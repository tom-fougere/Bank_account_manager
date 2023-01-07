from source.transactions.metadata import MetadataDB
from source.transactions.exgest import TransactionExgest


# ##################################### #
# ########### DROPDOWN MENU ########### #
# ##################################### #

def get_categories_for_dropdown_menu(db_connection, account_id):

    metadata_db = MetadataDB(db_connection, account_id=account_id)
    metadata_db.set_from_db()

    categories = metadata_db.get_list_categories()

    list_categories = []
    for category in categories:
        list_categories.append({'label': category, 'value': category})

    return list_categories


def get_sub_categories_for_dropdown_menu(db_connection, account_id, categories, add_suffix_cat=True):

    metadata_db = MetadataDB(db_connection, account_id=account_id)
    metadata_db.set_from_db()

    list_sub_categories = []
    for category in categories:
        sub_categories = metadata_db.get_list_subcategories(category=category)
        for sub_category in sub_categories:
            if add_suffix_cat:
                list_sub_categories.append({'label': f'{category}:{sub_category}',
                                            'value': f'{category}:{sub_category}'})
            else:
                list_sub_categories.append({'label': f'{sub_category}',
                                            'value': f'{sub_category}'})

    return list_sub_categories


def get_categories_and_sub_for_dropdown_menu(db_connection, account_id, delimiter=':'):

    metadata_db = MetadataDB(
        name_connection=db_connection,
        account_id=account_id)
    metadata_db.set_from_db()
    categories = metadata_db.get_list_categories()

    list_sub_categories = []
    for category in categories:
        for sub_category in metadata_db.get_list_subcategories(category):
            list_sub_categories.append({'label': f'{category}{delimiter}{sub_category}',
                                        'value': f'{category}{delimiter}{sub_category}'})

    return list_sub_categories


def get_occasions_for_dropdown_menu(db_connection, account_id):

    metadata_db = MetadataDB(db_connection, account_id=account_id)
    metadata_db.set_from_db()

    list_occasions = []
    for occas in metadata_db.occasions:
        list_occasions.append({'label': occas, 'value': occas})

    return list_occasions


def get_types_transaction_for_dropdown_menu(db_connection, account_id):

    metadata_db = MetadataDB(db_connection, account_id=account_id)
    metadata_db.set_from_db()

    list_types = []
    for trans_type in metadata_db.types_transaction:
        list_types.append({'label': trans_type, 'value': trans_type})

    return list_types


def get_list_years_for_dropdown_menu(name_db_connection):
    data_extractor = TransactionExgest(name_db_connection)
    distinct_years = data_extractor.get_distinct_years()

    dropdown_list_years = [
        {'label': str(year), 'value': year}
        for year in distinct_years
    ]

    return dropdown_list_years
