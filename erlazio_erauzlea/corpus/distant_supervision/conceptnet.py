import pandas as pd
import numpy as np


class ConceptNet:
    """ ConceptNet csv-a iragazteko funtzioak.

    Aurrebaldintza:
        Hizkuntza bakarreko tripletak erauzi:
        Erabili: grep ".*\/en\/.*\/en\/.*\/en\/.*\/en\/.*"

    """

    def __init__(self, fitxategia):
        self._fitxategia = fitxategia
        self._conceptnet = None
        self._erlazioak = []
        self._hiztegia = None

    @staticmethod
    def __prozesatu_chunka(chunk):
        chunk[1] = chunk[1].apply(lambda row: row.split('/')[2].replace('_', ' '))
        chunk[2] = chunk[2].apply(lambda row: row.split('/')[3].replace('_', ' '))
        chunk[3] = chunk[3].apply(lambda row: row.split('/')[3].replace('_', ' '))
        chunk.drop(columns=[0], inplace=True)

        result = pd.DataFrame(columns=['arg1', 'rel', 'arg2'])
        result[['arg1', 'rel', 'arg2']] = chunk[[2, 1, 3]]

        return result

    def formatua_egokitu(self, BUFFER_SIZE=10000, verbose=False):
        df_result = pd.DataFrame()

        # Kargatu ConceptNet chunk-a
        for i, chunk in enumerate(
                pd.read_csv(self._fitxategia, sep="\t", header=None, chunksize=BUFFER_SIZE, encoding='utf-8')):
            if verbose:
                print('Working on: ' + str(i * BUFFER_SIZE) + ' - ' + str((i + 1) * BUFFER_SIZE) + ' rows.')
            processed = self.__prozesatu_chunka(chunk)
            df_result = df_result.append(processed, ignore_index=True)

        df_result.dropna(inplace=True)
        self._conceptnet = df_result

        return self._conceptnet


    def erauzi_domeinuko_tripletak(self, hiztegia, BUFFER_SIZE=10000, eragiketa='and', verbose=False):
        """
        :param hiztegia:
        :param BUFFER_SIZE:
        :param eragiketa:
        :param verbose:
        :return:
        """
        hiztegia = np.load(hiztegia)

        if self._conceptnet is None:
            self.formatua_egokitu(BUFFER_SIZE, verbose)

        if eragiketa is 'and':
            df_result = self._conceptnet[self._conceptnet.arg1.isin(hiztegia) & self._conceptnet.arg2.isin(hiztegia)]
        else:
            df_result = self._conceptnet[self._conceptnet.arg1.isin(hiztegia) | self._conceptnet.arg2.isin(hiztegia)]

        df_result.dropna(inplace=True)
        self._hiztegia = hiztegia

        self._conceptnet = df_result

        return df_result

    def erauzi_erlazioak(self, erlazioak):
        self._erlazioak = erlazioak
        self._conceptnet = self._conceptnet.query(" rel == @erlazioak ")

        return self._conceptnet

    def lortu_conceptnet(self):
        return self._conceptnet

    def azterketa(self):
        erlazioak = pd.DataFrame()

        erlazio_izenak = self._conceptnet.rel.unique()
        erlazioak['Erlazioa'] = pd.Series(erlazio_izenak)
        erlazioak['Kopurua'] = pd.Series([self._conceptnet.query("rel == '" + erlazioa + "'").rel.count()
                                          for erlazioa in erlazio_izenak])
        rel_kop = self._conceptnet.rel.count()
        erlazioak['Kopurua%'] = erlazioak['Kopurua'] / rel_kop

        def lortu_hitzak(erlazio_df):
            hitzak1 = erlazio_df.arg1.values
            hitzak2 = erlazio_df.arg2.values

            return np.unique([hitzak1] + [hitzak2]).size

        erlazioak['Hitz_Kop'] = pd.Series([lortu_hitzak(self._conceptnet.query("rel == '" + erlazioa + "'"))
                                           for erlazioa in erlazio_izenak])
        erlazioak['Hitz_Kop%'] = erlazioak['Hitz_Kop'] / lortu_hitzak(self._conceptnet)
        erlazioak.sort_values('Kopurua', inplace=True, ascending=False)

        return erlazioak
