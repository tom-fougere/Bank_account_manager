

def check_duplicates_in_df(df1, df2):

    # Init duplicate column to False
    df1['duplicate'] = False

    if len(df2) > 0:
        for index, row in df1.iterrows():
            # Check if the same transaction exists
            df2_same = df2.loc[(df2['account_id'] == row['account_id']) &
                               (df2['amount'] == row['amount']) &
                               (df2['date_str'] == row['date_str']) &
                               (df2['date_transaction_str'] == row['date_transaction_str']) &
                               (df2['description'] == row['description'])].reset_index()

            # If transaction exists, replace values of some columns and set 'duplicate' to True
            if len(df2_same) == 1:
                column_to_copy = ['category', 'sub_category', 'occasion', 'note', 'check', 'type_transaction']
                for column in column_to_copy:
                    df1.loc[index, column] = df2_same[column][0]
                df1.loc[index, 'duplicate'] = True
            elif len(df2_same) > 1:
                raise ValueError('WARNING')


