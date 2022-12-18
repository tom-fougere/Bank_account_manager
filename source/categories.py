
# #################################### #
# ########## DEFINITIONS ############# #
# #################################### #

# CATEGORIES = {'Travail': ['Salaire', 'Prime', 'Autre'],
#               'Impots': ['Taxe habitation', 'Taxe Foncière', 'Autre'],
#               'Logement': ['Loyer/Prêt', 'Eau/Gaz/Elec', 'Assurance', 'Deco/Meuble', 'Copro.', 'Autre'],
#               'Transport': ['Carburant', 'Entretien', 'Assurance', 'Transport en commun', 'Autre'],
#               'Alimentation': ['Supermarché/Drive', 'Repas Travail', 'Resto', 'Autre'],
#               'Sortie/Voyage': ['Culture', 'Détente', 'Voyage', 'Soirée/Wkd', 'Autre'],
#               'Tech/Sport': ['Internet/TV/Tel', 'Abonnement', 'Sport', 'Electronique', 'Autre'],
#               'Autre': [],
#               'Santé': [],
#               'Perso': ['Tom', 'Elise'],
#               'Epargne': [],
#               'Fêtes': ['Anniversaire', 'Fêtes', 'Autre']}

OCCASIONS = ['Régulier', 'Ponctuel', 'Loisir']

TYPE_TRANSACTIONS = ['PRELEVEMENT', 'CREDIT', 'VIREMENT', 'ACHAT']

DEFAULT_OCCASION_FOR_CAT = {
    'Travail': {'Salaire': 'Régulier',
                'Prime': 'Ponctuel',
                'Autre': 'Ponctuel'},
    'Impots': {'Taxe habitation': 'Régulier',
               'Taxe Foncière': 'Régulier',
               'Autre': 'Ponctuel'},
    'Logement': {'Loyer/Prêt': 'Régulier',
                 'Eau/Gaz/Elec': 'Régulier',
                 'Assurance': 'Régulier',
                 'Deco/Meuble': 'Ponctuel',
                 'Copro.': 'Régulier',
                 'Autre': 'Ponctuel'},
    'Transport': {'Carburant': 'Régulier',
                  'Entretien': 'Ponctuel',
                  'Assurance': 'Régulier',
                  'Transport en commun': 'Régulier',
                  'Autre': 'Ponctuel'},
    'Alimentation': {'Supermarché/Drive': 'Régulier',
                     'Repas Travail': 'Régulier',
                     'Resto': 'Loisir',
                     'Autre': 'Ponctuel'},
    'Sortie/Voyage': {'Culture': 'Loisir',
                      'Détente': 'Loisir',
                      'Voyage': 'Loisir',
                      'Soirée/Wkd': 'Loisir',
                      'Autre': 'Loisir'},
    'Tech/Sport': {'Internet/TV/Tel': 'Régulier',
                   'Abonnement': 'Régulier',
                   'Sport': 'Ponctuel',
                   'Electronique': 'Ponctuel',
                   'Autre': 'Ponctuel'},
    'Autre': 'Ponctuel',
    'Santé': 'Ponctuel',
    'Perso': {'Tom': 'Loisir',
              'Elise': 'Loisir'},
    'Epargne': 'Ponctuel',
    'Fêtes': {'Anniversaire': 'Ponctuel',
              'Fêtes': 'Ponctuel',
              'Autre': 'Ponctuel'}
}

