from source.transactions.metadata import MetadataDB
from source.definitions import DB_CONN_ACCOUNT, ACCOUNT_ID
import plotly.graph_objects as go
import datetime


def get_metadata():
    db_meta = MetadataDB(DB_CONN_ACCOUNT, ACCOUNT_ID)
    db_meta.set_from_db()

    metadata = {
        "balance_in_bank": db_meta.balance_in_bank,
        "balance_in_db": db_meta.balance_in_db + db_meta.balance_bias,
        "balance_bias": db_meta.balance_bias,
        "date_last_import": db_meta.date_last_import,
        "nb_transactions_db": db_meta.nb_transactions_db,
    }

    return metadata


def fig_indicators_balances():
    metadata = get_metadata()
    delta_days = datetime.datetime.now() - metadata['date_last_import']['dt']

    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=round(metadata["balance_in_db"], 2),
        number={'suffix': "€", "valueformat": '.2f'},
        title={"text": "Total"},
        delta={'reference': round(metadata["balance_in_bank"], 2),
               'relative': False,
               'valueformat': '.2f',
               },
        domain={'row': 0, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number",
        value=metadata["nb_transactions_db"],
        title={"text": "Nombre de transactions"},
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
