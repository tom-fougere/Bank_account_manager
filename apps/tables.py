import pandas as pd
import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme
from source.definitions import ColumnsName, COLUMNS_RENAMING, ColumnsDisplay


# #################################### #
# ########### CONDITIONS ############# #
# #################################### #

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
