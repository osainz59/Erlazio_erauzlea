from math import log
import pandas as pd


def __pmi(row, df):
    n = len(df)
    c_e1e2 = len(df.query('arg1 == "' + row['arg1'] + '" and arg2 == "' + row['arg2'] + '"'))
    c_e1 = len(df.query('arg1 == "' + row['arg1'] + '"'))
    c_e2 = len(df.query('arg2 == "' + row['arg2'] + '"'))

    return log((c_e1e2 * n) / (c_e1 * c_e2), 2)


def pmi_iragazketa(dataset, atalasea=3.5, verbose=False):
    erlazioak = list(dataset.rel.unique())

    df_emaitza = pd.DataFrame()

    for rel in erlazioak:
        if verbose:
            print(rel)
        subset = dataset.query('rel == "' + rel + '"')
        subset['PMI'] = subset.apply(__pmi, axis=1, args=(subset,))
        df_emaitza = df_emaitza.append(subset, ignore_index=True)

    return df_emaitza[df_emaitza.PMI >= atalasea]


def argumentu_berdineko_tripletak_ezabatu(df):
    return df[df.arg1 != df.arg2]


def __ezabatu(row):
    arg1 = row['arg1'].split()
    arg2 = row['arg2'].split()
    return any([a in arg2 for a in arg1])


def multiwordeko_argumentu_berdineko_tripletak_ezabatu(df):
    df['ezabatu'] = df.apply(__ezabatu, axis=1)
    df = df[df.ezabatu == False]
    del df['ezabatu']

    return df


def agerpen_gutxiko_tripletak_ezabatu(df, atalasea=10):
    iragazteko_tripletak = df.groupby(['arg1', 'arg2']).count().docid
    iragazteko_tripletak = list(iragazteko_tripletak[iragazteko_tripletak < atalasea].keys())

    return df[~df[['arg1', 'arg2']].apply(tuple, 1).isin(iragazteko_tripletak)]


def multi_instance_adibideak_iragazi(df):
    lag = df[['arg1', 'arg2', 'docid']]
    indizeak = lag.drop_duplicates().index

    return df.loc[indizeak].reset_index()[['arg1', 'arg2', 'docid', 'rel']]