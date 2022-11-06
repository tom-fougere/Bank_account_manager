import pandas as pd
import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme
from source.definitions import InfoName, INFO_RENAMING, InfoDisplay


# #################################### #
# ########### CONDITIONS ############# #
# #################################### #

COND_COLUMN_WIDTH = [
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

COND_STYLE_CELL = (
        [
            {
                'if': {'column_id': c},
                'textAlign': 'left'
            } for c in [INFO_RENAMING[InfoName.DESCRIPTION]]
        ] +
        [
            {
                'if': {'column_id': c},
                'textAlign': 'center'
            } for c in [INFO_RENAMING[InfoName.DATE_BANK_STR],
                        INFO_RENAMING[InfoName.DATE_TRANS_STR]]
        ]
)


COND_STYLE_DATA = (
    [
        {
            'if': {
                'filter_query': '{{{}}} eq "Oui"'.format(INFO_RENAMING[InfoName.DUPLICATE])
            },
            'backgroundColor': '#DAE8FE'
        },
        {
            'if': {
                'column_id': INFO_RENAMING[InfoName.AMOUNT],
                'filter_query': '{{{}}} > 0'.format(INFO_RENAMING[InfoName.AMOUNT])
            },
            'backgroundColor': '#B5EEB6'
        },
        {
            'if': {
                'column_id': INFO_RENAMING[InfoName.CHECK],
                'filter_query': '{{{}}} eq "Non"'.format(INFO_RENAMING[InfoName.CHECK])
            },
            'backgroundColor': '#FFE9E9'
        },
    ]
)


# #################################### #
# ########### FUNCTIONS ############## #
# #################################### #

def format_dataframe(df, columns=InfoDisplay.ALL):

    # Drop useless columns
    if InfoName.ID in df.keys():
        new_df = df.drop(columns=[InfoName.ID])
    else:
        new_df = df.copy()

    # Filter wanted columns
    new_df = filter_columns(new_df, columns_name=columns)

    # Change boolean values by string
    new_df = format_boolean_information(new_df)

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


def format_boolean_information(df):

    if InfoName.DUPLICATE in df.keys():
        df[InfoName.DUPLICATE] = df[InfoName.DUPLICATE].apply(lambda x: 'Oui' if x == 'True' else 'Non')

    if InfoName.CHECK in df.keys():
        df[InfoName.CHECK] = df[InfoName.CHECK].apply(lambda x: 'Oui' if x is True else 'Non')

    return df


def df_to_datatable(df, table_id):

    # Create columns for datatable
    columns = [{"name": i, "id": i, } for i in df.columns]

    # Format the amount field to numeric value
    for idx, column in enumerate(columns):
        if column['name'] == INFO_RENAMING[InfoName.AMOUNT]:
            columns[idx]['type'] = 'numeric'
            columns[idx]['format'] = Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('€')

    # Create datatable
    dt_transactions = dt.DataTable(
        id=table_id,
        data=df.to_dict('records'),
        columns=columns,
        selected_columns=[],
        selected_rows=[],
        style_header={
            'backgroundColor': 'rgb(210, 210, 210)',
            'color': 'black',
            'fontWeight': 'bold',
            'padding-left': '0px',
            'textAlign': 'center',
        },
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'padding-left': '10px',
        },
        style_table={'overflowX': 'auto'},  # Horizontal scroll
        sort_action="native",
        editable=False,
        style_cell_conditional=COND_COLUMN_WIDTH + COND_STYLE_CELL,
        style_data_conditional=COND_STYLE_DATA,
    )

    return dt_transactions
