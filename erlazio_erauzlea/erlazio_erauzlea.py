from .sailkatzailea import Ebaluaketa, Sampling, HiperparametroOptimizadorea, EzaugarriErauzlea
from .corpus import testu_prozesaketa

from sklearn.svm import LinearSVC
from itertools import permutations

import pickle as pk
import numpy as np
import pandas as pd


class ErlazioErauzlea:

    def __init__(self, domeinuko_terminoak):
        self._egokitua = False
        self.terminoak = domeinuko_terminoak
        self.klase_izenak = [
            'AtLocation',
            'IsA',
            'PartOf',
            'UsedFor',
            'Nil'
        ]

    def egokitu(self, train_set, dev_set, tokens, lemmas,
                pos=None, izen_lexikografikoak=None,
                mota='zhou', laginketa=True, optimizatu=True,
                argumentuen_arteko_distantzia=10, ezaugarri_atalasea=0,
                optimizazio_iterazio_kop=25, verbose=False):

        # Gorde beharrezko informazioa klaseko aldagai bezela
        self.izen_lexikografikoak = izen_lexikografikoak
        self.argumentuen_arteko_distantzia = argumentuen_arteko_distantzia
        self.ezaugarri_atalasea = ezaugarri_atalasea

        # Ezaugarri erauzlea definitu
        self.erauzlea = EzaugarriErauzlea(izen_lexikografikoak, ezaugarrien_agerpen_atalasea=ezaugarri_atalasea,
                                          ezaugarri_mota=mota,
                                          argumentuen_arteko_distantzia=argumentuen_arteko_distantzia)

        # Ezaugarria erauzi datasetetatik
        print("Ezaugarriak erauzten...", end="", flush=True)
        X_train, y_train, _ = self.erauzlea.egokitu_eta_eraldatu(train_set, tokens, lemmas, pos)
        X_dev, y_dev, _ = self.erauzlea.eraldatu(dev_set, tokens, lemmas, pos)
        print("erauzita! {} ezaugarri.".format(X_train.shape[1]))

        # Laginketa
        if laginketa:
            print("Laginketa aplikatzen...", end="", flush=True)
            sampler = Sampling()
            X_train, y_train = sampler.adibide_sintetikoak_sortu(X_train, y_train)
            print("Ondo!")

        # Hiperparamtro optimizazioa
        if optimizatu:
            print("Hiperparametroak optimizatzen...", end="", flush=True)
            opt = HiperparametroOptimizadorea()
            self._C, _ = opt.optimizatu(X_train, X_dev, y_train, y_dev, iterazio_kop=optimizazio_iterazio_kop)
            print("Ondo! C={}.".format(self._C))
        else:
            self._C = 1.0

        self.clf = LinearSVC(C=self._C)

        # Ebaluatzailea sortuta
        self.ebaluatzailea = Ebaluaketa(LinearSVC(C=self._C), X_train, X_dev, y_train, y_dev)
        print('Sailkatzailea egokituta:')
        print('Doitasuna:{}, Estaldura:{}, F1-Neurria:{}'.format(*self.ebaluatzailea.precision_recall_fscore()))

        # Sailkatzailea entrenatu
        self.clf.fit(X_train, y_train)

        self._egokitua = True

    def __terminoak_bilatu(self, lemmak):
        lemmak_b = [l.split() for l in lemmak]
        result = [[] for _ in range(len(lemmak_b))]

        for i, esaldia in enumerate(lemmak_b):
            for lemma in esaldia:
                if lemma in self.terminoak:
                    result[i].append(lemma)

        return result

    def __hautagai_posibleak(self, esaldi_termino_zerrenda):
        result = []

        for esaldi, termino_zerrenda in enumerate(esaldi_termino_zerrenda):
            result.extend([(esaldi, termino_pare) for termino_pare in permutations(termino_zerrenda, 2)])

        return result

    def __erlazioen_noranzkoa_zuzendu(self, datuak):

        def konparatu_tripletak(row, datuak):
            bestea = datuak.query("arg1 == '{}' and arg2 == '{}' and rel == '{}' and docid == '{}'".format(row.arg2, row.arg1, row.rel, row.docid)).reset_index()
            if len(bestea) > 0:
                bestea = bestea.loc[0]
            else:
                return row

            if bestea.konfiantza > row.konfiantza and not bestea.rel == 'Nil':
                row.rel = 'Nil'
                row.konfiantza = -np.inf

            return row

        datuak = datuak.apply(konparatu_tripletak, axis=1, args=(datuak,))

        return datuak

    def erlazioak_erauzi(self, testua, konfiantza_faktorea=0.0, noranzkoa_zuzendu=True):
        if not self._egokitua:
            raise Exception('Erlazio-erauzlea ez dago egokitua.')

        # Testua prozesatu
        token, lemma, pos = testu_prozesaketa.prozesatu_esaldiak(testua)

        # Aurkitu terminoak
        term_per_sent = self.__terminoak_bilatu(lemma)

        # Posible erlaziodun hautagaiak
        posibleak = self.__hautagai_posibleak(term_per_sent)

        # Datuak prestatu
        tokens = pd.DataFrame({'tokens': token})
        lemmas = pd.DataFrame({'lemmas': lemma})
        pos_etiketak = pd.DataFrame({'pos': pos})
        tripletak = {
            'arg1': [],
            'arg2': [],
            'docid': [],
            'rel': 'Nil'
        }
        for hautagai in posibleak:
            tripletak['arg1'].append(hautagai[1][0])
            tripletak['arg2'].append(hautagai[1][1])
            tripletak['docid'].append(hautagai[0])

        datuak = pd.DataFrame(tripletak)

        # Ezaugarriak erauzi
        X, _, datuak = self.erauzlea.eraldatu(datuak, tokens, lemmas, pos_etiketak)

        # Sailkapena egin
        y = self.clf.predict(X)
        df = self.clf.decision_function(X)

        # Konfiantza faktorera iristen ez direnak NIL bezela markatu
        y[np.max(df, axis=1) < konfiantza_faktorea] = 4
        df[np.max(df, axis=1) < konfiantza_faktorea] = -np.inf

        y = list(map(lambda x: self.klase_izenak[x], y))

        datuak['rel'] = y
        datuak['konfiantza'] = np.max(df, axis=1)

        if noranzkoa_zuzendu:
            datuak = self.__erlazioen_noranzkoa_zuzendu(datuak)

        tokens.reset_index(inplace=True)
        datuak = datuak.merge(tokens, left_on='docid', right_on='index')
        del datuak['docid']
        del datuak['index']

        return datuak

    @staticmethod
    def kargatu_bertsio_zahar_batetik(path):
        zaharra = ErlazioErauzlea.kargatu(path)

        berria = ErlazioErauzlea(zaharra.terminoak)
        berria.izen_lexikografikoak = zaharra.izen_lexikografikoak
        berria.argumentuen_arteko_distantzia = zaharra.argumentuen_arteko_distantzia
        berria.ezaugarri_atalasea = zaharra.ezaugarri_atalasea

        berria.erauzlea = zaharra.erauzlea
        berria._C = zaharra._C
        berria.ebaluatzailea = zaharra.ebaluatzailea
        berria.clf = zaharra.clf

        berria._egokitua = True

        return berria


    @staticmethod
    def kargatu(path):
        with open(path, 'rb') as fitx:
            return pk.load(fitx)

    def gorde(self, path):
        with open(path, 'wb') as fitx:
            pk.dump(self, fitx)
