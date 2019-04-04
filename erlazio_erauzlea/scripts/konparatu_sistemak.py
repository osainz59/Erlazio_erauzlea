import warnings

warnings.filterwarnings('ignore')

import argparse
from itertools import product
from collections import OrderedDict

import pandas as pd
import matplotlib.pyplot as plt

from multiprocessing import Pool
from functools import partial

from erlazio_erauzlea.sailkatzailea import Sampling, HiperparametroOptimizadorea, EzaugarriErauzlea
from erlazio_erauzlea.sailkatzailea import Ebaluaketa
from erlazio_erauzlea.sailkatzailea.ebaluaketa import precision_recall_kurba_anizkoitza
from sklearn.svm import LinearSVC

# Paralelizazioa
NUMBER_OF_PROCESS = 4


def lortu_ebaluaketa(konf, X_train, y_train, X_dev, y_dev):
    print(konf)
    izena = konf["mota"]

    if konf["laginketa"]:
        izena += '-sampling'
        print("{}-Trainset-a orekatu adibide berriak sortuz sintetikoki...".format(konf))
        sampler = Sampling()
        X_train_, y_train_ = sampler.adibide_sintetikoak_sortu(X_train[konf["mota"]], y_train[konf["mota"]])
        print("{}-Okey".format(konf))
    else:
        X_train_, y_train_ = X_train[konf["mota"]], y_train[konf["mota"]]

    if konf["parametro-opt"]:
        izena += '-opt'
        print("{}-Sailkatzailearen hyperparametroak optimizatu...".format(konf))
        opt = HiperparametroOptimizadorea()
        C, _ = opt.optimizatu(X_train_,
                              X_dev[konf["mota"]],
                              y_train_,
                              y_dev[konf["mota"]], iterazio_kop=10)
        print("{}-Okey".format(konf))
        clf = LinearSVC(C=C)
    else:
        clf = LinearSVC()

    result = Ebaluaketa(clf, X_train_, X_dev[konf["mota"]], y_train_, y_dev[konf["mota"]])
    result.save('modeloak/' + izena + '.pkl')

    return izena, result


def konparatu_sistemak(tokens, lemmas, pos, il, train, dev, atalasea, cores=NUMBER_OF_PROCESS, verbose=False):
    print("Corpusa kargatu...", end="", flush=True)
    tokens = pd.read_csv(tokens, sep='\t', compression='bz2', index_col=0, encoding='latin-1')
    lemmas = pd.read_csv(lemmas, sep='\t', compression='bz2', index_col=0, encoding='latin-1')
    pos = pd.read_csv(pos, sep='\t', compression='bz2', index_col=0, encoding='latin-1')
    izen_lexikografikoak = pd.read_csv(il, sep='\t')
    izen_lexikografikoak = izen_lexikografikoak.set_index('word').T.to_dict('list')

    train = pd.read_csv(train, sep='\t')
    dev = pd.read_csv(dev, sep='\t')
    print("Okey!")

    sistemen_konfigurazioak = OrderedDict()
    sistemen_konfigurazioak['mota'] = ['mintz', 'zhou']
    sistemen_konfigurazioak['laginketa'] = [False, True]
    sistemen_konfigurazioak['parametro-opt'] = [False, True]

    sistemen_konfigurazioak = [{'mota': mota, 'laginketa': samp, 'parametro-opt': param}
                               for mota, samp, param in list(product(*sistemen_konfigurazioak.values()))]

    # Sortu erauzlearen instantzia
    print("Ezaugarri erauzlea sortu eta egokitu...", end="", flush=True)
    erauzlea_mintz = EzaugarriErauzlea(izen_lexikografikoak, ezaugarrien_agerpen_atalasea=atalasea,
                                       ezaugarri_mota='mintz')
    erauzlea_zhou = EzaugarriErauzlea(izen_lexikografikoak, ezaugarrien_agerpen_atalasea=atalasea,
                                      ezaugarri_mota='zhou')

    # fit_transform
    X_train, y_train, X_dev, y_dev = {}, {}, {}, {}
    X_train["mintz"], y_train["mintz"], _ = erauzlea_mintz.egokitu_eta_eraldatu(train, tokens, lemmas, pos)
    X_train["zhou"], y_train["zhou"], _ = erauzlea_zhou.egokitu_eta_eraldatu(train, tokens, lemmas, pos)
    X_dev["mintz"], y_dev["mintz"], _ = erauzlea_mintz.eraldatu(dev, tokens, lemmas, pos)
    X_dev["zhou"], y_dev["zhou"], _ = erauzlea_zhou.eraldatu(dev, tokens, lemmas, pos)
    print("Okey!")

    # Memoria garbitu
    del tokens, lemmas, pos, train, dev, izen_lexikografikoak, erauzlea_mintz, erauzlea_zhou

    if cores > 1:
        with Pool(NUMBER_OF_PROCESS) as pool:
            result = pool.map(partial(lortu_ebaluaketa, X_train=X_train, y_train=y_train, X_dev=X_dev, y_dev=y_dev),
                              sistemen_konfigurazioak)
    else:
        result = [lortu_ebaluaketa(konf, X_train=X_train, y_train=y_train, X_dev=X_dev, y_dev=y_dev) for konf in
                  sistemen_konfigurazioak]

    modeloak = {izena: modeloa for izena, modeloa in result}

    # Ebaluatu sailkatzaileak
    precision_recall_kurba_anizkoitza(modeloak)
    plt.savefig('irudiak/sistemen_arteko_precision_recall_kurba.png')


def main():
    # Argumentuak jaso
    parser = argparse.ArgumentParser(prog="train_eval", description="Erlazio erauzlea entrenatu eta ebaluatu.")
    parser.add_argument('-tokens', type=str, dest='tokens',
                        help="Token fitxategiaren path-a.")
    parser.add_argument('-lemmas', type=str, dest='lemmas',
                        help="Lemma fitxategiaren path-a.")
    parser.add_argument('-pos', type=str, dest='pos',
                        help="POS fitxategiaren path-a.", default=None)
    parser.add_argument('-il', type=str, dest='il',
                        help="Izen-lexikografikoen fitxategiaren path-a.", default=None)
    parser.add_argument('-train', type=str, dest='train',
                        help="Entrenamendurako datasetaren path-a")
    parser.add_argument('-dev', type=str, dest='dev',
                        help="Developmenterako datasetaren path-a")
    parser.add_argument('-ezaugarri_atalasea', type=int, dest='atalasea',
                        help="Ezaugarrien agerpen kopuru minimoa.", default=0)
    parser.add_argument('-verbose', action='store_true', default=False)

    args = parser.parse_args()
    # Argumentuak ondo jaso direla ziurtatu
    if args.tokens is None:
        raise IOError('Token fitxategia beharrezko argumentu bat da.')

    if args.lemmas is None:
        raise IOError('Lemma fitxategia beharrezko argumentu bat da.')

    if args.pos is None:
        raise IOError('POS fitxategia beharrezko argumentu bat da mintz ezaugarrientzako.')

    if args.il is None:
        raise IOError('Izen Lexikografikoko fitxategia beharrezko argumentu bat da mintz ezaugarrientzako.')

    if args.train is None:
        raise IOError('Train fitxategia beharrezko argumentu bat da.')

    if args.dev is None:
        raise IOError('Dev fitxategia beharrezko argumentu bat da.')

    # Deitu funtzioari
    konparatu_sistemak(**vars(args))


if __name__ == "__main__":
    main()
