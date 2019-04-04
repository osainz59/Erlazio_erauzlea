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
        self._conceptnet = pd.DataFrame()
        self._erlazioak = []
        self._hiztegia = None

    @staticmethod
    def __prozesatu_chunka(chunk):
        chunk[1] = chunk[1].apply(lambda row: row.split('/')[2])
        chunk[2] = chunk[2].apply(lambda row: row.split('/')[3])
        chunk[3] = chunk[3].apply(lambda row: row.split('/')[3])
        # chunk[4] = chunk[4].apply(lambda row: get_weight(row))
        chunk.drop(columns=[0], inplace=True)
        # result = pd.DataFrame(columns=['arg1', 'rel', 'arg2', 'weight'])
        result = pd.DataFrame(columns=['arg1', 'rel', 'arg2'])
        # result[['arg1', 'rel', 'arg2', 'weight']] = chunk[[2, 1, 3, 4]]
        result[['arg1', 'rel', 'arg2']] = chunk[[2, 1, 3]]

        return result

    def erauzi_domeinuko_tripletak(self, hiztegia, BUFFER_SIZE=10000, eragiketa='and', verbose=False):
        df_result = pd.DataFrame()
        hiztegia = np.load(hiztegia)

        # Kargatu ConceptNet chunk-a
        for i, chunk in enumerate(
                pd.read_csv(self._fitxategia, sep="\t", header=None, chunksize=BUFFER_SIZE, encoding='utf-8')):
            if verbose:
                print('Working on: ' + str(i * BUFFER_SIZE) + ' - ' + str((i + 1) * BUFFER_SIZE) + ' rows.')
            processed = self.__prozesatu_chunka(chunk)
            if eragiketa is 'and':
                processed = processed[processed['arg1'].isin(hiztegia) & processed['arg2'].isin(hiztegia)]
            else:
                processed = processed[processed['arg1'].isin(hiztegia) | processed['arg2'].isin(hiztegia)]
            df_result = df_result.append(processed, ignore_index=True)

        df_result.dropna(inplace=True)
        self._conceptnet = df_result
        self._hiztegia = hiztegia

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
        erlazioak['Pisu_Handiena'] = pd.Series([self._conceptnet.query("rel == '" + erlazioa + "'").weight.max()
                                                for erlazioa in erlazio_izenak])

        def lortu_hitzak(erlazio_df):
            hitzak1 = erlazio_df.arg1.values
            hitzak2 = erlazio_df.arg2.values

            return np.unique([hitzak1] + [hitzak2]).size

        erlazioak['Hitz_Kop'] = pd.Series([lortu_hitzak(self._conceptnet.query("rel == '" + erlazioa + "'"))
                                           for erlazioa in erlazio_izenak])
        erlazioak['Hitz_Kop%'] = erlazioak['Hitz_Kop'] / self._hiztegia
        erlazioak.sort_values('Kopurua', inplace=True, ascending=False)

        hitzak = pd.DataFrame()
        hitzak['Terminoa'] = pd.Series(pd.unique(self._conceptnet[["arg1", "arg2"]].values.ravel('K')))
        for erlazioa in erlazioak.Erlazioa:
            hitzak[erlazioa] = pd.Series([self._conceptnet.query(
                'rel == "' + erlazioa + '" and ( arg1 == "' + hitza + '" or arg2 == "' + hitza + '")').rel.count()
                                          for hitza in hitzak.Terminoa])

        hitzak['Total'] = hitzak.sum(axis=1)
        hitzak.sort_values('Total', inplace=True, ascending=False)

        return erlazioak, hitzak
