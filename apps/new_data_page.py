import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import Input, Output, State
import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme
from app import app
from datetime import date

from source.data_reader.bank_file_reader import BankTSVReader
from utils.text_operations import get_project_root

DATA_FOLDER = 'raw_data'


layout = html.Div([

    dcc.Upload(
        id='drag_upload_file',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a File')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        }),

    html.Div(id="new_transaction_msg"),
    html.Div(id="table"),
    dbc.Offcanvas(
            [html.P(
                "This is the content of the Offcanvas. "
                "Close it by clicking on the close button, or "
                "the backdrop."
            ),
            html.Div(id='test')],
            id="offcanvas",
            title="Title",
            is_open=False,
        ),

])

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


def create_datatable(df):

    df_display = df.copy()
    df_display.drop(['amount_f'], inplace=True, axis=1)
    df_display['date_transaction'] = df_display['date_transaction'].dt.strftime('%d/%m/%Y')
    df_display['date_bank'] = df_display['date_bank'].dt.strftime('%d/%m/%Y')
    df_display = df_display[['date_transaction', 'amount_e', 'description', 'type_transaction', 'date_bank']]
    df_display.rename(columns={'date_bank': 'Date (banque)',
                               'amount_e': 'Montant (€)',
                               'description': 'Libelé',
                               'type_transaction': 'Type',
                               'date_transaction': 'Date'}, inplace=True)

    columns = [{"name": i, "id": i, } for i in df_display.columns]
    columns[1]['type'] = 'numeric'
    columns[1]['format'] = Format(precision=2, scheme=Scheme.fixed).symbol(Symbol.yes).symbol_suffix('€')

    dt_transactions = dt.DataTable(id='table_content',
                                   data=df_display.to_dict('records'),
                                   columns=columns,
                                   column_selectable="single",
                                   selected_columns=[],
                                   selected_rows=[],
                                   style_data_conditional=[
                                       {
                                           'if': {
                                               'column_id': 'Montant (€)',
                                               'filter_query': '{Montant (€)} > 0'
                                           },
                                           'backgroundColor': '#B5EEB6'
                                       },
                                   ],
                                   style_cell_conditional=style_cell_conditional,
                                   style_header={
                                       'backgroundColor': 'rgb(210, 210, 210)',
                                       'color': 'black',
                                       'fontWeight': 'bold'
                                   }
                                   )
    return dt_transactions


def create_sidebar_transaction(df):
    component = dcc.DatePickerSingle(
        id='date-picker',
        date=date(df.date_transaction.year, df.date_transaction.month, df.date_transaction.day)
    )

    return component

@app.callback(
    Output("new_transaction_msg", 'children'),
    Output("table", 'children'),
    Input('drag_upload_file', 'contents'),
    State('drag_upload_file', 'filename'))
def upload_file(list_of_contents, filename):

    # default outputs
    msg = ''
    dt_transactions = dt.DataTable()
    if list_of_contents is not None:

        # Read data
        data_reader = BankTSVReader('/'.join([get_project_root(), DATA_FOLDER, filename]))
        df = data_reader.data

        # Create message
        msg = 'New transactions = {}'.format(len(df))

        # Convert to dataTable
        dt_transactions = create_datatable(df)

    return html.Div(msg), dt_transactions


@app.callback(
    [Output("offcanvas", "is_open"),
     Output('test', 'children')],
    Input('table_content', 'active_cell'),
    [State("offcanvas", "is_open"),
     State('drag_upload_file', 'filename')])
def display_one_transaction(active_cell, canvas_is_open, filename):

    # Read data
    data_reader = BankTSVReader('/'.join([get_project_root(), DATA_FOLDER, filename]))
    df = data_reader.data

    if active_cell is None:
        return canvas_is_open, html.Div()
    else:
        component = create_sidebar_transaction(df.iloc[active_cell['row']])
        return (not canvas_is_open), component



