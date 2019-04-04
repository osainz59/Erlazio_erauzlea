import pandas as pd
import numpy as np
from gensim import corpora, models
import pickle as pk

from math import log


class TerminoakLDA:

    def __init__(self):
        self._lda = None
        self._tf = None
        self._prob = None
        self._terminoak = None

    @staticmethod
    def __irakurri_artikuloak(input, sep='\t', encoding='utf-8', header=-1):
        df = pd.read_csv(input, sep=sep, encoding=encoding, header=header)
        # return np.array(df[1], dtype='U')
        return df[1].values.astype('U')

    def __lortu_lda(self, text_data, save_path=None, num_topics=100):
        hiztegia = corpora.Dictionary(text_data)
        corpus = [hiztegia.doc2bow(text) for text in text_data]

        ldamodel = models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=hiztegia, passes=15, random_state=42)

        if save_path:
            with open(save_path + "/lda_corpus.pkl", 'wb') as f:
                pk.dump(corpus, f)
            hiztegia.save(save_path + "hiztegia.gensim")
            ldamodel.save(save_path + "ldamodel_{}.gensim".format(num_topics))

        self._lda = {
            'hiztegia': hiztegia,
            'corpus': corpus,
            'modeloa': ldamodel
        }

    def __lortu_prob(self):
        hiztegia = self._lda['hiztegia']
        ldamodel = self._lda['modeloa']

        def prob_handiena(x):
            if len(x) > 0:
                return x[0][1]
            return 0

        prob = np.zeros(len(hiztegia))
        for i in hiztegia.keys():
            prob[i] = prob_handiena(ldamodel.get_term_topics(i))

        self._prob = prob

    def __lortu_tf(self):
        tf = np.zeros(len(self._lda['hiztegia']))
        for artikuloa in self._lda['corpus']:
            for hitza in artikuloa:
                tf[hitza[0]] += hitza[1]

        self._tf = tf

    def lortu_lda(self):
        if not self._lda:
            raise Exception("Terminoak ez dira oraindik erauzi.")
        return self._lda

    def lortu_prob(self):
        if not self._prob:
            raise Exception("Terminoak ez dira oraindik erauzi.")
        return self._prob

    def lortu_tf(self):
        if not self._tf:
            raise Exception("Terminoak ez dira oraindik erauzi.")
        return self._tf

    def erauzi_terminoak(self, fitxategi_izena, verbose=False, **kwargs):
        # Kargatu fitxategia
        text_data = [artikuloa.split() for artikuloa in self.__irakurri_artikuloak(fitxategi_izena, **kwargs)]
        if verbose:
            print("Fitxategia irakurria.")

        self.__lortu_lda(text_data, **kwargs)
        if verbose:
            print("LDA sortuta.")

        self.__lortu_prob()
        if verbose:
            print("Probabilitateak lortuta")

        self.__lortu_tf()
        if verbose:
            print("TF lortuta.")

        data = {
            'Keys' : self._lda['hiztegia'].keys(),
            'Values' : list(self._lda['hiztegia'].values())
        }
        df = pd.DataFrame(data)
        df.set_index('Keys', inplace=True)
        df['TF'] = pd.Series(self._tf).apply(lambda x: log(x, 10))
        df['PROB'] = pd.Series(self._prob)

        df['Termhood'] = df['TF'] * df['PROB']

        df = df[ df['Termhood'] > 0 ].sort_values('Termhood', ascending=False)

        if verbose:
            print("Hiztegi osoaren luzeera: {}".format(len(df)))
            print(df.head())

        self._terminoak = df.Values.values

        return self._terminoak, df