ALL_CATEGORIES = {
    'Travail': {
        "Sub-categories": {
            "Salaire": {
                "Default_occasion": 'Régulier',
                "Order": 1,
            },
            "Prime": {
                "Default_occasion": 'Ponctuel',
                "Order": 2,
            },
            "Autre": {
                "Default_occasion": 'Ponctuel',
                "Order": 3,
            },
        },
        "Default_occasion": None,
        "Order": 1,
    },
    'Impots': {
       "Sub-categories": {
           "Taxe habitation": {
               "Default_occasion": 'Régulier',
               "Order": 1,
           },
           "Taxe Foncière": {
               "Default_occasion": 'Régulier',
               "Order": 2,
           },
           "Autre": {
               "Default_occasion": 'Ponctuel',
               "Order": 3,
           },
       },
       "Default_occasion": None,
       "Order": 1,
    },
    'Logement': {
       "Sub-categories": {
           "Loyer/Prêt": {
               "Default_occasion": 'Régulier',
               "Order": 1,
           },
           "Eau/Gaz/Elec": {
               "Default_occasion": 'Régulier',
               "Order": 2,
           },
           "Assurance": {
               "Default_occasion": 'Régulier',
               "Order": 3,
           },
           "Deco/Meuble": {
               "Default_occasion": 'Ponctuel',
               "Order": 4,
           },
           "Copro.": {
               "Default_occasion": 'Régulier',
               "Order": 5,
           },
           "Autre": {
               "Default_occasion": 'Ponctuel',
               "Order": 6,
           },
       },
       "Default_occasion": None,
       "Order": 1,
    },
    'Transport': {
       "Sub-categories": {
           "Carburant": {
               "Default_occasion": 'Régulier',
               "Order": 1,
           },
           "Entretien": {
               "Default_occasion": 'Ponctuel',
               "Order": 2,
           },
           "Assurance": {
               "Default_occasion": 'Régulier',
               "Order": 3,
           },
           "Transport en commun": {
               "Default_occasion": 'Régulier',
               "Order": 4,
           },
           "Autre": {
               "Default_occasion": 'Ponctuel',
               "Order": 5,
           },
       },
       "Default_occasion": None,
       "Order": 1,
    },
    'Alimentation': {
       "Sub-categories": {
           "Supermarché/Drive": {
               "Default_occasion": 'Régulier',
               "Order": 1,
           },
           "Repas Travail": {
               "Default_occasion": 'Régulier',
               "Order": 2,
           },
           "Resto": {
               "Default_occasion": 'Loisir',
               "Order": 3,
           },
           "Autre": {
               "Default_occasion": 'Ponctuel',
               "Order": 4,
           },
       },
       "Default_occasion": None,
       "Order": 1,
    },
    'Sortie/Voyage': {
        "Sub-categories": {
            "Culture": {
                "Default_occasion": 'Loisir',
                "Order": 1,
            },
            "Détente": {
                "Default_occasion": 'Loisir',
                "Order": 2,
            },
            "Voyage": {
                "Default_occasion": 'Loisir',
                "Order": 3,
            },
            "Soirée/Wkd": {
                "Default_occasion": 'Loisir',
                "Order": 4,
            },
            "Autre": {
                "Default_occasion": 'Loisir',
                "Order": 5,
            },
        },
        "Default_occasion": None,
        "Order": 1,
    },
    'Tech/Sport': {
        "Sub-categories": {
            "Internet/TV/Tel": {
                "Default_occasion": 'Régulier',
                "Order": 1,
            },
            "Abonnement": {
                "Default_occasion": 'Régulier',
                "Order": 2,
            },
            "Sport": {
                "Default_occasion": 'Régulier',
                "Order": 3,
            },
            "Electronique": {
                "Default_occasion": 'Ponctuel',
                "Order": 4,
            },
            "Autre": {
                "Default_occasion": 'Ponctuel',
                "Order": 5,
            },
        },
        "Default_occasion": None,
        "Order": 1,
    },
    'Perso': {
        "Sub-categories": {
            "Tom": {
                "Default_occasion": 'Loisir',
                "Order": 1,
            },
            "Elise": {
                "Default_occasion": 'Loisir',
                "Order": 2,
            },
        },
        "Default_occasion": None,
        "Order": 1,
    },
    'Fêtes': {
        "Sub-categories": {
            "Anniversaire": {
                "Default_occasion": 'Ponctuel',
                "Order": 1,
            },
            "Fêtes": {
                "Default_occasion": 'Ponctuel',
                "Order": 2,
            },
            "Autre": {
                "Default_occasion": 'Ponctuel',
                "Order": 3,
            },
        },
        "Default_occasion": None,
        "Order": 1,
    },
    'Santé': {
        "Sub-categories": {
        },
        "Default_occasion": "Ponctuel",
        "Order": 1,
    },
    'Autre': {
        "Sub-categories": {
        },
        "Default_occasion": "Ponctuel",
        "Order": 1,
    },
    'Epargne': {
        "Sub-categories": {
        },
        "Default_occasion": "Ponctuel",
        "Order": 1,
    },
}


# #################################### #
# ############ FUNCTIONS ############# #
# #################################### #

def get_list_categories():
    return list(ALL_CATEGORIES.keys())


def get_list_categories_and_sub():
    cat_and_sub_cat = dict()
    for cat, value in ALL_CATEGORIES.items():
        cat_and_sub_cat[cat] = list(value['Sub-categories'].keys())

    return cat_and_sub_cat


def get_sub_categories(category):
    return list(ALL_CATEGORIES[category]['Sub-categories'].keys())


def get_default_occasion(category, sub_category=None):
    category_info = ALL_CATEGORIES[category]
    default_occasion = category_info['Default_occasion']
    if sub_category is not None and sub_category in list(category_info['Sub-categories'].keys()):
        default_occasion = category_info['Sub-categories'][sub_category]['Default_occasion']

    return default_occasion
