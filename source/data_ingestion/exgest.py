import datetime
import pandas as pd


class TransactionExgest:
    def __init__(self, mongodb_connection, dict_searches):
        self.connection = mongodb_connection
        self.attributes = ['account_id', 'date', 'description',
                           'amount', 'type_transaction',
                           'category', 'sub_category', 'occasion', 'check',
                           'date_transaction']
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

    def exgest_all(self):
        return pd.DataFrame(list(self.connection.collection.find()))

    def aggregate(self, pipeline):
        if len(pipeline) == 0:
            result = pd.DataFrame()
        else:
            result = pd.DataFrame(list(self.connection.collection.aggregate(pipeline)))
        return result

    def create_pipeline(self):
        pipeline = []

        for att in self.attributes:
            att_value = getattr(self, att)

            if is_var_empty(att_value) is False:

                # Manage dates
                if 'date' in att:
                    pipeline.append({
                        "$match": {
                            '.'.join([att, 'dt']): {"$gte": att_value[0].isoformat(),
                                                    "$lte": att_value[1].isoformat()}
                        }
                    })
                # Manage numeric value
                elif 'amount' in att:
                    pipeline.append({
                        "$match": {
                            att: {"$gte": min(att_value[0], att_value[1]),
                                  "$lte": max(att_value[0], att_value[1])}
                        }
                    })
                # Manage description
                elif 'description' in att:
                    pipeline.append({
                        "$match": {
                            att: {"$regex": ''.join(['/*', att_value, '/*']), "$options": 'i'}
                        }
                    })
                else:
                    pipeline.append({
                        "$match": {
                            att: att_value
                        }})

        pipeline.append({
            "$addFields": {
                "date_str": "$date.str",
                "date_dt": "$date.dt",
                "date_transaction_str": "$date_transaction.str",
                "date_transaction_dt": "$date_transaction.st",
            }
        })

        # if len(pipeline) > 1:
        #     pipeline.append({
        #         "$project": {"_id": 0}
        #     })

        return pipeline

    def exgest(self):
        pipeline = self.create_pipeline()
        result = self.aggregate(pipeline=pipeline)

        return result


def is_var_empty(var):

    empty_var = False
    if ((type(var) is list) and (len(var) == 0)) or\
            (var is None):
        empty_var = True

    return empty_var


