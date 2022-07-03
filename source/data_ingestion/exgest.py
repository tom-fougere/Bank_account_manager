import pandas as pd
from utils.mixed_utils import expand_columns_of_dataframe
from source.db_connection.db_access import MongoDBConnection


class TransactionExgest:
    def __init__(self, name_connection):

        self.connection = MongoDBConnection(name_connection)

        # Method use for the exgestion: "search" or "pipeline"
        self.exgestion_method = None

        self.attributes = ['account_id', 'date', 'description',
                           'amount', 'type_transaction',
                           'category', 'occasion', 'check',
                           'date_transaction']
        self.account_id = None
        self.date = []
        self.description = None
        self.amount = []
        self.type_transaction = None
        self.category = None
        self.occasion = None
        self.date_transaction = []
        self.check = None
        self.pipeline = []

    def set_search_criteria(self, dict_searches):
        self.account_id = dict_searches.get('account_id', None)
        self.date = dict_searches.get('date', [])
        self.description = dict_searches.get('description', None)
        self.amount = dict_searches.get('amount', [])
        self.type_transaction = dict_searches.get('type_transaction', None)
        self.occasion = dict_searches.get('occasion', None)
        self.date_transaction = dict_searches.get('date_transaction', [])
        self.check = dict_searches.get('check', None)

        searched_attributes = [key for key in dict_searches if key in self.attributes]

        # Set categories and sub-categories
        self._set_categories(dict_searches)

        # Generate the pipeline
        self.create_pipeline_from_search_criteria(searched_attributes)

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

        if len(self.pipeline) > 0:
            self._add_date_fields()

    def exgest_all(self):
        return pd.DataFrame(list(self.connection.collection.find()))

    def aggregate(self, pipeline):
        if len(pipeline) == 0:
            result = pd.DataFrame()
        else:
            result = pd.DataFrame(list(self.connection.collection.aggregate(pipeline)))
        return result

    def create_pipeline_from_search_criteria(self, searched_attributes):
        self.pipeline = []

        for att in searched_attributes:
            att_value = getattr(self, att)

            if is_var_empty(att_value) is False:

                # Manage dates
                if att in ['date', 'date_transaction']:
                    if att_value[0] is None:
                        cond = {"$lte": att_value[1]}
                    else:
                        cond = {"$gte": att_value[0],
                                "$lte": att_value[1]}
                    self.pipeline.append({
                        "$match": {
                            '.'.join([att, 'dt']): cond
                        }
                    })

                # Manage text areas
                elif att in ['description', 'note']:
                    self.pipeline.append({
                        "$match": {
                            att: {"$regex": ''.join(['/*', att_value, '/*']), "$options": 'i'}
                        }
                    })

                # Manage numeric value
                elif att in ['amount']:
                    self.pipeline.append({
                        "$match": {
                            att: {cond: value for cond, value in zip(['$gte', '$lte'], att_value) if value is not None}
                            # att: {"$gte": min(att_value[0], att_value[1]),
                            #       "$lte": max(att_value[0], att_value[1])}
                        }
                    })

                elif att in ['category']:
                    all_cat_cond = []
                    for cat in att_value:
                        cat_cond = {'category': cat[0]}

                        if cat[1]:
                            cat_cond['sub_category'] = cat[1]

                        all_cat_cond.append(cat_cond)

                    self.pipeline.append({
                        "$match": {"$or": all_cat_cond}

                    })
                elif isinstance(att_value, list):
                    self.pipeline.append({
                        "$match": {
                            att: {"$in": att_value}
                        }})
                else:
                    self.pipeline.append({
                        "$match": {
                            att: att_value
                        }})
            else:
                self.pipeline.append({
                    "$match": {
                        att: None
                    }})

        self._add_date_fields()

    def _set_categories(self, dict_searches):

        if 'category' in dict_searches.keys() and dict_searches['category'] is not None:
            self.category = join_cat_and_subcat(
                categories=dict_searches.get('category'),
                sub_categories=dict_searches.get('sub_category', None)
            )
        else:
            self.category = None

    def _add_date_fields(self):
        self.pipeline.append({
            "$addFields": {
                "date_str": "$date.str",
                "date_dt": "$date.dt",
                "date_transaction_str": "$date_transaction.str",
                "date_transaction_dt": "$date_transaction.dt",
            }
        })

    def exgest(self):
        result = self.aggregate(pipeline=self.pipeline)

        if len(result) > 0:
            result.drop(columns=['date_transaction', 'date'], inplace=True, errors='ignore')

        return result

    def get_distinct_years(self):
        self.pipeline = [
            {
                "$group": {
                    "_id": {
                        "year": {
                            "$year": "$date.dt"
                        }
                    },
                    "total": {
                        "$sum": 1
                    }
                }
            }
        ]
        result = self.exgest()

        df_result = expand_columns_of_dataframe(result, '_id')

        return df_result['year'].values


def is_var_empty(var):

    empty_var = False
    if ((type(var) is list) and (len(var) == 0)) or\
            (var is None):
        empty_var = True

    return empty_var


def join_cat_and_subcat(categories, sub_categories):

    list_cat = []
    if sub_categories is not None:
        for sub_cat in sub_categories:
            # Extract category and sub-category
            cat = sub_cat[:sub_cat.find(':')]
            sub_cat = sub_cat[sub_cat.find(':')+1:]

            # Add to the list to search
            list_cat.append((cat, sub_cat))

            # Remove category from list of categories
            if cat in categories:
                categories.remove(cat)

    for cat in categories:
        list_cat.append((cat, None))

    return list_cat




