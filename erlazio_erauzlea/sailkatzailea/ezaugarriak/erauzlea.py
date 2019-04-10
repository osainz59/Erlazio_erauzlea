import numpy as np
from scipy import sparse as sp
from collections import Counter

from erlazio_erauzlea.sailkatzailea.ezaugarriak import zhou, mintz


class EzaugarriErauzlea:

    def __init__(self, izen_lexikografikoak=None,
                 ezaugarri_hiztegia=None, argumentuen_arteko_distantzia=20,
                 ezaugarrien_agerpen_atalasea=0,
                 ezaugarri_mota = 'zhou'):

        if ezaugarri_mota == 'zhou' and izen_lexikografikoak is None:
            raise Exception('Zhou ezaugarrientzako beharrezkoak dira Izen lexikografikoak.')

        self._tokens = None
        self._lemmas = None
        self._pos = None
        self._izen_lexikografikoak = izen_lexikografikoak
        self._ezaugarri_hiztegia = ezaugarri_hiztegia
        self._label2id = None
        self._egokitua = False
        self._mota = ezaugarri_mota

        # Konfigurazioa
        self._arg_dist = argumentuen_arteko_distantzia
        self._atalasea = ezaugarrien_agerpen_atalasea

    @staticmethod
    def __lortu_argumentuen_posizioak(arg1, arg2, lemmas):
        """
        Bi argumentuen esaldian duten posizioa itzultzen du.

        :param arg1: Lehenengo argumentua.
        :param arg2: Bigarren argumentua.
        :param lemmas: Esaldia lemmatizatua.
        :return: Bi argumentuen esaldian duten posizioa itzultzen du.
        """

        # Hasieraketak
        arg1_pos, arg2_pos = [], []

        # Multiword-ak identifikatu
        arg1_s, arg2_s = arg1.split(), arg2.split()
        arg1_l, arg2_l = len(arg1_s), len(arg2_s)
        for index, lemma in enumerate(lemmas):
            try:
                if len(lemma) < 3: continue
                if arg1_s[0] in lemma or lemma in arg1_s[0]:
                    if all([arg1_s[i] in lemmas[index + i] or lemmas[index + i] in arg1_s[i] for i in range(arg1_l)]):
                        arg1_pos.append(index)
                if arg2_s[0] in lemma or lemma in arg2_s[0]:
                    if all([arg2_s[i] in lemmas[index + i] or lemmas[index + i] in arg2_s[i] for i in range(arg2_l)]):
                        arg2_pos.append(index)

            # Index erroreak tratatzeko
            except:
                continue

        tuplak = []
        for x in arg1_pos:
            for y in arg2_pos:
                tuplak.append((x, y))
        try:
            result = min([(abs(x - y), x, y) for x, y in tuplak], key=lambda x: x[0])
        except:
            raise Exception('Argumentuak ez dira aurkitu!')

        return result

    def __lortu_lerroaren_ezaugarriak(self, lerroa, feature_dict=None):
        try:
            docid = int(lerroa['docid'])
            arg1 = lerroa['arg1']
            arg2 = lerroa['arg2']
            tokens, lemmas = self._tokens.loc[docid][0].split(), self._lemmas.loc[docid][0].split()
            if self._mota == 'mintz':
                pos = self._pos.loc[docid][0].split()

            distantzia, arg1_pos, arg2_pos = self.__lortu_argumentuen_posizioak(arg1, arg2, lemmas)

            if distantzia > self._arg_dist:
                return None

            # Kalkulatu zatiguneak
            if arg1_pos <= arg2_pos:
                a1, a2 = arg1, arg2
                a, b, c, d = arg1_pos, arg1_pos + len(arg1.split()), arg2_pos, arg2_pos + len(arg2.split())
            else:
                a1, a2 = arg2, arg1
                a, b, c, d = arg2_pos, arg2_pos + len(arg2.split()), arg1_pos, arg1_pos + len(arg1.split())

            if self._mota == 'zhou':
                features = zhou.lortu_ezaugarri_guztiak(arg1_pos, arg2_pos,
                                                        a, b, c, d, a1, a2,
                                                        tokens, self._izen_lexikografikoak)
            elif self._mota == 'mintz':
                features = mintz.lortu_ezaugarri_guztiak(arg1_pos, arg2_pos,
                                                         a, b, c, d,
                                                         tokens, pos)
            else:
                features = []

            if feature_dict is not None:
                for feature in features:
                    feature_dict[feature] = feature_dict.get(feature, 0) + 1

            return features, lerroa['rel']

        except Exception:
            return None

    def egokitu(self, X, tokens, lemmas, pos=None, verbose=False):
        """

        :param X: Tripleten adibideen DataFrame-a [arg1, arg2, rel, docid] egiturarekin.
        :param verbose: Trazak erakutsi edo ez boolearra.
        """

        self._tokens = tokens
        self._lemmas = lemmas
        self._pos = pos

        if self._mota == 'mintz' and pos is None:
            raise Exception('Mintz ezaugarrientzako beharrezkoa da POS argumentua.')

        ezaugarri_hiztegia = Counter()
        self._label2id = {label: i for i, label in enumerate(X.rel.unique())}

        # Lortu lerro bakoitzeko ezaugarriak
        for index, row in X.iterrows():
            if verbose & (index % 500 == 0):
                print(index)

            emaitza = self.__lortu_lerroaren_ezaugarriak(row, ezaugarri_hiztegia)
            if emaitza is None:
                continue

        # Ezaugarrien garbiketa agerpen kopuruarekiko
        self._ezaugarri_hiztegia = dict()
        index = 0
        for key, value in ezaugarri_hiztegia.items():
            if value > self._atalasea:
                self._ezaugarri_hiztegia[key] = index
                index += 1

        self._egokitua = True

    def egokitu_eta_eraldatu(self, X, tokens, lemmas, pos=None, verbose=False):
        """

        :param X: Tripleten adibideen DataFrame-a [arg1, arg2, rel, docid] egiturarekin.
        :param pos:
        :param lemmas:
        :param tokens:
        :param verbose: Trazak erakutsi edo ez boolearra.
        :return ezaugarriak: Eraldatutako ezaugarri matrizea.
        :return klaseak: Klase aldagaiaren bektorea.
        :return X_iragazia: Gelditutako dataseta.
        """

        self._tokens = tokens
        self._lemmas = lemmas
        self._pos = pos

        if self._mota == 'mintz' and pos is None:
            raise Exception('Mintz ezaugarrientzako beharrezkoa da POS argumentua.')

        ezaugarri_lista, klase_lista, indize_lista = [], [], []
        ezaugarri_hiztegia = Counter()
        self._label2id = {label: i for i, label in enumerate(X.rel.unique())}

        # Lortu lerro bakoitzeko ezaugarriak
        for index, row in X.iterrows():
            if verbose & (index % 500 == 0):
                print(index)

            emaitza = self.__lortu_lerroaren_ezaugarriak(row, ezaugarri_hiztegia)
            if emaitza is None:
                continue

            ezaugarri, klase = emaitza
            ezaugarri_lista.append(ezaugarri)
            klase_lista.append(self._label2id[klase])
            indize_lista.append(index)

        if not ezaugarri_lista:
            return

        # Ezaugarrien garbiketa agerpen kopuruarekiko
        self._ezaugarri_hiztegia = dict()
        index = 0
        for key, value in ezaugarri_hiztegia.items():
            if value > self._atalasea:
                self._ezaugarri_hiztegia[key] = index
                index += 1

        self._egokitua = True

        # Sortu ezaugarri matrizea
        ezaugarriak, klaseak, indizeak = [], [], []
        for ind, ezaugarri, klase in zip(indize_lista, ezaugarri_lista, klase_lista):
            ezaugarri_bektorea = np.zeros(index)
            ezaugarri_bektorea[[self._ezaugarri_hiztegia[f] for f in ezaugarri if f in self._ezaugarri_hiztegia]] = 1

            if not np.sum(ezaugarri_bektorea):
                continue

            ezaugarriak.append(sp.csr_matrix(ezaugarri_bektorea))
            klaseak.append(klase)
            indizeak.append(ind)

        ezaugarriak = sp.vstack(ezaugarriak)
        klaseak = np.array(klaseak)
        X = X.loc[indizeak]

        return ezaugarriak, klaseak, X

    def eraldatu(self, X, tokens, lemmas, pos=None, verbose=False):
        """

        :param X: Tripleten adibideen DataFrame-a [arg1, arg2, rel, docid] egiturarekin.
        :param verbose: Trazak erakutsi edo ez boolearra.
        :return ezaugarriak: Eraldatutako ezaugarri matrizea.
        :return klaseak: Klase aldagaiaren bektorea.
        :return X_iragazia: Gelditutako dataseta.
        """

        if not self._egokitua:
            raise Exception('Lehendabizi egokitu.')

        self._tokens = tokens
        self._lemmas = lemmas
        self._pos = pos

        if self._mota == 'mintz' and pos is None:
            raise Exception('Mintz ezaugarrientzako beharrezkoa da POS argumentua.')

        ezaugarri_lista, klase_lista, indize_lista = [], [], []

        # Lortu lerro bakoitzeko ezaugarriak
        for index, row in X.iterrows():
            if verbose & (index % 500 == 0):
                print(index)

            emaitza = self.__lortu_lerroaren_ezaugarriak(row, {})
            if emaitza is None:
                continue

            ezaugarri, klase = emaitza
            ezaugarri_lista.append(ezaugarri)
            klase_lista.append(self._label2id[klase])
            indize_lista.append(index)

        # Sortu ezaugarri matrizea
        ezaugarriak, klaseak, indizeak = [], [], []
        for ind, ezaugarri, klase in zip(indize_lista, ezaugarri_lista, klase_lista):
            ezaugarri_bektorea = np.zeros(len(self._ezaugarri_hiztegia))
            ezaugarri_bektorea[[self._ezaugarri_hiztegia[f] for f in ezaugarri if f in self._ezaugarri_hiztegia]] = 1

            if not np.sum(ezaugarri_bektorea):
                continue

            ezaugarriak.append(sp.csr_matrix(ezaugarri_bektorea))
            klaseak.append(klase)
            indizeak.append(ind)

        ezaugarriak = sp.vstack(ezaugarriak)
        klaseak = np.array(klaseak)
        X = X.loc[indizeak]

        return ezaugarriak, klaseak, X

    def lortu_ezaugarri_hiztegia(self):
        """
        Itzuli Ezaugarri : Id hiztegia.

        :return: Itzuli Ezaugarri : Id hiztegia.
        """
        return self._ezaugarri_hiztegia
