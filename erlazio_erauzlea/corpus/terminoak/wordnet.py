import numpy as np
import pandas as pd
import mysql.connector
from textblob import Word


class TerminoakWordNet:
    WORDNET_DEFAULT_CONFIG = {
        'user': 'guest',
        'password': 'guest',
        'host': 'adimen.si.ehu.es',
        'database': 'mcr10'
    }

    def __init__(self, wordnet_config=None):

        if wordnet_config is None:
            wordnet_config = self.WORDNET_DEFAULT_CONFIG

        if 'user' not in wordnet_config:
            raise ValueError('user parametroa beharrezkoa da wordnet-era sartzeko.')
        if 'password' not in wordnet_config:
            raise ValueError('password parametroa beharrezkoa da wordnet-era sartzeko.')
        if 'host' not in wordnet_config:
            raise ValueError('host parametroa beharrezkoa da wordnet-era sartzeko.')
        if 'database' not in wordnet_config:
            raise ValueError('database parametroa beharrezkoa da wordnet-era sartzeko.')

        self._conf = wordnet_config

    @staticmethod
    def __lortu_hitz_zerrenda(konexioa, domeinua):
        c = konexioa.cursor()
        query = ("""SELECT word
            FROM `wei_domains`, `wei_eng-30_variant`, `wei_eng-30_to_ili`, `wei_ili_to_domains`
            WHERE
            (`wei_domains`.`source` LIKE %s OR `wei_domains`.`target` LIKE %s) AND `wei_domains`.`target` LIKE `wei_ili_to_domains`.`domain` AND
            `wei_eng-30_variant`.`offset` LIKE `wei_eng-30_to_ili`.`offset` AND
            `wei_eng-30_to_ili`.`iliOffset` LIKE `wei_ili_to_domains`.`iliOffset`""")
        c.execute(query, (domeinua, domeinua))
        result = [row[0].decode('utf-8') for row in c]
        c.close()
        return result

    def erauzi_terminoak(self, domain="biology", *args, **kwargs):
        # Konexioa ireki
        con = mysql.connector.connect(**self._conf)

        # Eskatu hitzak zerbitzariari
        hitzak = self.__lortu_hitz_zerrenda(con, domain)
        con.close()

        hitzak = np.array([h.replace('_', ' ') for h in hitzak])

        return hitzak, None

    @staticmethod
    def __lortu_hitzaren_izen_lexikografikoa(hitza, konexioa):
        c = konexioa.cursor()
        print('Looking for {}'.format(hitza.replace(' ', '_')))
        query = """SELECT `word`, `sense`, `name`, `domain`
                   FROM `wei_eng-30_variant`, `wei_eng-30_to_ili`, `wei_ili_record`, `wei_ili_to_domains`, `wei_lexnames`
                   WHERE `wei_eng-30_variant`.`word` LIKE %s AND
                         `wei_eng-30_variant`.`offset` = `wei_eng-30_to_ili`.`offset` AND
                         `wei_eng-30_to_ili`.`iliOffset` = `wei_ili_to_domains`.`iliOffset` AND
                         `wei_eng-30_to_ili`.`iliOffset` = `wei_ili_record`.`iliOffset` AND
                         `wei_ili_record`.`semf` = `wei_lexnames`.`semf`
                   ORDER BY `domain` LIKE 'biology' DESC, `domain` LIKE 'anatomy' DESC, 
                         `domain` LIKE 'biochemistry' DESC, `domain` LIKE 'genetics' DESC, 
                         `domain` LIKE 'physiology' DESC, `sense`, `name` LIKE 'all'
                   LIMIT 1"""
        c.execute(query, (hitza.replace(' ', '_'),))
        row = c.fetchone()
        if row is not None:
            result = row[2].decode('utf-8')
        else:
            result = 'NIW'

        c.close()
        return result

    @staticmethod
    def __to_singular(row, ne):

        if 'NIW' not in ne.izen_lexikografikoa.values:
            return row

        word = Word(row.word).singularize()

        try:
            singular = ne[ne.word == word].reset_index().loc[0]
            row.izen_lexikografikoa = singular.izen_lexikografikoa
        except:
            pass
        return row

    def lortu_izen_lexikografiko_zerrenda(self, hitzak):
        # Izen lexikografikoa = lexnames
        # Konexioa ireki
        con = mysql.connector.connect(**self._conf)

        word2IL = pd.DataFrame()
        word2IL['word'] = hitzak
        word2IL['izen_lexikografikoa'] = word2IL['word'].apply(self.__lortu_hitzaren_izen_lexikografikoa, args=(con,))
        # Pluralak tratatu
        word2IL = word2IL.apply(self.__to_singular, axis=1, args=(word2IL,))

        con.close()
        return word2IL
