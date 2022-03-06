p_expenses_gains_per_date = [
    {
        '$group': {
            '_id': {
                'Mois': {
                    '$month': "$date.dt"},
                'Année': {
                    '$year': "$date.dt"},
            },
            'Total_positive': {
                '$sum':{
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
        '$group': {
            '_id': {
                'Mois': {
                    '$month': "$date.dt"},
                'Année': {
                    '$year': "$date.dt"},
                'Categorie': '$category',
                'Occasion': '$occasion',
            },
            'Balance': {
                '$sum': "$amount"}
        }
    }
]
