import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq

from source.definitions import DB_CONN_ACCOUNT, ACCOUNT_ID
from source.transactions.metadata import MetadataDB
from apps.components import (
    get_categories_and_sub_for_dropdown_menu,
    get_occasions_for_dropdown_menu,
    get_categories_for_dropdown_menu,
)


def get_categories_name():
    metadata_db = MetadataDB(
        name_connection=DB_CONN_ACCOUNT,
        account_id=ACCOUNT_ID)
    metadata_db.set_from_db()
    categories = metadata_db.get_list_categories()

    return categories

# #################################### #
# ####### SWITCH CATEGORY ############ #
# #################################### #


def get_switch_cat_content():
    content = html.Div([
        html.Br(),
        dbc.Card(
            create_switch_cat_content(),
            body=True,
        ),
        html.Br()
    ])

    return content


def create_switch_cat_content():
    content = html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='id_dropdown_switch_cat_from',
                    options=get_categories_and_sub_for_dropdown_menu(
                        db_connection=DB_CONN_ACCOUNT,
                        account_id=ACCOUNT_ID,
                        delimiter=' - ',
                    ),
                    value=[],
                    style={'align-items': 'center'}
                ),
                width={"size": 3, "order": 1},
            ),
            dbc.Col(
                html.Div('=>'),
                width={"size": 1, "order": 2},
                style={'align': 'center'}
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='id_dropdown_switch_cat_to',
                    options=get_categories_for_dropdown_menu(
                        db_connection=DB_CONN_ACCOUNT,
                        account_id=ACCOUNT_ID
                    ),
                    value=[],
                    style={'align-items': 'center'}
                ),
                width={"size": 3, "order": 3},
            ),
            dbc.Col(
                dbc.Button(
                    "Save",
                    color="primary",
                    id='id_button_switch_cat',
                ),
                width={"size": 1, "order": "last", 'offset': 4},
            ),
        ])
    ])

    return content

# #################################### #
# ######## NEW CATEGORY ############## #
# #################################### #


def get_new_cat_content():
    content = html.Div([
        html.Br(),
        dbc.Card(
            create_new_cat_content(),
            body=True,
        ),
        html.Br()
    ])

    return content


def create_new_cat_content():

    content = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div("Nom:"),
                            align="center",
                            width={"size": 4},
                        ),
                        dbc.Col(
                            dbc.Input(
                                id='id_input_new_cat',
                                type="",
                                placeholder=''
                            ),
                            width={"size": 4},
                        ),
                        dbc.Col(
                            'test',
                            id='id_text_new_cat',
                            width={"size": 2},
                            align="center",
                        )
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div("Occasion par défault:"),
                            align="center",
                            width={"size": 4},
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='id_dropdown_new_cat_occasion',
                                options=get_occasions_for_dropdown_menu(
                                    db_connection=DB_CONN_ACCOUNT,
                                    account_id=ACCOUNT_ID,
                                ),
                                value=[],
                                style={'align-items': 'center'}
                            ),
                            width={"size": 4},
                            style={'align-items': 'center'}
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div('Sous-catégorie ?'),
                                    daq.BooleanSwitch(
                                        id='id_switch_new_cat',
                                        on=False,
                                        style={"margin-left": 10}),
                                ],
                                style={'margin-top': 10,
                                       "display": 'flex'}
                            ),
                            width={"size": 4},
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='id_dropdown_new_cat',
                                options=get_categories_for_dropdown_menu(
                                    db_connection=DB_CONN_ACCOUNT,
                                    account_id=ACCOUNT_ID
                                ),
                                value=[],
                                disabled=True,
                                style={'align-items': 'center'}
                            ),
                            width={"size": 4},
                            style={'align-items': 'center'}
                        ),
                    ]
                )
            ]),
            dbc.Col([
                html.Div([
                    dbc.Button(
                        "Save",
                        color="primary",
                        style={"height": 38 * 3},
                        id='id_button_new_cat',
                    ),
                ],
                )
            ],
                width=1,
            )
        ]),
    ])

    return content

