import os

from scipy import sparse
from scipy.sparse import coo_matrix
import numpy as np

from dfiner.classifier.lexicon import Lexicon
from dfiner.utils.utils import dump_pickle, load_pickle


class FeatureStroage(object):

    cache_dir = "/tmp/cache"
    COO = "COO"
    DENSE = "DENSE"

    @staticmethod
    def set_cache_dir(path):
        FeatureStroage.cache_dir = path

    @staticmethod
    def save_sparse_csr(filename, array):
        np.savez(filename,
                 data=array.data,
                 row=array.row,
                 col=array.col,
                 shape=array.shape)

    @staticmethod
    def load_sparse_csr(mat_file):
        print(mat_file)
#         mat_file = "%s.coo_mat" % mat_file
        loader = np.load(mat_file)
        data = loader['data']
        row = loader['row']
        col = loader['col']
        shape = loader['shape']
        return coo_matrix((data, (row, col)), shape=shape)

    @staticmethod
    def dump_mat(mat, feature_name, corpora_name):
        # We assume the input is either plain dense numpy matrix,
        # or coo_matrix from scipy
        base_file = os.path.join(FeatureStroage.cache_dir,
                                 "%s__%s.cache_mat" % (feature_name,
                                                       corpora_name))
        if sparse.isspmatrix_coo(mat):
            filename = "%s.coo_mat.npz" % base_file
#             with open(filename, "wb") as out:
            FeatureStroage.save_sparse_csr(filename, mat)

        else:
            filename = "%s.dense_mat.npz" % base_file
#             with open(filename, "wb") as out:
            np.savez(filename, data=mat)

    @staticmethod
    def cache_exist(mat_path):
        dense_path = "%s.dense_mat.npz" % mat_path
        if os.path.exists(dense_path):
            return FeatureStroage.DENSE, dense_path
        else:
            coo_path = "%s.coo_mat.npz" % mat_path
            if os.path.exists(coo_path):
                return FeatureStroage.COO, coo_path
            else:
                return None, None

    @staticmethod
    def load(feature_name, corpora_name):
        base_path = os.path.join(FeatureStroage.cache_dir,
                                 "%s__%s.cache_mat" % (feature_name,
                                                       corpora_name))
        existed, mat_path = FeatureStroage.cache_exist(base_path)
        if not existed:
            return None
        else:
            # Do extraction.
            if existed is FeatureStroage.COO:
                return FeatureStroage.load_sparse_csr(mat_path)

            if existed is FeatureStroage.DENSE:
                return np.load(mat_path)["data"]


class FeatureExtractor(object):
    def __init__(self, feature_functions):
        self.ffs = feature_functions

    def extract(self,
                corpora_name,
                corpora,
                force_update=False,
                save_new_to_cache=True):
        number_of_intance = len(corpora)
        matrices = []
        for feature_func in self.ffs:
            cache = None
            if not force_update:
                # Allow to use cache
                print("Searching cache for %s on %s" %
                      (corpora_name, feature_func.name))
                cache = FeatureStroage.load(feature_func.name, corpora_name)
                if cache is not None:
                    if cache.shape[0] != number_of_intance:
                        cache = None
                    else:
                        # Cache is valid
                        print("Found cache for %s on %s"
                              % (corpora_name, feature_func.name))
                        mat = cache
                        matrices.append(mat)

            if cache is None:
                # If not allow to use cache or cache missed.
                mat = feature_func.matrix_of(corpora)
                matrices.append(mat)

                if save_new_to_cache:
                    FeatureStroage.dump_mat(mat,
                                            feature_func.name,
                                            corpora_name)

        return sparse.hstack(matrices)

    def build_lexicon(self, corpora, min_support=5, force_update=False):
        for feature_func in self.ffs:
            feature_func.build_lexicon(corpora, min_support, force_update)

    def reverse_lexicon(self):
        rlex = []
        for feature_func in self.ffs:
            for f in feature_func.reverse_lexicon():
                rlex.append("%s=%s" % (feature_func.name, f))
        return rlex


class FeatureFunction_(object):

    def __init__(self, feature_func, name, reuse_lex_from_cache=True):
        self.lex = None
        self.func = feature_func
        self.name = name
        if reuse_lex_from_cache:
            lex_path = os.path.join(FeatureStroage.cache_dir,
                                    "%s.cache_lex" % (name))
            if os.path.exists(lex_path):
                # Load the lex file.
                self.lex = Lexicon()
                self.lex.lexeme_to_index = load_pickle(lex_path)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return "%s.FeatureFunction()" % self.name

    def build_lexicon(self, corpora, min_support=5, force_update=False):
        if not force_update and self.lex is not None:
            print("Using exist lexicon for feature [%s].." % self.name)
            return
        self.lex = Lexicon()
        for x in corpora:
            ret = self.func(*x)
            for x in ret:
                if isinstance(x, tuple):
                    k, v = x
                else:
                    k = x
                self.lex.see_lexeme(k)
        self.lex.prune(min_support)
        lex_path = os.path.join(FeatureStroage.cache_dir,
                                "%s.cache_lex" % (self.name))
        dump_pickle(self.lex.lexeme_to_index, lex_path)

    def freeze_lexicon(self, lex):
        self.lex.allow_new_lexemes = False

    def prune(self, min_support):
        self.lex.prune(min_support)

    def reverse_lexicon(self):
        return self.lex.reverse_lex()

    def matrix_of(self, objs):
        if self.lex is None:
            print("%s has no lexicon.. giving up" % self.name)
        rows = []
        cols = []
        data = []
        for i, x in enumerate(objs):
            ret = self.func(*x)
            for x in ret:
                if isinstance(x, tuple):
                    k, v = x
                else:
                    k = x
                    v = 1.0
                idx = self.lex.getOrNegOne(k)
                if idx != -1:
                    rows.append(i)
                    cols.append(idx)
                    data.append(float(v))
        shape = (len(objs), self.lex.size)
        return coo_matrix((data, (rows, cols)), shape=shape)


class DenseFeatureFunction_(object):

    def __init__(self, feature_func, name, dim):
        self.func = feature_func
        self.name = name
        self.dim = dim

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return "%s.FeatureFunction()" % self.name

    def build_lexicon(self, corpora, min_support=5, force_update=False):
        return

    def matrix_of(self, objs):
        rows = []
        for x in objs:
            row = self.func(*x)
            rows.append(row)
        mats = np.vstack(rows)
        return mats

    def reverse_lexicon(self):
        return [self.name] * self.dim


class FeatureFunction(object):
    def __init__(self, name=None, reuse_lex=True):
        self.name = name
        self.reuse_lex = reuse_lex

    def __call__(self, original_func):

        if self.name is None:
            self.name = original_func.__name__

        return FeatureFunction_(original_func, self.name, self.reuse_lex)


class DenseFeatureFunction(object):
    def __init__(self, dim, name=None):
        self.dim = dim
        self.name = name

    def __call__(self, original_func):

        if self.name is None:
            self.name = original_func.__name__

        return DenseFeatureFunction_(original_func, self.name, self.dim)
