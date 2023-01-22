from source.transactions.metadata import MetadataDB
from source.transactions.transactions_db import TransactionDB


class AccountManagerDB:
    def __init__(self, name_connection_metadata, name_connection_transaction, account_id):
        self.account_id = account_id
        self.transactions_db = TransactionDB(
            name_connection=name_connection_transaction,
            account_id=account_id,
        )

        self.metadata_db = MetadataDB(
            name_connection=name_connection_metadata,
            account_id=self.account_id,
        )
        self.metadata_db.set_from_db()

    def ingest(self, df_transactions, bank_info):

        # Insert transactions
        self.transactions_db.ingest(df_transactions)

        # Update metadata info
        self._update_metadata(bank_info)

    def delete(self, df_transactions):

        # Delete transactions
        self.transactions_db.delete(df_transactions)

        # Update metadata DB
        self._update_metadata(
            bank_info=None
        )

    def update(self, df_transactions):
        # Update transactions
        self.transactions_db.update(df_transactions)

        # Update metadata DB (new date, amount)
        self._update_metadata(
            bank_info=None
        )

    def check_consistency(self):
        balance_metadata = self.metadata_db.balance_in_db
        balance_transaction = self.transactions_db.get_balance()

        nb_transactions_metadata = self.metadata_db.nb_transactions_db
        nb_transactions_transaction = self.transactions_db.get_nb_transactions()

        latest_date_metadata = self.metadata_db.date_last_import['dt']
        latest_date_transaction = self.transactions_db.get_latest_date()

        results = dict()
        for field in ['balance', 'nb_transactions', 'latest_date']:
            val_metadata = eval(field + '_metadata')
            val_transaction = eval(field + '_transaction')
            if isinstance(val_metadata, float):
                is_same_val = round(val_metadata, 2) == round(val_transaction, 2)
            else:
                is_same_val = val_metadata == val_transaction

            results[field] = {
                'metadata': val_metadata,
                'transaction': val_transaction,
                'identical': is_same_val,
            }

        return results

    def check_with_new_transactions(self, df_transactions, bank_info):
        balance_bank = bank_info['balance']
        potential_balance = \
            sum(df_transactions['amount']) + self.metadata_db.balance_in_db + self.metadata_db.balance_bias

        result = {
            'balance_bank': round(balance_bank, 2),
            'potential_balance': round(potential_balance, 2),
            'difference': round(potential_balance, 2) - round(balance_bank, 2),
            'identical': round(balance_bank, 2) == round(potential_balance, 2)
        }

        return result

    def _update_metadata(self, bank_info):
        self.metadata_db.update_values(
            {
                # BANK
                'balance_in_bank': bank_info['balance'] \
                    if bank_info is not None else self.metadata_db.balance_in_bank,
                'date_balance_in_bank': bank_info['date'] \
                    if bank_info is not None else self.metadata_db.date_balance_in_bank['dt'],

                # DATABASE
                'balance_in_db': self.transactions_db.get_balance(),
                'nb_transactions_db': self.transactions_db.get_nb_transactions(),
                'date_last_import': self.transactions_db.get_latest_date(),
            }
        )
        self.metadata_db.update_db()

    def add_new_category(self, new_category, parent_category=None):

        # Add category in Metadata
        self.metadata_db.add_category(
            new_category=new_category,
            name_parent_category=parent_category,
        )

    def _remove_category(self, category_to_remove, parent_category):

        # Remove category in Metadata
        self.metadata_db.remove_category(
            category_to_remove=category_to_remove,
            parent_category=parent_category,
        )

    def update_category_properties(self, name_category, name_parent_category, new_category):

        # Update category properties in Metadata
        self.metadata_db.update_category_properties(
            name_category=name_category,
            name_parent_category=name_parent_category,
            new_category=new_category,
        )

    def move_category(self, name_category, name_current_parent, name_new_parent):

        if name_current_parent is None:
            Warning("It's impossible to move a parent category !")
        else:

            self.metadata_db.move_category(
                name_category=name_category,
                name_current_parent_category=name_current_parent,
                name_new_parent_category=name_new_parent,
            )
