import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq

from source.definitions import DB_CONN_ACCOUNT, ACCOUNT_ID, OCCASIONS
from source.transactions.metadata import MetadataDB
from source.transactions.transaction_operations import get_categories_and_subcat


def get_categories_name():
    metadata_db = MetadataDB(
        name_connection=DB_CONN_ACCOUNT,
        account_id=ACCOUNT_ID)
    categories = metadata_db.get_categories()

    return categories


def get_tab_content(tab_id):
    category = tab_id.replace('id_tab_', '')

    # Get subcategories
    metadata_db = MetadataDB(
        name_connection=DB_CONN_ACCOUNT,
        account_id=ACCOUNT_ID)
    sub_categories = metadata_db.get_sub_categories(
        category=category
    )

    # Create accordion
    accordion = create_accordion(
        name=category,
        accordion_names=sub_categories,
    )

    # tab_content = dbc.Card(
    #     dbc.CardBody(
    #         [
    #             html.P('')
    #         ]
    #     )
    # )
    return accordion


def create_content(name):
    content = html.Div([
        html.Div([
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
                                    id='id_dropdown_occasion_' + name,
                                    options=[{'label': occ, 'value': occ} for occ in OCCASIONS],
                                    value=[],
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
                                            id='id_bool_switch_rename',
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
                                    id='id_input_rename',
                                    type="text",
                                    placeholder="",
                                    disabled=True
                                ),
                                width={"size": 4},
                                style={'align-items': 'center'}
                            ),
                            dbc.Col(
                                html.Div('text', id='id_text_renamed'),
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
                        ),
                    ],
                    # className="d-grid gap-2",
                    )

                ],
                    width=1,
                )
            ]),
        ]
        ),
    ])

    return content


def create_accordion(name, accordion_names, list_contents=None):
    accordion_items = []
    if list_contents is None:
        list_contents = [None] * len(accordion_names)

    for cat, content in zip(accordion_names, list_contents):
        accordion_items.append(
            create_single_accordion_item(
                name=cat,
                content=content)
        )

    accordion = dbc.Accordion(
        accordion_items,
        id="id_" + name,
        start_collapsed=True,
        flush=True,
        # always_open=True,
        # active_item="item-categories",
        style={'padding': '0.1rm'},
    )

    return accordion


def create_single_accordion_item(name):

    accordion_item = dbc.AccordionItem(
        create_content(name),
        title=name,
        item_id='item_' + name
    )

    return accordion_item
