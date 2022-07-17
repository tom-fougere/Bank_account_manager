import pandas as pd
import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme


# #################################### #
# ########## DEFINITION ############## #
# #################################### #

class ColumnsName:
    ID = '_id'
    DATE_BANK_STR = 'date_str'
    DATE_BANK = 'date'
    AMOUNT = 'amount'
    DESCRIPTION = 'description'
    TYPE = 'type_transaction'
    DATE_TRANS_STR = 'date_transaction_str'
    DATE_TRANS = 'date_transaction'
    CATEGORY = 'category'
    SUB_CATEGORY = 'sub_category'
    OCCASION = 'occasion'
    CHECK = 'check'
    NOTE = 'note'
    DUPLICATE = 'duplicate'


class ColumnsDisplay:
    ALL = [
        ColumnsName.DATE_BANK_STR,
        ColumnsName.AMOUNT,
        ColumnsName.DESCRIPTION,
        ColumnsName.CATEGORY,
        ColumnsName.SUB_CATEGORY,
        ColumnsName.OCCASION,
        ColumnsName.CHECK,
        ColumnsName.NOTE,
        ColumnsName.TYPE,
        ColumnsName.DATE_TRANS_STR,
        ColumnsName.DATE_BANK,
        ColumnsName.DATE_TRANS,
        ColumnsName.DUPLICATE,
    ]
    SEARCH = [
        ColumnsName.DATE_BANK_STR,
        ColumnsName.AMOUNT,
        ColumnsName.DESCRIPTION,
        ColumnsName.CATEGORY,
        ColumnsName.SUB_CATEGORY,
        ColumnsName.OCCASION,
        ColumnsName.CHECK,
        ColumnsName.NOTE,
        ColumnsName.TYPE,
        ColumnsName.DATE_TRANS_STR,
    ]
    IMPORT = [
        ColumnsName.DATE_BANK_STR,
        ColumnsName.AMOUNT,
        ColumnsName.DESCRIPTION,
        ColumnsName.TYPE,
        ColumnsName.DATE_TRANS_STR,
        ColumnsName.DUPLICATE,
    ]


COLUMNS_RENAMING = {
    ColumnsName.DATE_BANK_STR: 'Date (banque)',
    ColumnsName.AMOUNT: 'Montant (€)',
    ColumnsName.DESCRIPTION: 'Libelé',
    ColumnsName.CATEGORY: 'Catégorie',
    ColumnsName.SUB_CATEGORY: 'Sous-catégorie',
    ColumnsName.OCCASION: 'Occasion',
    ColumnsName.CHECK: 'Pointage',
    ColumnsName.NOTE: 'Note',
    ColumnsName.TYPE: 'Type',
    ColumnsName.DATE_TRANS_STR: 'Date',
    ColumnsName.DATE_BANK: 'Date (banque)',
    ColumnsName.DATE_TRANS: 'Date',
    ColumnsName.DUPLICATE: 'Duplicata',
}


# #################################### #
# ########### CONDITIONS ############# #
# #################################### #
X = {'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',}

COND_WIDTH = [
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.DATE_BANK_STR]},
     'minWidth': '140px', 'width': '140px', 'maxWidth': '140px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.AMOUNT]},
     'minWidth': '120px', 'width': '120px', 'maxWidth': '120px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.DESCRIPTION]},
     'minWidth': '350px', 'width': '350px', 'maxWidth': '350px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.CATEGORY]},
     'minWidth': '140px', 'width': '140px', 'maxWidth': '140px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.SUB_CATEGORY]},
     'minWidth': '200px', 'width': '200px', 'maxWidth': '200px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.OCCASION]},
     'minWidth': '90px', 'width': '90px', 'maxWidth': '90px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.CHECK]},
     'minWidth': '90px', 'width': '90px', 'maxWidth': '90px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.NOTE]},
     'minWidth': '250px', 'width': '250px', 'maxWidth': '250px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.TYPE]},
     'minWidth': '110px', 'width': '110px', 'maxWidth': '110px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.DATE_TRANS_STR]},
     'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.DATE_BANK]},
     'minWidth': '130px', 'width': '130px', 'maxWidth': '130px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.DATE_TRANS]},
     'minWidth': '130px', 'width': '130px', 'maxWidth': '130px'},
    {'if': {'column_id': COLUMNS_RENAMING[ColumnsName.DUPLICATE]},
     'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
]


# #################################### #
# ########### FUNCTIONS ############## #
# #################################### #

def format_dataframe(df, columns=ColumnsDisplay.ALL):

    # Drop useless columns
    new_df = df.drop(columns=[ColumnsName.ID])

    # Filter wanted columns
    new_df = filter_columns(new_df, columns_name=columns)

    # Rename columns
    rename_columns(new_df)

    return new_df


def filter_columns(df, columns_name):

    new_df = pd.DataFrame()

    keys = df.keys()
    for column in columns_name:
        if column in keys:
            new_df[column] = df[column].copy()

    return new_df


def rename_columns(df):

    df_keys = df.keys()
    for key in COLUMNS_RENAMING:
        if key in df_keys:
            df.rename(columns={key: COLUMNS_RENAMING[key]}, inplace=True)


def df_to_datatable(df):

    # Create columns for datatable
    columns = [{"name": i, "id": i, } for i in df.columns]

    # Format the amount field to numeric value
    for idx, column in enumerate(columns):
        if column['name'] == COLUMNS_RENAMING[ColumnsName.AMOUNT]:
            columns[idx]['type'] = 'numeric'
            columns[idx]['format'] = Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('€')

    # Create datatable
    dt_transactions = dt.DataTable(
        id='cell_search',
        data=df.to_dict('records'),
        columns=columns,
        column_selectable="single",
        selected_columns=[],
        selected_rows=[],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'padding-left': '0px',
        },
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'padding-left': '10px',
        },
        style_table={'overflowX': 'auto'},  # Horizontal scroll
        sort_action="native",
        editable=False,
        style_cell_conditional=COND_WIDTH,
    )

    return dt_transactions
