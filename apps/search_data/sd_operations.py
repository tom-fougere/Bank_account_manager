import dash_table as dt

from source.transactions.exgest import TransactionExgest
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


def search_transactions(connection_name, filters):

    # Init
    searches = dict()

    for filter_name in filters.keys():
        filter_enable, condition = filters[filter_name]
        if filter_enable:
            if isinstance(condition, list) and (len(condition) == 0 or (not any(condition))):
                searches[filter_name] = None
            else:
                searches[filter_name] = condition

    data_extractor = TransactionExgest(connection_name)
    data_extractor.set_search_criteria(dict_searches=searches)

    df_transaction = data_extractor.exgest()

    # Sort by date
    if len(df_transaction) > 0:
        df_transaction = df_transaction.sort_values(by='date_dt', ascending=False)

    return df_transaction


def create_datatable(df):
    df_display, columns = format_dataframe_to_datatable(df, show_new_data=True, show_category=False)

    dt_transactions = dt.DataTable(id='cell_search',
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
