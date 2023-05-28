import plotly.graph_objects as go

from apps.current_stats.cs_operations import get_data_for_graph


custom_pipeline = [
    {'$match': {"_id": {"$exists": True}}}
]

pipeline_only_label = [

    {'$match': {"_id": {"$exists": True}}},
    {'$limit': 1}
]


def get_data_label():
    df = get_data_for_graph(pipeline_only_label)

    return df.keys().tolist()


def custom_fig(x_data_str, y_data_str):

    # Figures
    if x_data_str is not None and y_data_str is not None:

        # Get data
        df = get_data_for_graph(custom_pipeline)

        figure = go.Figure()
        figure.add_trace(
            go.Scatter(
                x=df[x_data_str],
                y=df[y_data_str]
            )
        )

    else:
        figure = {}

    return figure
