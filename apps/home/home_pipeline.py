p_savings = [
    {
        '$match': {
            'category': "Epargne"
        },
    },
    {
        '$group': {
            '_id': {
                'Année': {
                    '$year': "$date.dt"},
            },
            'Sum': {
                '$sum': "$amount"}
        }
    }
]

p_loan = [
    {
        '$match': {
            'category': "Logement",
            'sub_category': "Loyer/Prêt",
        },
    },
    {
        '$group': {
            '_id': {
                'Année': {
                    '$year': "$date.dt"},
            },
            'Sum': {
                '$sum': "$amount"}
        }
    },
]

p_gain = [
    {
        '$group': {
            '_id': {
                'Année': {
                    '$year': "$date.dt"},
            },
            'Sum': {
                '$sum': "$amount"}
        }
    }
]