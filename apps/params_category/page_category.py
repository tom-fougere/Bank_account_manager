import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, ALL
from app import app

from apps.params_category.pc_operations import get_categories_name, get_tab_content, get_new_cat_content, \
    get_switch_cat_content

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
            id='title_page_category',
            style={'textAlign': 'left'}),
    html.Div(get_new_cat_content()),

    html.H4('Déplacer une catégorie',
            id='title_page_category',
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
    Output('id_dropdown_new_cat', 'disabled'),
    Input('id_switch_new_cat', 'on')
)
def disable_new_sub_cat(value):
    return not value


@app.callback(
    [Output('id_text_new_cat', 'children'),
     Output('id_button_new_cat', 'disabled'), ],
    [Input('id_input_new_cat', 'value'),
     Input('id_switch_new_cat', 'on'),
     Input('id_dropdown_new_cat_occasion', 'value'),
     Input('id_dropdown_new_cat', 'value'),]

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
