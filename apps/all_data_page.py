import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import Input, Output, State
import dash_table as dt
from dash_table.Format import Format, Symbol, Scheme
from app import app

from source.data_reader.bank_file_reader import BankTSVReader
from utils.text_operations import get_project_root
from source.db_connection.db_access import MongoDBConnection
from source.data_ingestion.ingest import TransactionIngest

DB_CONNECTION = 'db_bank_connection'


layout = html.Div([
    html.Div('Compte bancaire:'),
    dcc.Input(
        value=None,
        style={'width': '100%'},
        type='number'),
    html.Div('Date Transaction'),
    dcc.DatePickerRange(),
    html.Div('Libelé'),
    dcc.Textarea(
        value=None,
        style={'width': '100%'}),
    html.Div('Montant (€)'),
    dcc.Input(
        type="number",
        placeholder="Minimum",
        style={'width': '50%'}),
    dcc.Input(
        type="number",
        debounce=True,
        placeholder="Maximum",
        style={'width': '50%'}),
    html.Div('Type:'),
    dcc.Input(
        value=None,
        style={'width': '100%'}),
    html.Div('Catégorie:'),
    dcc.Input(
        value=None,
        style={'width': '100%'}),
    dcc.Input(
        value=None,
        style={'width': '100%'}),
    html.Div('Occasion:'),
    dcc.Input(
        value=None,
        style={'width': '100%'}),
    html.Div('Date à la banque:'),
    dcc.DatePickerRange(),
    html.Div('Note:'),
    dcc.Textarea(
        value=None,
        style={'width': '100%'}),
    html.Div(id="table"),
])




