# -*- coding: utf-8 -*-
import numpy as np
from scipy.sparse import coo_matrix, hstack


class MentionClassifier(object):

    @classmethod
    def load_classifier(clz, w2v, ):
        pass

    def __init__(self,
                 model=None,
                 feature_functions=None,
                 dense_feature_functions=None,
                 feature_lex=None,
                 type_lex=None):
        self.model = model
        self.feature_functions = feature_functions
        self.dense_feature_functions = dense_feature_functions
        self.feature_lex = feature_lex
        self.type_lex = type_lex
        self.idx_to_typ = [None] * len(type_lex)

        for i in type_lex:
            self.idx_to_typ[type_lex[i]] = i

    def classify(self, doc, start, end):
        vx = self.generate_vecs([(doc, start, end)],
                                self.feature_functions,
                                self.dense_feature_functions,
                                self.feature_lex)
        scores = self.model.decision_function(vx)[0]
        return {t: s for t, s in zip(self.idx_to_typ, scores)}

    @staticmethod
    def generate_vecs(objs,
                      feature_func,
                      dense_real_vec_features,
                      lex):
        len_x = len(objs)

        row_ids = []
        col_ids = []
        vs = []

        dense_vecs = []

        for i, x in enumerate(objs):
            doc, start, end = x
            for ff in feature_func:
                for k, v in ff(doc, start, end):
                    if k in lex:
                        idx = lex[k]
                        row_ids.append(i)
                        col_ids.append(idx)
                        vs.append(v)

            if len(dense_real_vec_features) > 0:
                ds = []
                for dff in dense_real_vec_features:
                    v = dff(doc, start, end)
                    ds.append(v)
                denv = np.hstack((ds))
                dense_vecs.append(denv)
        m_shape = (len_x, len(lex))
        xs = coo_matrix((vs, (row_ids, col_ids)), shape=m_shape)

        dense_vecs = np.vstack(dense_vecs)

        if len(dense_real_vec_features) > 0:
            xs = hstack((xs, dense_vecs))
        return xs.tocsr()
