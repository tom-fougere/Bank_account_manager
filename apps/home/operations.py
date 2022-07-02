from source.data_ingestion.metadata import MetadataDB
from source.definitions import DB_CONN_ACCOUNT, ACCOUNT_ID
import plotly.graph_objects as go
import dash_html_components as html
import datetime


def get_metadata():
    db_meta = MetadataDB(DB_CONN_ACCOUNT, ACCOUNT_ID)

    db_meta.get_all_values()

    metadata = {
        "balance_in_bank": db_meta.balance_in_bank,
        "balance_in_db": db_meta.balance_in_db + db_meta.balance_bias,
        "balance_bias": db_meta.balance_bias,
        "date_last_import": db_meta.date_last_import,
        "nb_transactions_db": db_meta.nb_transactions_db,
        "nb_transactions_bank": db_meta.nb_transactions_bank,
    }

    return metadata


def fig_indicators_balances():
    metadata = get_metadata()
    delta_days = datetime.datetime.now() - metadata['date_last_import']['dt']

    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=metadata["balance_in_db"],
        number={'suffix': "€", "valueformat": '.2f'},
        title={"text": "Total"},
        delta={'reference': metadata["balance_in_bank"],
               'relative': False,
               'valueformat': '.2f',
               },
        domain={'row': 0, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=metadata["nb_transactions_bank"],
        title={"text": "Nombre de transactions"},
        delta={'reference': metadata["nb_transactions_bank"],
               'relative': False,
               'valueformat': 'f'},
        domain={'row': 0, 'column': 1}))
    figure.add_trace(go.Indicator(
        mode="number",
        value=delta_days.days,
        title={"text": "Dernière importation<br>"
                       "<span style='font-size:0.8em;color:gray'>{}</span>".format(metadata['date_last_import']['str'])},
        number={'suffix': "j"},
        domain={'row': 1, 'column': 0}))
    figure.update_layout(
        grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
    )

    return figure