# #################################### #
# ########## TABULATION ############## #
# #################################### #


def get_tab_content(tab_id):
    category = tab_id.replace('id_tab_', '')

    # Get subcategories
    metadata_db = MetadataDB(
        name_connection=DB_CONN_ACCOUNT,
        account_id=ACCOUNT_ID)
    metadata_db.set_from_db()
    sub_categories = metadata_db.categories[category]['Sub-categories']

    # Get information of the current category
    category_info = metadata_db.get_list_subcategories(
        category=category,
    )

    # Create accordion
    accordion = create_accordion(
        cat=category,
        sub_cats=sub_categories,
    )

    first_component = dbc.Card(
        dbc.CardBody([
            html.H5(category, className="card-title"),
            create_tab_content(
                cat=category,
                sub_cat='',
                default_occas=category_info['Default_occasion'],
                default_rename=category,
                disabled_occasion=len(sub_categories) > 0,
            ),
        ]),
        body=True,
    )

    content = html.Div([
        html.Br(),
        first_component,
        html.Br(),
        accordion
    ])

    return content


def create_tab_content(cat, sub_cat, default_occas=None, default_rename=None, disabled_occasion=False):
    name = cat + ':' + sub_cat

    content = html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div("Occasion par défault:"),
                            align="center",
                            width={"size": 4},
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id={
                                    'type': 'id_dropdown_default_occasion',
                                    'name': name
                                },
                                disabled=disabled_occasion,
                                options=get_occasions_for_dropdown_menu(
                                    db_connection=DB_CONN_ACCOUNT,
                                    account_id=ACCOUNT_ID,
                                ),
                                value=default_occas if default_occas is not None else [],
                                style={'align-items': 'center'}
                            ),
                            width={"size": 4},
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                [
                                    html.Div('Renommer:'),
                                    daq.BooleanSwitch(
                                        id={
                                            'type': 'id_switch_rename',
                                            'name': name
                                        },
                                        on=False,
                                        style={"margin-left": 10}),
                                ],
                                style={'margin-top': 10,
                                       "display": 'flex'}
                            ),
                            width={"size": 4},
                        ),
                        dbc.Col(
                            dbc.Input(
                                id={
                                    'type': 'id_input_rename',
                                    'name': name
                                },
                                # id='id_test',
                                type="",
                                placeholder=default_rename,
                                disabled=False
                            ),
                            width={"size": 4},
                            style={'align-items': 'center'}
                        ),
                        dbc.Col(
                            html.Div(
                                '',
                                id={
                                    'type': 'id_text_rename',
                                    'name': name,
                                }),
                            width={"size": 1},
                            align="center",
                        )
                    ]
                )
            ]),
            dbc.Col([
                html.Div([
                    dbc.Button(
                        "Save",
                        color="primary",
                        style={"height": 38*2},
                        id='id_button_save_param_' + name,
                    ),
                ],
                )
            ],
                width=1,
            )
        ]),
    ])

    return content

# #################################### #
# ########### ACCORDION ############## #
# #################################### #


def create_accordion(cat, sub_cats):
    accordion_items = []

    for sub_cat, info in sub_cats.items():

        accordion_items.append(
            create_single_accordion_item(
                cat=cat,
                sub_cat=sub_cat,
                default_occas=info['Default_occasion'],
                default_rename=sub_cat)
        )

    accordion = dbc.Accordion(
        accordion_items,
        # id="id_" + name,
        id='accordion',
        start_collapsed=True,
        flush=True,
        # always_open=True,
        # active_item="item-categories",
        style={'padding': '0.1rm'},
    )

    return accordion


def create_single_accordion_item(cat, sub_cat, default_occas=None, default_rename=None):

    accordion_item = dbc.AccordionItem(
        create_tab_content(
            cat=cat,
            sub_cat=sub_cat,
            default_occas=default_occas,
            default_rename=default_rename
        ),
        title=sub_cat,
        item_id='accordion_item_' + cat + ':' + sub_cat
    )

    return accordion_item
