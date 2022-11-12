import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, ClientsideFunction
from app import app

from apps.params_category.pc_operations import get_categories_name, get_tab_content


tabs_category = dbc.Tabs(
    [
        dbc.Tab(
            label=cat,
            tab_id='id_tab_' + cat,
            active_label_style={"color": "#0043DB"},
            activeTabClassName="fw-bold",
        ) for cat in get_categories_name()
    ],
    id='id_all_tabs',
)

accordion_category = ()

layout = html.Div([

    html.H1('Catégories',
            id='title_page_category',
            style={'textAlign': 'center'}),

    tabs_category,
    html.Div(id='tab_content'),

    html.Br(),
    html.H3('Ajouter une nouvelle catégorie',
            id='title_page_category',
            style={'textAlign': 'left'}),

    html.H3('Déplacer une catégorie',
            id='title_page_category',
            style={'textAlign': 'left'}),

    # create_cat_accordion(),

    html.Div(id="accordion-contents", className="mt-3"),
],)


@app.callback(
    Output("tab_content", "children"),
    [Input("id_all_tabs", "active_tab")])
def switch_tab(active_tab):

    return get_tab_content(active_tab)


@app.callback(
    [Output('id_input_rename', 'disabled')],
    [Input('id_bool_switch_rename', 'on')],
    [State('id_input_rename', 'disabled'),
     State('id_input_rename', 'disabled')])
def disable_enable_renaming(
        bool_amount, bool_category, bool_type, bool_occasion, bool_description, bool_note, bool_check):

    pass
    # return get_tab_content(active_tab)


