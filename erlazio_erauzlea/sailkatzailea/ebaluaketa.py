import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import itertools
from copy import copy
import pickle as pickle

from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import precision_score, recall_score, f1_score

from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier


def precision_recall_kurba_anizkoitza(modeloak):
    #colors = itertools.cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal'])
    colors = itertools.cycle(mcolors.TABLEAU_COLORS)


    plt.figure(figsize=(7, 8))
    f_scores = np.linspace(0.2, 0.8, num=4)
    lines = []
    labels = []
    for f_score in f_scores:
        x = np.linspace(0.01, 1)
        y = f_score * x / (2 * x - f_score)
        l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
        plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[45] + 0.02))

    lines.append(l)
    labels.append('iso-f1 curves')

    for modeloa, color in zip(sorted(modeloak.items(), key=lambda x:x[0]), colors):
        izena, modeloa = modeloa
        precision, recall, average_precision = modeloa.precision_recall_kurba(irudikatu=False)
        l, = plt.plot(recall, precision, color=color, lw=2)
        lines.append(l)
        labels.append('Precision-recall for class {0} (area = {1:0.2f})'
                      ''.format(izena, average_precision))

    fig = plt.gcf()
    fig.subplots_adjust(bottom=0.25)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Doitasun/estaldura kurba')
    plt.legend(lines, labels, loc=(0, -.38), prop=dict(size=14))


class Ebaluaketa:

    def __init__(self, modeloa, X_train, X_test, y_train, y_test):
        self._modeloa = modeloa
        self._X_train = X_train
        self._X_test = X_test
        self._y_train = y_train
        self._y_test = y_test
        self._class_names = [
            'AtLocation',
            'IsA',
            'PartOf',
            'UsedFor',
            'Nil'
        ]

    def konfusio_matrizea(self, izenburua, normalizatua=True):

        def plot_confusion_matrix(cm, classes, ax=plt,
                                  normalize=False,
                                  title='Confusion matrix',
                                  cmap=plt.cm.Blues):
            """
            This function prints and plots the confusion matrix.
            Normalization can be applied by setting `normalize=True`.
            """
            if normalize:
                cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

            plt.imshow(cm, interpolation='nearest', cmap=cmap)
            plt.title(title)
            # plt.colorbar()
            tick_marks = np.arange(len(classes))
            plt.xticks(tick_marks, classes, rotation=45)
            plt.yticks(tick_marks, classes)

            fmt = '.2f' if normalize else 'd'
            thresh = cm.max() / 2.
            for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
                plt.text(j, i, format(cm[i, j], fmt),
                         horizontalalignment="center",
                         color="white" if cm[i, j] > thresh else "black")

        clf = copy(self._modeloa)
        clf.fit(self._X_train, self._y_train)
        predictions = clf.predict(self._X_test)
        cm = confusion_matrix(self._y_test, predictions)
        plt.figure()
        plot_confusion_matrix(cm, classes=self._class_names, normalize=normalizatua, title=izenburua)

    def precision_recall_kurba(self, irudikatu=True):
        # Aurreprozesatu datuak
        y_train = label_binarize(self._y_train, classes=list(range(len(self._class_names))))
        y_test = label_binarize(self._y_test, classes=list(range(len(self._class_names))))

        classifier = copy(self._modeloa)
        classifier = OneVsRestClassifier(classifier)
        classifier.fit(self._X_train, y_train)
        y_score = classifier.decision_function(self._X_test)

        # For each class
        precision = dict()
        recall = dict()
        average_precision = dict()
        for i in range(len(self._class_names)):
            precision[i], recall[i], _ = precision_recall_curve(y_test[:, i],
                                                                y_score[:, i])
            average_precision[i] = average_precision_score(y_test[:, i], y_score[:, i])

        # A "micro-average": quantifying score on all classes jointly
        precision["micro"], recall["micro"], _ = precision_recall_curve(y_test.ravel(),
                                                                        y_score.ravel())
        average_precision["micro"] = average_precision_score(y_test, y_score,
                                                             average="micro")
        print('Average precision score, micro-averaged over all classes: {0:0.2f}'
              .format(average_precision["micro"]))

        if irudikatu:
            colors = itertools.cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal'])

            plt.figure(figsize=(7, 8))
            f_scores = np.linspace(0.2, 0.8, num=4)
            lines = []
            labels = []
            for f_score in f_scores:
                x = np.linspace(0.01, 1)
                y = f_score * x / (2 * x - f_score)
                l, = plt.plot(x[y >= 0], y[y >= 0], color='gray', alpha=0.2)
                plt.annotate('f1={0:0.1f}'.format(f_score), xy=(0.9, y[45] + 0.02))

            lines.append(l)
            labels.append('iso-f1 curves')
            l, = plt.plot(recall["micro"], precision["micro"], color='gold', lw=2)
            lines.append(l)
            labels.append('micro-average Precision-recall (area = {0:0.2f})'
                          ''.format(average_precision["micro"]))

            for i, color in zip(range(len(self._class_names)), colors):
                l, = plt.plot(recall[i], precision[i], color=color, lw=2)
                lines.append(l)
                labels.append('Precision-recall for class {0} (area = {1:0.2f})'
                          ''.format(self._class_names[i], average_precision[i]))

            fig = plt.gcf()
            fig.subplots_adjust(bottom=0.25)
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('Recall')
            plt.ylabel('Precision')
            plt.title('Extension of Precision-Recall curve to multi-class')
            plt.legend(lines, labels, loc=(0, -.38), prop=dict(size=14))

        return precision["micro"], recall["micro"], average_precision["micro"]


    def precision_recall_fscore(self):
        clf = copy(self._modeloa)
        clf.fit(self._X_train, self._y_train)
        pre = clf.predict(self._X_test)

        precision = precision_score(self._y_test, pre, average='macro')
        recall = recall_score(self._y_test, pre, average='macro')
        fscore = f1_score(self._y_test, pre, average='macro')
        #precision, recall, fscore, _ = precision_recall_fscore_support(self._y_test, pre, average='macro')

        return precision, recall, fscore

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            model = pickle.load(f)

        return model
