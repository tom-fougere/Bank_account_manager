# #################################### #
# ############### DATE ############### #
# #################################### #

MONTHS = [
    'Janvier',
    'Février',
    'Mars',
    'Avril',
    'Mai',
    'Juin',
    'Juillet',
    'Août',
    'Septembre',
    'Octobre',
    'Novembre',
    'Décembre'
]


# #################################### #
# ############# COLUMNS ############## #
# #################################### #

class InfoName:
    ID = '_id'
    DATE_BANK_STR = 'date_str'
    DATE_BANK = 'date'
    AMOUNT = 'amount'
    DESCRIPTION = 'description'
    TYPE = 'type_transaction'
    DATE_TRANS_STR = 'date_transaction_str'
    DATE_TRANS = 'date_transaction'
    CATEGORY = 'category'
    SUB_CATEGORY = 'sub_category'
    OCCASION = 'occasion'
    CHECK = 'check'
    NOTE = 'note'
    DUPLICATE = 'duplicate'


class InfoDisplay:
    ALL = [
        InfoName.DATE_BANK_STR,
        InfoName.AMOUNT,
        InfoName.DESCRIPTION,
        InfoName.CATEGORY,
        InfoName.SUB_CATEGORY,
        InfoName.OCCASION,
        InfoName.CHECK,
        InfoName.NOTE,
        InfoName.TYPE,
        InfoName.DATE_TRANS_STR,
        InfoName.DATE_BANK,
        InfoName.DATE_TRANS,
        InfoName.DUPLICATE,
    ]
    SEARCH = [
        InfoName.DATE_TRANS_STR,
        InfoName.AMOUNT,
        InfoName.DESCRIPTION,
        InfoName.CATEGORY,
        InfoName.SUB_CATEGORY,
        InfoName.OCCASION,
        InfoName.CHECK,
        InfoName.NOTE,
        InfoName.TYPE,
        InfoName.DATE_BANK_STR,
    ]
    IMPORT = [
        InfoName.DATE_BANK_STR,
        InfoName.AMOUNT,
        InfoName.DESCRIPTION,
        InfoName.TYPE,
        InfoName.DATE_TRANS_STR,
        InfoName.DUPLICATE,
    ]


INFO_RENAMING = {
    InfoName.DATE_BANK_STR: 'Date (banque)',
    InfoName.AMOUNT: 'Montant (€)',
    InfoName.DESCRIPTION: 'Libelé',
    InfoName.CATEGORY: 'Catégorie',
    InfoName.SUB_CATEGORY: 'Sous-catégorie',
    InfoName.OCCASION: 'Occasion',
    InfoName.CHECK: 'Pointage',
    InfoName.NOTE: 'Note',
    InfoName.TYPE: 'Type',
    InfoName.DATE_TRANS_STR: 'Date',
    InfoName.DATE_BANK: 'Date (banque)',
    InfoName.DATE_TRANS: 'Date',
    InfoName.DUPLICATE: 'Duplicata',
}

# #################################### #
# ############# OTHERS ############### #
# #################################### #

DATA_FOLDER = 'raw_data'
DB_CONN_TRANSACTION = 'db_transaction_connection'
DB_CONN_ACCOUNT = 'db_account_connection'
ACCOUNT_ID = ''
