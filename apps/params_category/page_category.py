import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, ALL, callback_context
from app import app

from apps.params_category.pc_operations import get_categories_name, get_tab_content, get_new_cat_content, \
    get_switch_cat_content, add_new_category

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

layout = html.Div([

    html.H1('Catégories',
            id='title_page_category',
            style={'textAlign': 'center'}),

    tabs_category,
    html.Div(id='tab_content'),

    html.Br(),
    html.Hr(),
    html.H4('Ajouter une nouvelle catégorie',
            id='title_new_category',
            style={'textAlign': 'left'}),
    html.Div(get_new_cat_content()),

    html.H4('Déplacer une catégorie',
            id='title_move_category',
            style={'textAlign': 'left'}),
    html.Div(get_switch_cat_content()),

], )


@app.callback(
    Output("tab_content", "children"),
    [Input("id_all_tabs", "active_tab")])
def switch_tab(active_tab):
    return get_tab_content(active_tab)


@app.callback(
    Output({'type': 'id_input_rename', 'name': ALL}, 'disabled'),
    Input({'type': 'id_switch_rename', 'name': ALL}, 'on')
)
def disable_enable_renaming(values):
    return [not value for value in values]


@app.callback(
    Output('id_dropdown_parent_new_cat', 'disabled'),
    Input('id_switch_new_cat', 'on')
)
def disable_new_sub_cat(value):
    return not value


@app.callback(
    [Output('id_text_new_cat', 'children'),
     Output('id_button_new_cat', 'disabled')],
    [Input('id_input_new_cat', 'value'),
     Input('id_switch_new_cat', 'on'),
     Input('id_dropdown_new_cat_occasion', 'value'),
     Input('id_dropdown_parent_new_cat', 'value')]
)
def check_new_cat_exist(new_cat_name, is_subcat, occasion, mother_cat):
    message = ''
    button_disable = True

    if new_cat_name is not None:

        if len(new_cat_name) > 0 and \
                '.' not in new_cat_name and \
                new_cat_name not in get_categories_name() and\
                occasion is not None and len(occasion) > 0 and \
                (not is_subcat or (mother_cat is not None and len(mother_cat) > 0)):
            button_disable = False

        if '.' in new_cat_name:
            message = "Le `.` n'est pas autorisé !"
        # elif is_subcat and new_name in get_sub_categories(cat):
        elif new_cat_name in get_categories_name():
            message = 'Déjà existant !'

    return message, button_disable


@app.callback(
    Output('id_button_switch_cat', 'disabled'),
    [Input('id_dropdown_switch_cat_from', 'value'),
     Input('id_dropdown_switch_cat_to', 'value')]

)
def check_switch_cat(previous_cat, new_cat):

    disabled = True
    if previous_cat is not None and new_cat is not None and len(previous_cat) > 0 and len(new_cat) > 0:
        disabled = False

    return disabled


@app.callback(
    Output({'type': 'id_text_rename', 'name': ALL}, 'children'),
    Input({'type': 'id_input_rename', 'name': ALL}, 'value'),
)
def check_renaming(values):

    print(values)
    return values


@app.callback(
    Output("badge_new_cat", "children"),
    Output("badge_new_cat", "is_open"),
    Input("id_button_new_cat", "n_clicks"),
    State("id_input_new_cat", "value"),
    State("id_dropdown_new_cat_occasion", "value"),
    State("id_dropdown_parent_new_cat", "value")
)
def add_new_category(n_clicks, new_cat_name, new_cat_default_occ, parent_cat):

    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    message = ""
    is_open = False

    if triggered_input == 'id_button_new_cat':

        add_new_category(
            new_cat_name=new_cat_name,
            new_cat_occasion=new_cat_default_occ,
            parent_cat_name=parent_cat if len(new_cat_name) > 0 else None
        )

        message = "Done"
        is_open = True

    return message, is_open


@app.callback(
    Output("badge_switch_cat", "children"),
    Output("badge_switch_cat", "is_open"),
    Input("id_button_switch_cat", "n_clicks"),
    State("id_dropdown_switch_cat_from", "value"),
    State("id_dropdown_switch_cat_to", "value"),
)
def move_category(n_clicks, cat_and_parent_cat, new_parent_cat):
    ctx = callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    message = ""
    is_open = False

    if triggered_input == 'id_button_switch_cat':

        move_category(cat_and_parent_cat, new_parent_cat)

        message = "Done"
        is_open = True

    return message, is_open
