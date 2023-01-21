from source.categories import ALL_CATEGORIES, OCCASIONS, TYPE_TRANSACTIONS
from source.db_connection.db_access import MongoDBConnection

LIST_ATTRIBUTES_METADATA = [
    'balance_in_bank',
    'balance_in_db',
    'balance_bias',
    'categories',
    'occasions',
    'nb_transactions_db',
    'types_transaction',
    'date_balance_in_bank',
    'date_last_import',
]


class MetadataDB:
    def __init__(self, name_connection, account_id):
        self.connection = MongoDBConnection(name_connection)
        self.account_id = account_id

        # Set default value
        for attribute in LIST_ATTRIBUTES_METADATA:
            setattr(self, attribute, None)

    def set(self, balance_in_bank, balance_in_db, balance_bias,
            date_balance_in_bank, date_last_import, nb_trans_db=0,
            categories=ALL_CATEGORIES, occasions=OCCASIONS, types=TYPE_TRANSACTIONS):

        self.balance_in_bank = balance_in_bank
        self.balance_in_db = balance_in_db
        self.balance_bias = balance_bias
        self.categories = categories
        self.occasions = occasions
        self.types_transaction = types
        self.nb_transactions_db = nb_trans_db
        self.date_balance_in_bank = dict()
        self.date_balance_in_bank['dt'] = date_balance_in_bank
        self.date_balance_in_bank['str'] = date_balance_in_bank.strftime("%d/%m/%Y")
        self.date_last_import = dict()
        self.date_last_import['dt'] = date_last_import
        self.date_last_import['str'] = date_last_import.strftime("%d/%m/%Y")

        # self.connection.collection.insert_one(data_to_ingest)

    def set_from_db(self):
        # Extract all data
        data = self.connection.collection.find_one({'account_id': self.account_id})

        if data is not None:
            # remove useless field
            del data['_id']
            del data['account_id']

            # Set dict as class attributes
            for key, value in data.items():
                setattr(self, key, value)

    def update_db(self):

        data_to_ingest = {
            'balance_in_bank': self.balance_in_bank,
            'balance_in_db': self.balance_in_db,
            'balance_bias': self.balance_bias,
            'categories': self.categories,
            'occasions': self.occasions,
            'nb_transactions_db': self.nb_transactions_db,
            'types_transaction': self.types_transaction,
            'date_balance_in_bank': self.date_balance_in_bank,
            'date_last_import': self.date_last_import,
        }

        self.connection.collection.update(
            {
                'account_id': self.account_id
            },
            {
                "$set": data_to_ingest
            },
            upsert=True
        )

    def update_values(self, new_values):
        for key, value in new_values.items():
            if (key == 'date_balance_in_bank') or (key == 'date_last_import'):
                value_dict = {
                    'dt': value,
                    'str': value.strftime("%d/%m/%Y"),
                }
                self.__setattr__(key, value_dict)
            elif key in self.__dict__.keys():
                self.__setattr__(key, value)

    def get_list_categories(self):
        return list(self.categories.keys())

    def get_list_categories_and_sub(self):

        cat_and_sub_cat = dict()
        for cat, value in self.categories.items():
            cat_and_sub_cat[cat] = list(value['Sub-categories'].keys())

        return cat_and_sub_cat

    def get_default_occasion(self, category, sub_category=None):

        category_info = self.categories[category]
        default_occasion = category_info['Default_occasion']
        if sub_category is not None and sub_category in list(category_info['Sub-categories'].keys()):
            default_occasion = category_info['Sub-categories'][sub_category]['Default_occasion']

        return default_occasion

    def get_list_subcategories(self, category):
        category_info = self.categories[category]
        return list(category_info['Sub-categories'].keys())

    def update_date_balance_in_bank(self, date):

        date_dt = date
        date_str = date.strftime("%d/%m/%Y")

        self.connection.collection.update({'account_id': self.account_id},
                                          {"$set": {'date_balance_in_bank.str': date_str,
                                                    'date_balance_in_bank.dt': date_dt}}, upsert=False)

    def update_date_last_import(self, date):

        date_dt = date
        date_str = date.strftime("%d/%m/%Y")

        self.connection.collection.update({'account_id': self.account_id},
                                          {"$set": {'date_last_import.str': date_str,
                                                    'date_last_import.dt': date_dt}}, upsert=False)

    def add_category(self, new_category, name_parent_category=None):
        list_categories = self.categories
        name_new_category = list(new_category.keys())[0]

        for att in ['Default_occasion', 'Order']:
            assert att in list(new_category[name_new_category].keys())

        # If the new category is a parent, add attributes to add sub-categories
        if name_parent_category is None:
            new_category[name_new_category]['Sub-categories'] = {}
            new_list_categories = {**list_categories, **new_category}
        else:
            new_list_categories = list_categories.copy()
            new_list_categories[name_parent_category]['Sub-categories'] = {
                **new_list_categories[name_parent_category]['Sub-categories'],
                **new_category}

        # Update list of categories
        self.categories = new_list_categories
        self.update_db()

    def remove_category(self, name_category_to_remove, name_parent_category):

        # Delete category
        if name_parent_category is None:
            del self.categories[name_category_to_remove]
        else:
            del self.categories[name_parent_category]['Sub-categories'][name_category_to_remove]

        # Update list of categories
        self.update_db()

    def update_category_properties(self, name_category, name_parent_category, new_category):

        # Store sub-categories if they exist
        if name_parent_category is None:
            previous_sub_cat = self.categories[name_category]['Sub-categories']
        else:
            previous_sub_cat = None

        # Remove previous category
        self.remove_category(
            name_category_to_remove=name_category,
            name_parent_category=name_parent_category,
        )

        # Add new category
        self.add_category(
            new_category=new_category,
            name_parent_category=name_parent_category,
        )

        # Put back the sub-categories
        if previous_sub_cat is not None:
            name_new_category = list(new_category.keys())[0]
            self.categories[name_new_category]['Sub-categories'] = previous_sub_cat
            self.update_db()

    def move_category(self, name_category, name_current_parent_category, name_new_parent_category):

        if name_current_parent_category is None or name_new_parent_category is None:
            Warning("One of the parent category is None")
            Warning("Current parent: {}".format(name_current_parent_category))
            Warning("New parent: {}".format(name_new_parent_category))
        else:
            # Get the category info
            category = {
                name_category: self.categories[name_current_parent_category]["Sub-categories"][name_category],
            }

            # Remove previous category
            self.remove_category(
                name_category_to_remove=name_category,
                name_parent_category=name_current_parent_category,
            )

            # Add new category
            self.add_category(
                new_category=category,
                name_parent_category=name_new_parent_category,
            )
