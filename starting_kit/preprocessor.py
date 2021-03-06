"""
Created on Fri Mar 27 17:49:23 2020
@author: Jérôme, Pierre, George, Raphaël, Paul, Luqman
Last revised: Avr 04, 2020
Revision History :
    Avr 04, 2020 : Jérôme
    Mar 27, 2020 : Jérôme

This class aim to automate the preprocessing chain.
Briefly, it will extract features from a set of data... TODO
"""
import warnings
import paths
from data_manager import DataManager

from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectKBest
from sklearn.decomposition import PCA
from sklearn.neighbors import LocalOutlierFactor
import seaborn as sns
import numpy as np

warnings.simplefilter(action='ignore', category=FutureWarning)
sns.set()
paths


with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from sklearn.base import BaseEstimator
    # Note: if zDataManager is not ready, use the mother class DataManager


class preprocessor(BaseEstimator):

    def __init__(self):
        self.show = False
        self.fited = False
        self.n_components = 70
        self.transformer = [PCA(self.n_components)]

    def extract_features(self):
        ...

    def fit(self, X, Y):
        """
        Learning from data
        """
        # TODO : determine best parameters (eg: threshold see below)
        # [x] featureSelection
        # [x] Outliners
        # [ ] PCA
        # [ ] add some prints

        self.nbFeatures = self._featureSelectionFit(X, Y)
        self.feature_selection = SelectKBest(chi2, self.nbFeatures).fit(X, Y)
        self.thresholdOutliners = self._removeOutlinersFit(X)

        self.fited = True
        return self

    def fit_transform(self, X, Y):
        self.fit(X, Y)
        self.fited = True
        return self.fit(X, Y).transform(X)

    def transform(self, X, Y=None):
        if not self.fited:
            raise Exception("Cannot transform is data is not fit")
        else:
            X = self.feature_selection.transform(X)
            X = self._removeOutliners(X)
            return X

    def _removeOutlinersFit(self, X):
        """
        From X, _removeOutlinersFit calculates the threshold to remove outliers
        """
        clf = LocalOutlierFactor()
        clf.fit_predict(X)
        arr = clf.negative_outlier_factor_.copy()
        thresholds = np.flip(np.sort(arr))
        diff = (max(arr) - min(arr)) / 4000.
        for i, th in enumerate(thresholds):
            if i > 10 and abs(thresholds[i] - thresholds[i - 1]) > diff:
                return th
        print("error")

    def _removeOutliners(self, X):
        threshold = self.thresholdOutliners
        clf = LocalOutlierFactor()
        clf.fit_predict(X)
        arr = clf.negative_outlier_factor_.copy()

        idxToDelete = []
        for i, d in enumerate(arr):
            if d < threshold:
                idxToDelete += [i]
        D.data['X_train'] = np.delete(D.data['X_train'], idxToDelete, axis=0)
        return np.delete(X, idxToDelete, axis=0)

    def _featureSelectionFit(self, X, Y):
        score, pvalue = chi2(X, Y)
        threshold = self._best_threshold_featureselect(pvalue, X, Y)

        nbFeatures = 0
        for i in pvalue:
            if(i < threshold):
                nbFeatures += 1

        print("best number of features (with threshold = {}) is {}".format(threshold, nbFeatures))
        return nbFeatures

    def _best_threshold_featureselect(self, pvalue, x, y):
        thresholds = np.linspace(0, 1, 1000)
        res = np.zeros(len(thresholds))
        for i, threshold in enumerate(thresholds):
            k = 0
            for l in pvalue:
                if(l < threshold):
                    k += 1
            res[i] = k
            if i > 1 and res[i] - res[i - 1] < 1:
                return threshold

    # TODO
    def get_params(self, deep=True):
        # suppose this estimator has parameters "alpha" and "recursive"
        return {"alpha": self.alpha, "recursive": self.recursive}

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self


if __name__ == "__main__":
    # We can use this to run this file as a script and test the preprocessor
    # check_estimator(preprocessor)

    data_name = 'plankton'
    data_dir = './public_data'          # The sample_data directory should contain only a very small subset of the data

    basename = 'Iris'
    D = DataManager(data_name, data_dir, replace_missing=True)
    print("*** Original data ***")
    print(D)

    Prepro = preprocessor()

    # Preprocess on the data and load it back into D
    D.data['X_train'] = Prepro.fit_transform(D.data['X_train'], D.data['Y_train'])
    D.data['X_valid'] = Prepro.transform(D.data['X_valid'])
    D.data['X_test'] = Prepro.transform(D.data['X_test'])

    # Here show something that proves that the preprocessing worked fine
    print("*** Transformed data ***")
    print(D)
