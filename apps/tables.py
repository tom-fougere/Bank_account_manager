import pandas as pd
import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme
from source.definitions import InfoName, INFO_RENAMING, InfoDisplay


# #################################### #
# ########### CONDITIONS ############# #
# #################################### #

COND_WIDTH = [
    {'if': {'column_id': INFO_RENAMING[InfoName.DATE_BANK_STR]},
     'minWidth': '140px', 'width': '140px', 'maxWidth': '140px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.AMOUNT]},
     'minWidth': '120px', 'width': '120px', 'maxWidth': '120px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.DESCRIPTION]},
     'minWidth': '350px', 'width': '350px', 'maxWidth': '350px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.CATEGORY]},
     'minWidth': '140px', 'width': '140px', 'maxWidth': '140px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.SUB_CATEGORY]},
     'minWidth': '200px', 'width': '200px', 'maxWidth': '200px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.OCCASION]},
     'minWidth': '90px', 'width': '90px', 'maxWidth': '90px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.CHECK]},
     'minWidth': '90px', 'width': '90px', 'maxWidth': '90px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.NOTE]},
     'minWidth': '250px', 'width': '250px', 'maxWidth': '250px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.TYPE]},
     'minWidth': '110px', 'width': '110px', 'maxWidth': '110px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.DATE_TRANS_STR]},
     'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.DATE_BANK]},
     'minWidth': '130px', 'width': '130px', 'maxWidth': '130px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.DATE_TRANS]},
     'minWidth': '130px', 'width': '130px', 'maxWidth': '130px'},
    {'if': {'column_id': INFO_RENAMING[InfoName.DUPLICATE]},
     'minWidth': '100px', 'width': '100px', 'maxWidth': '100px'},
]


# #################################### #
# ########### FUNCTIONS ############## #
# #################################### #

def format_dataframe(df, columns=InfoDisplay.ALL):

    # Drop useless columns
    new_df = df.drop(columns=[InfoName.ID])

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
    for key in INFO_RENAMING:
        if key in df_keys:
            df.rename(columns={key: INFO_RENAMING[key]}, inplace=True)


def df_to_datatable(df):

    # Create columns for datatable
    columns = [{"name": i, "id": i, } for i in df.columns]

    # Format the amount field to numeric value
    for idx, column in enumerate(columns):
        if column['name'] == INFO_RENAMING[InfoName.AMOUNT]:
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
