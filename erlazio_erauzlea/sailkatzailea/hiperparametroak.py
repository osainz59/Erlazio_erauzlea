import numpy as np

from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score


class HiperparametroOptimizadorea:

    def __init__(self, hasierako_balioa=10, epsilon=0.001, ebaluazio_funtzioa=f1_score, ebaluazio_batazbesteko_mota='macro'):
        self._C = hasierako_balioa
        self._e = epsilon
        self._ebaluatu = ebaluazio_funtzioa
        self._average = ebaluazio_batazbesteko_mota

    def __grid_search(self, X_train, X_dev, y_train, y_dev, balioak, verbose):
        sol = (0, 0)
        emaitzak = []
        for C in balioak:
            clf = LinearSVC(C=C)
            clf.fit(X_train, y_train)
            pre = clf.predict(X_dev)
            score = self._ebaluatu(y_dev, pre, average=self._average)

            emaitzak.append(score)
            if verbose:
                print(C, score)
            if score > sol[1]:
                sol = (C, score)

        return sol[0], sol[1], np.array(emaitzak)

    def __bilaketa_jalea(self, X_train, X_dev, y_train, y_dev, iterazio_kop, verbose):
        C = self._C + self._e
        d_ = self._C
        emaitzak = np.array([])
        balioak = np.array([])
        for i in range(iterazio_kop):
            d = 2 / np.power(5, i)
            C_balioak = np.arange(C - d_, C + d_ + d, d)
            C_balioak = C_balioak[C_balioak > 0]
            C, score, ema = self.__grid_search(X_train, X_dev, y_train, y_dev, C_balioak, verbose)
            balioak = np.hstack((balioak, C_balioak))
            emaitzak = np.hstack((emaitzak, ema))
            d_ = d
            if verbose:
                print("{}. iterazioaren emaitzak: {} - {}".format(i + 1, C, score))

        emaitzak = np.vstack((balioak, emaitzak)).T

        if C <= 0:
            C = self._e

        return C, emaitzak

    def optimizatu(self, X_train, X_dev, y_train, y_dev, iterazio_kop=10, verbose=False):
        return self.__bilaketa_jalea(X_train, X_dev, y_train, y_dev, iterazio_kop, verbose)
