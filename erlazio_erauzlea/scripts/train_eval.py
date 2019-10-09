import warnings

warnings.filterwarnings('ignore')

import argparse

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from erlazio_erauzlea.sailkatzailea import Sampling, HiperparametroOptimizadorea, EzaugarriErauzlea
from erlazio_erauzlea.sailkatzailea import Ebaluaketa
from sklearn.svm import LinearSVC


def train_eval(tokens, lemmas, pos, il, train, dev, mota, atalasea, verbose=False, param=False, sampling=False):
    print("Corpusa kargatu...", end="", flush=True)
    tokens = pd.read_csv(tokens, sep='\t', compression='bz2', index_col=0, encoding='latin-1')
    lemmas = pd.read_csv(lemmas, sep='\t', compression='bz2', index_col=0, encoding='latin-1')

    if mota == 'mintz':
        pos = pd.read_csv(pos, sep='\t', compression='bz2', index_col=0, encoding='latin-1')
        izen_lexikografikoak = None
    elif mota == 'zhou':
        izen_lexikografikoak = pd.read_csv(il, sep='\t')
        izen_lexikografikoak = izen_lexikografikoak.set_index('word').T.to_dict('list')
        pos = None
    else:
        print('Emandako ezaugarri mota ez da ezagutzen.')
        return

    train = pd.read_csv(train, sep='\t')
    dev = pd.read_csv(dev, sep='\t')

    print("Okey!")

    # Sortu erauzlearen instantzia
    print("Ezaugarri erauzlea sortu eta egokitu...", end="", flush=True)
    erauzlea = EzaugarriErauzlea(izen_lexikografikoak, ezaugarrien_agerpen_atalasea=atalasea,
                                 ezaugarri_mota=mota)

    # fit_transform
    X_train, y_train, ema = erauzlea.egokitu_eta_eraldatu(train, tokens, lemmas, pos)
    X_dev, y_dev, _ = erauzlea.eraldatu(dev, tokens, lemmas, pos)
    print("Okey!")

    # Memoria garbitu
    del tokens, lemmas, pos, train, dev, izen_lexikografikoak, erauzlea

    if sampling:
        # Sampling-a aplikatu (Memoria arazoak eman ditzake)
        print("Trainset-a orekatu adibide berriak sortuz sintetikoki...", end="", flush=True)
        sampler = Sampling()
        X_train, y_train = sampler.adibide_sintetikoak_sortu(X_train, y_train)
        print("Okey")

    if param:
        # Hyperparametroak optimizatu
        print("Sailkatzailearen hyperparametroak optimizatu...", end="", flush=True)
        opt = HiperparametroOptimizadorea()
        C, _ = opt.optimizatu(X_train, X_dev, y_train, y_dev, iterazio_kop=10)
        print("Okey")
        clf = LinearSVC(C=C)
    else:
        clf = LinearSVC()

    # Ebaluatu sailkatzailea
    ebaluaketa = Ebaluaketa(clf, X_train, X_dev, y_train, y_dev)
    ebaluaketa.konfusio_matrizea('Konfusio matrize normalizatua')
    plt.savefig('irudiak/konfusio_matrizea-{}-{}-{}.png'.format(mota, sampling, param))
    precision, recall, _ = ebaluaketa.precision_recall_kurba()
    plt.savefig('irudiak/precision_recall_kurba-{}-{}-{}.png'.format(mota, sampling, param))
    np.save('kurbak/precision_curve-{}-{}-{}.npy'.format(mota, sampling, param), precision)
    np.save('kurbak/recall_curve-{}-{}-{}.npy'.format(mota, sampling, param), recall)
    precision, recall, fscore = ebaluaketa.precision_recall_fscore()
    print("Precision: {}, Recall: {}, F-Score: {}".format(precision, recall, fscore))

    with open('train_eval_emaitzak.txt', "a") as f:
        f.write("Mota: {}, Sampling: {}, Parametro-finketa: {} --> Precision: {}, Recall: {}, FScore: {}\n".format(
            mota, sampling, param, precision, recall, fscore
        ))


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
    parser.add_argument('-mota', type=str, dest='mota',
                        help="Ezaugarrien mota: mintz edo zhou.", default='zhou')
    parser.add_argument('-ezaugarri_atalasea', type=int, dest='atalasea',
                        help="Ezaugarrien agerpen kopuru minimoa.", default=0)
    # parser.add_argument('-emaitzak', type=str, dest='emaitzak',
    #                    help="Prozesuan lortutako balioen emaitzak gordetzeko fitxategia.")
    parser.add_argument('-verbose', action='store_true', default=False)
    parser.add_argument('-sampling', action='store_true', default=False)
    parser.add_argument('-param', action='store_true', default=False)

    args = parser.parse_args()
    # Argumentuak ondo jaso direla ziurtatu
    if args.tokens is None:
        raise IOError('Token fitxategia beharrezko argumentu bat da.')

    if args.lemmas is None:
        raise IOError('Lemma fitxategia beharrezko argumentu bat da.')

    if args.mota is 'mintz' and args.pos is None:
        raise IOError('POS fitxategia beharrezko argumentu bat da mintz ezaugarrientzako.')

    if args.mota is 'zhou' and args.il is None:
        raise IOError('Izen Lexikografikoko fitxategia beharrezko argumentu bat da mintz ezaugarrientzako.')

    if args.train is None:
        raise IOError('Train fitxategia beharrezko argumentu bat da.')

    if args.dev is None:
        raise IOError('Dev fitxategia beharrezko argumentu bat da.')

    # Deitu funtzioari
    train_eval(**vars(args))


if __name__ == "__main__":
    main()
