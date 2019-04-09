import pandas as pd
import json
import numpy as np


def kalkulatu_erlazioen_adibide_proportzioa(dataseta):
    return dataseta.groupby('rel').count().docid / len(dataseta)


def __kfold(dataset, k=5, debug=False):
    def kfold_over_class(splitted_dataframe, k=5):
        lists = [[] for _ in range(k)]
        groups = splitted_dataframe.groupby(['arg1', 'arg2']).groups
        g_bysize = sorted([(key, len(value)) for key, value in groups.items()], key=lambda x: x[1], reverse=True)

        for key, _ in g_bysize:
            l = min(lists, key=len)
            l.extend(groups[key].values)

        return list(map(pd.Int64Index, lists))

    df_list = [dataset.loc[indexes] for key, indexes in dataset.groupby('rel').groups.items()]
    folds = [pd.Int64Index([]) for _ in range(k)]
    folds_stats = []
    for i, kfold_per_class in enumerate(map(lambda df: kfold_over_class(df, k), df_list)):
        folds_stats.append([])
        for j, index in enumerate(kfold_per_class):
            folds_stats[i].append(len(index))
            folds[j] = folds[j].union(index)

    if debug:
        percent = [[stat / len(fold) for stat, fold in zip(stats, folds)] for stats in folds_stats]

        for i, p in enumerate(percent):
            print('{} class percent per fold: {}'.format(i, list(map(lambda x: "{}%".format(round(100 * x, 2)), p))))

    return folds


def split_dataset(dataset):
    folds_index = __kfold(dataset, k=10, debug=False)
    dataset_folds = [dataset.loc[fold].reset_index()[['arg1', 'arg2', 'docid', 'rel']] for fold in folds_index]

    train_set = pd.concat(dataset_folds[0:7], axis=0).reset_index()[['arg1', 'arg2', 'docid', 'rel']]
    dev_set = pd.concat(dataset_folds[7:9], axis=0).reset_index()[['arg1', 'arg2', 'docid', 'rel']]
    test_set = pd.concat(dataset_folds[9:], axis=0).reset_index()[['arg1', 'arg2', 'docid', 'rel']]

    return train_set, dev_set, test_set


def __to_dict(argumentua, id2term):
    return {'word': argumentua, 'id': id2term[argumentua]}


def dataset_to_json(dataset, tokens, id2term):

    new_df = pd.DataFrame()

    tokens = tokens.reset_index()
    df = dataset.merge(tokens, left_on='docid', right_on='index')

    new_df['head'] = df['arg1'].apply(__to_dict, args=(id2term,))
    new_df['tail'] = df['arg2'].apply(__to_dict, args=(id2term,))
    new_df['sentence'] = df['tokens']
    new_df['relation'] = df['rel']

    df_dict = new_df.to_dict(orient='records')

    return json.dumps(df_dict, indent='\t')


def glove_to_list_of_dicts(glove_path):
    word_list = []
    with open(glove_path, 'rt') as fitx:
        for line in fitx:
            splitted_line = line.split()
            word = splitted_line[0]
            embedding = [float(val) for val in splitted_line[1:]]
            word_list.append({'word' : word, 'vec' : embedding})

    return word_list
