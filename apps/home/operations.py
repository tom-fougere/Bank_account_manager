from source.transactions.metadata import MetadataDB
from source.transactions.exgest import exgest_with_pipeline
from source.definitions import DB_CONN_ACCOUNT, ACCOUNT_ID, DB_CONN_TRANSACTION
from apps.home.home_pipeline import p_gain, p_loan, p_savings
import plotly.graph_objects as go
import datetime


def get_sums(pipeline):
    current_year = datetime.datetime.now().year

    df = exgest_with_pipeline(
        db_connection=DB_CONN_TRANSACTION,
        pipeline=pipeline,
    )
    sum_all_year = df['Sum'].sum()

    try:
        sum_current_year = df.loc[df['Année'] == current_year, 'Sum'].values[0]
    except Exception as e:
        sum_current_year = 0.

    return sum_all_year, sum_current_year

def get_metadata():
    db_meta = MetadataDB(DB_CONN_ACCOUNT, ACCOUNT_ID)
    db_meta.set_from_db()

    # Get data
    all_gains, gain_current_year = get_sums(p_gain)
    all_savings, savings_current_year = get_sums(p_savings)
    all_loan, loan_current_year = get_sums(p_loan)

    metadata = {
        "balance_in_bank": db_meta.balance_in_bank,
        "balance_in_db": db_meta.balance_in_db + db_meta.balance_bias,
        "balance_bias": db_meta.balance_bias,
        "date_last_import": db_meta.date_last_import,
        "nb_transactions_db": db_meta.nb_transactions_db,
        "all_gain": all_gains,
        "gain_current_year": gain_current_year,
        "all_savings": -all_savings,
        "savings_current_year": -savings_current_year,
        "all_loan": all_loan,
        "loan_current_year": loan_current_year,
    }

    return metadata


def fig_indicators_balances():
    metadata = get_metadata()
    delta_days = datetime.datetime.now() - metadata['date_last_import']['dt']

    figure = go.Figure()
    figure.add_trace(go.Indicator(
        mode="number",
        value=delta_days.days,
        title={"text": "Dernière importation<br>"
                       "<span style='font-size:0.8em;color:gray'>{}</span>".format(metadata['date_last_import']['str'])},
        number={'suffix': "j"},
        domain={'row': 0, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=round(metadata["balance_in_db"], 1),
        number={'suffix': " €", "valueformat": '.1f'},
        title={"text": "Total"},
        delta={'reference': round(metadata["balance_in_bank"], 1),
               'relative': False,
               'valueformat': '.1f',
               },
        domain={'row': 0, 'column': 1}))
    figure.add_trace(go.Indicator(
        mode="number",
        value=metadata["nb_transactions_db"],
        title={"text": "Nombre de transactions"},
        domain={'row': 0, 'column': 2}))

    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=round(metadata["all_gain"], 1),
        number={'suffix': " €", "valueformat": '.1f'},
        title={"text": "Gain (depuis 2022)"},
        delta={'reference': round(metadata["all_gain"] - metadata["gain_current_year"], 1),
               'relative': False,
               'valueformat': '.1f',
               },
        domain={'row': 1, 'column': 0}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=round(metadata["all_savings"], 1),
        number={'suffix': " €", "valueformat": '.1f'},
        title={"text": "Epargne"},
        delta={'reference': round(metadata["all_savings"] - metadata["savings_current_year"], 1),
               'relative': False,
               'valueformat': '.1f',
               },
        domain={'row': 1, 'column': 1}))
    figure.add_trace(go.Indicator(
        mode="number+delta",
        value=round(metadata["all_loan"], 1),
        number={'suffix': " €", "valueformat": '.1f'},
        title={"text": "Prêt"},
        delta={'reference': round(metadata["all_loan"] - metadata["loan_current_year"], 1),
               'relative': False,
               'valueformat': '.1f',
               },
        domain={'row': 1, 'column': 2}))

    figure.update_layout(
        grid={'rows': 2, 'columns': 3, 'pattern': "independent"},
    )

    return figure
