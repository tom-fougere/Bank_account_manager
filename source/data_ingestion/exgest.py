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

            # if att == ''
            if (type(att_value) is list) and (len(att_value) >= 2):
                # if isinstance(att_value[0], datetime.datetime):
                pipeline.append({
                    "$match": {
                        "$gte": att_value[0],
                        "$lt": att_value[0]
                    }
                })
            elif type(att_value) is list:
                pass
            elif att_value is not None:
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

        pipeline.append({
            "$project": {"_id": 0}
        })

        return pipeline

    def exgest(self):
        pipeline = self.create_pipeline()
        self.aggregate(pipeline=pipeline)

    def ingest_one_transaction(self, transaction_series):

        transaction_dict = transaction_series.to_dict()
        db_trans = self.connection.collection.find({'account_id': transaction_dict['account_id'],
                                                    'date': transaction_dict['date'],
                                                    'date_transaction': transaction_dict['date_transaction'],
                                                    'amount': transaction_dict['amount']})

        if len(list(db_trans)) >= 1:
            raise ValueError('There is 1 or more documents in the DB with the same attributes: '
                             ' - account_id: {},'
                             ' - date: {},'
                             ' - date_transaction: {},'
                             ' - amount: {}'.format(transaction_dict['account_id'],
                                                    transaction_dict['date'],
                                                    transaction_dict['date_transaction'],
                                                    transaction_dict['amount']))
        else:
            self.connection.collection.insert(transaction_dict)
