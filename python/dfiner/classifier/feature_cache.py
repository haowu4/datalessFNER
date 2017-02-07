from collections import defaultdict
from spacy.strings import hash_string
import cPickle as pickle


class FeatureCache(object):

    def __init__(self, feat_to_index=None, sparse_feat_cache=None, dense_feat_cache=None):
        self._sparse_feat_cache = sparse_feat_cache if sparse_feat_cache else \
            defaultdict(lambda : defaultdict(list))
        self._dense_feat_cache = dense_feat_cache if dense_feat_cache else \
            defaultdict(dict)
        self._feat_to_index = feat_to_index if feat_to_index else {}
        self._index_to_feat = {index: feat for feat, index in self._feat_to_index.iteritems()}
        self._cache_new = True

    @property
    def cache_new(self):
        return self._cache_new

    @cache_new.setter
    def cache_new(self, value):
        assert isinstance(value, bool)
        self._cache_new = value

    def get_feat_index(self, feat):
        if feat in self._feat_to_index:
            return self._feat_to_index[feat]
        else:
            feat_index = len(self._feat_to_index)
            self._feat_to_index[feat] = feat_index
            self._index_to_feat[feat_index] = feat
            return feat_index

    @staticmethod
    def get_key(doc, mention):
        key = hash_string(doc.text) ^ hash(mention)
        return key

    def add_sparse_feats_to_cache(self, doc, mention, feat_template_name, features):
        if not self._cache_new:
            print("WARNING: cannot add new items to cache")
            return
        key = self.get_key(doc, mention)
        for feat, value in features:
            feat_index = self.get_feat_index(feat)
            if feat_index > -1:
                self._sparse_feat_cache[feat_template_name][key].append((feat_index, value))

    def fetch_sparse_feats_or_none(self, doc, mention, feat_template_name):
        key = self.get_key(doc, mention)
        if feat_template_name in self._sparse_feat_cache and \
                key in self._sparse_feat_cache[feat_template_name]:
            indexed_features = self._sparse_feat_cache[feat_template_name][key]
            return [(self._index_to_feat[feat_index], value) for feat_index, value in indexed_features]
        else:
            return None

    def add_dense_feats_to_cache(self, doc, mention, feat_template_name, dense_vec):
        if not self._cache_new:
            print("WARNING: cannot add new items to cache")
            return
        key = self.get_key(doc, mention)
        self._dense_feat_cache[feat_template_name][key] = dense_vec

    def fetch_dense_feats_or_none(self, doc, mention, feat_template_name):
        key = self.get_key(doc, mention)
        if feat_template_name in self._dense_feat_cache and \
                key in self._dense_feat_cache[feat_template_name]:
            return self._dense_feat_cache[feat_template_name][key]
        else:
            return None

    def flush_cache(self, sparse_feats=True, dense_feats=True):
        if sparse_feats:
            self._sparse_feat_cache = defaultdict(lambda : defaultdict(list))
        if dense_feats:
            self._dense_feat_cache = defaultdict(lambda : dict)

    def flush_feats(self, is_sparse, feat_template_name):
        if is_sparse:
            if feat_template_name in self._sparse_feat_cache:
                self._sparse_feat_cache[feat_template_name] = defaultdict(list)
        else:
            if feat_template_name in self._dense_feat_cache:
                self._dense_feat_cache[feat_template_name] = dict()

    def save_cache(self, save_path, include_lexicon=False):
        with open(save_path, 'wb') as f_out:
            d = dict()
            d['sparse_feat_cache'] = self._sparse_feat_cache
            d['dense_feat_cache'] = self._dense_feat_cache
            d['feat_to_index'] = self._feat_to_index
            pickle.dump(d, f_out, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load_from_path(cls, load_path):
        with open(load_path, 'rb') as f_in:
            d = pickle.load(f_in)
        return cls(feat_to_index=d['feat_to_index'],
                   sparse_feat_cache=d['sparse_feat_cache'],
                   dense_feat_cache=d['dense_feat_cache'])
