p_expenses_revenue_per_date = [
    {
        '$group': {
            '_id': {
                'Mois': {
                    '$month': "$date.dt"},
                'Année': {
                    '$year': "$date.dt"},
            },
            'Total_positive': {
                '$sum': {
                    '$cond': [
                        {
                            '$gt': ['$amount', 0]
                        },
                        "$amount", 0]
                }
            },
            'Total_negative': {
                '$sum': {
                    '$cond': [{
                        '$lt': ['$amount', 0]
                    },
                        "$amount", 0]
                }
            },
            'Balance': {
                '$sum': "$amount"}
        }
    }
]

p_balance_category_per_date = [
    {
        '$group': {
            '_id': {
                'Mois': {
                    '$month': "$date.dt"},
                'Année': {
                    '$year': "$date.dt"},
                'Categorie': '$category',
                'Sous-categorie': '$sub_category',
            },
            'Balance': {
                '$sum': "$amount"}
        }
    }
]

p_balance_occasion_per_date = [
    {
        '$match': {
            'category': {'$ne': 'Travail'}
        }
    },
    {
        '$group': {
            '_id': {
                'Mois': {
                    '$month': "$date.dt"},
                'Année': {
                    '$year': "$date.dt"},
                'Occasion': '$occasion',
            },
            'Balance': {
                '$sum': "$amount"}
        }
    }
]


p_savings_per_date = [
    {
        '$match': {
            'category': "Epargne"
        },
    },
    {
        '$group': {
            '_id': {
                'Mois': {
                    '$month': "$date.dt"},
                'Année': {
                    '$year': "$date.dt"},
            },
            'Balance': {
                '$sum': "$amount"}
        }
    }
]


p_loan_per_date = [
    {
        '$match': {
            'category': "Logement",
            'sub_category': "Loyer/Prêt",
        },
    },
    {
        '$group': {
            '_id': {
                'Mois': {
                    '$month': "$date.dt"},
                'Année': {
                    '$year': "$date.dt"},
            },
            'Balance': {
                '$sum': "$amount"}
        }
    }
]
