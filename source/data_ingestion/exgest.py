import pandas as pd


class TransactionExgest:
    def __init__(self, mongodb_connection):
        self.connection = mongodb_connection

        # Method use for the exgestion: "search" or "pipeline"
        self.exgestion_method = None

        self.attributes = ['account_id', 'date', 'description',
                           'amount', 'type_transaction',
                           'category', 'sub_category', 'occasion', 'check',
                           'date_transaction']
        self.account_id = None
        self.date = []
        self.description = None
        self.amount = []
        self.type_transaction = None
        self.category = None
        self.sub_category = None
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
        self.category = dict_searches.get('category', None)
        self.sub_category = dict_searches.get('sub_category', None)
        self.occasion = dict_searches.get('occasion', None)
        self.date_transaction = dict_searches.get('date_transaction', [])
        self.check = dict_searches.get('check', None)

        # Generate the pipeline
        self.create_pipeline_from_search_criteria()

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

    def exgest_all(self):
        return pd.DataFrame(list(self.connection.collection.find()))

    def aggregate(self, pipeline):
        if len(pipeline) == 0:
            result = pd.DataFrame()
        else:
            result = pd.DataFrame(list(self.connection.collection.aggregate(pipeline)))
        return result

    def create_pipeline_from_search_criteria(self):
        self.pipeline = []

        for att in self.attributes:
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


def is_var_empty(var):

    empty_var = False
    if ((type(var) is list) and (len(var) == 0)) or\
            (var is None):
        empty_var = True

    return empty_var


