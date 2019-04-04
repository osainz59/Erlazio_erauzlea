from imblearn import combine as cb


class Sampling:

    def __init__(self):
        self._sampling_strategy = 'auto'
        self._random_state = 42

    def adibide_sintetikoak_sortu(self, X_train, y_train):

        sampler = cb.SMOTETomek(sampling_strategy=self._sampling_strategy,
                                random_state=self._random_state)

        X, y = sampler.fit_resample(X_train, y_train)

        return X, y