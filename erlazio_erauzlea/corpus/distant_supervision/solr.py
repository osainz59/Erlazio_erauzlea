import json
import requests
import bz2
import pandas as pd
import numpy as np
from random import randint


class Solr:

    def __init__(self, url):
        self._url = url

    def query(self, query, sort=None, start=None,
              rows=None, fq=None, fl=None, time=None,
              debug=False):

        q = "{}select?q={}".format(self._url, query)
        if sort is not None:
            q = "{}&sort={}".format(q, sort)
        if start is not None:
            q = "{}&start={}".format(q, start)
        if rows is not None:
            q = "{}&rows={}".format(q, rows)
        if fq is not None:
            q = "{}&fq={}".format(q, fq)
        if fl is not None:
            q = "{}&fl={}".format(q, fl)
        if time is not None:
            q = "{}&time={}".format(q, time)

        q.replace(" ", "+")

        if debug:
            print(q)

        response = json.loads(requests.get(q).text)

        return response

    def __indexatu(self, datuak):
        requests.post("{}update/json/docs?commit=true".format(self._url), data=json.dumps(datuak))

    def __commit(self):
        requests.post("{}update?commit=true".format(self._url))

    def indexatu_corpusa(self, fitxategia):
        with bz2.open(fitxategia, 'rt') as infile:

            izenburuak = False
            data = []

            for line in infile:
                if not izenburuak:
                    izenburuak = True
                    continue

                row = line.split('\t')

                data.append({
                    "id": row[0],
                    "text": row[1][:-1]
                })

            self.__indexatu(data)
            self.__commit()

    def erauzi_corpusa(self, conceptnet, verbose=False):
        training = pd.DataFrame()

        for index, row in conceptnet.iterrows():
            query = "text:\"" + row.arg1.replace("_", " ") + "\" AND text:\"" + row.arg2.replace("_", " ") + "\""

            response = self.query(query, rows=660000, fl="id")['response']
            if response['numFound'] == 0:
                continue

            rows = pd.DataFrame({'arg1': row.arg1.replace("_", " "),
                                 'arg2': row.arg2.replace("_", " "),
                                 'docid': [sentence['id'] for sentence in response['docs']],
                                 'rel': row.rel})

            training = training.append(rows, ignore_index=True)

            if verbose and index % 100 == 0:
                print(index)

        return training

    def sortu_nil_adibideak(self, conceptnet, n=10000, verbose=False):
        args = conceptnet.arg1.append(conceptnet.arg2).unique()
        # M = len(args)

        result = pd.DataFrame(columns=['arg1', 'arg2', 'docid', 'rel'])

        while len(result) < n:
            ok = False
            count = 0
            while not ok:
                count += 1
                # a, b = (args[randint(0, M - 1)], args[randint(0, M - 1)])
                a, b = np.random.choice(args, size=2, replace=False)

                if len(conceptnet.query(
                        '(arg1 == "' + a + '" and arg2 == "' + b + '") or (arg1 == "' + b + '" and arg2 == "' + a + '")')):
                    continue

                if len(result.query(
                        '(arg1 == "' + a + '" and arg2 == "' + b + '") or (arg1 == "' + b + '" and arg2 == "' + a + '")')):
                    continue

                query = "text:\"" + a.replace("_", " ") + "\" AND text:\"" + b.replace("_", " ") + "\""
                response = self.query(query=query, rows=660000, fl="id")['response']

                if response['numFound'] == 0:
                    continue

                rows = pd.DataFrame({'arg1': a.replace("_", " "),
                                     'arg2': b.replace("_", " "),
                                     'docid': [sentence['id'] for sentence in response['docs']],
                                     'rel': 'Nil'
                                     })

                result = result.append(rows, ignore_index=True)
                ok = True
                if verbose:
                    print(len(result), count)
