import pandas as pd


def expand_columns_of_dataframe(df, column):
    df_column = pd.json_normalize(df[column])

    df_merge = pd.concat([df, df_column], axis=1)
    df_merge.drop(columns=[column], inplace=True)

    return df_merge
