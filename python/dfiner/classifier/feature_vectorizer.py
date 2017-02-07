import numpy as np
import scipy.sparse as sp

from dfiner.classifier.feature_cache import FeatureCache
from dfiner.classifier.lexicon import Lexicon
from dfiner.ontonote.ontonotes_data import GoldMentionView
from dfiner.classifier.utils import get_feat_template_name

import pdb


def build_lexicons(
        docs,
        type_func,
        sparse_feature_funcs,
        feat_lex,
        type_lex,
        prune_threshold,
        min_length,
        mention_viewname
        ):

    if not (type_lex.allow_new_lexemes or feat_lex.allow_new_lexemes):
        return

    for doc in docs:

        if len(doc) < min_length:
            continue

        for mention_constituent in doc.user_data[mention_viewname]:

            if type_lex.allow_new_lexemes:
                t = type_func(mention_constituent)
                if t:
                    type_lex.see_lexeme(t)

            if feat_lex.allow_new_lexemes:
                for ffunc in sparse_feature_funcs:
                    features = ffunc(doc, mention_constituent)
                    for feat, val in features:
                        feat_lex.see_lexeme(feat, cls=type_func(mention_constituent))

    if feat_lex.allow_new_lexemes:
        feat_lex.prune(prune_threshold)


def generate_vecs(
        docs,
        type_func,
        sparse_feature_funcs,
        dense_vec_feat_funcs,
        feat_lex=None,
        type_lex=None,
        prune_threshold=7,
        min_length=0,
        mention_viewname=GoldMentionView.GOLD_MENTION_VIEW_NAME,
        feat_cache=None
        ):

    if type_lex is None:
        type_lex = Lexicon()

    if feat_lex is None:
        feat_lex = Lexicon()

    build_lexicons(
        docs, type_func, sparse_feature_funcs,
        feat_lex, type_lex, prune_threshold, min_length, mention_viewname)

    # feat_cache
    # None: don't cache features
    # True: create a new cache object and cache features
    # FeatureCache object: use the FeatureCache object
    if feat_cache is True:
        feat_cache = FeatureCache(feat_lex)

    # sparse features
    row_ids = []
    col_ids = []
    vs = []

    # the doc index corresponding to each row (denoting a mention)
    doc_indices = []
    # the surface string corresponding to each mention
    surfaces = []

    dense_vecs = []

    ys = []

    min_len_skipped = 0
    type_skipped = 0
    num_mentions = 0

    for doc_index, doc in enumerate(docs):
        if len(doc) < min_length:
            min_len_skipped += 1
            continue
        for mention_constituent in doc.user_data[mention_viewname]:
            t = type_func(mention_constituent)
            if t is None or type_lex[t] == -1:
                type_skipped += 1
                continue
            type_lex_index = type_lex[t]
            ys.append(type_lex_index)

            for ffunc in sparse_feature_funcs:
                f_name = get_feat_template_name(ffunc)
                features = None
                if feat_cache:
                    features = \
                        feat_cache.fetch_sparse_feats_or_none(
                            doc, mention_constituent, f_name)
                if features is None:
                    features = list(ffunc(doc, mention_constituent))
                    # if feat_cache, then cache the features for this doc, mention
                    if feat_cache:
                        feat_cache.add_sparse_feats_to_cache(
                            doc, mention_constituent, f_name, features
                        )
                indexed_features = [(feat_lex[feat], val) for feat, val in features
                                    if feat_lex[feat] > -1]
                for feat_index, val in indexed_features:
                    row_ids.append(num_mentions)
                    col_ids.append(feat_index)
                    vs.append(val)
            num_mentions += 1
            doc_indices.append(doc_index)
            surfaces.append(doc[mention_constituent.start:mention_constituent.end].text)

            if len(dense_vec_feat_funcs) == 0:
                continue
            # more than 1 dense feat funcs
            ds = []
            for dffunc in dense_vec_feat_funcs:
                f_name = get_feat_template_name(dffunc)
                dense_vec = None
                if feat_cache:
                    dense_vec = feat_cache.fetch_dense_feats_or_none(
                        doc, mention_constituent, f_name)
                if dense_vec is None:
                    dense_vec = dffunc(doc, mention_constituent)
                    if feat_cache:
                        feat_cache.add_dense_feats_to_cache(
                            doc, mention_constituent, f_name, dense_vec)
                ds.extend(dense_vec)
            dense_vecs.append(ds)

    assert len(row_ids) == len(col_ids) == len(vs)
    assert len(doc_indices) == len(ys)
    if len(dense_vec_feat_funcs) > 0:
        assert len(ys) == len(dense_vecs)

    print "# samples = %d" % num_mentions
    print "# skipped because of min_length(%d) = %d" % (min_length, min_len_skipped)
    print "# skipped because of missing type = %d" % (type_skipped)
    print "# sparse feats = %d" % feat_lex.size
    sparse_feat_mat = sp.coo_matrix((vs, (row_ids, col_ids)), shape=(num_mentions, feat_lex.size))

    if len(dense_vec_feat_funcs) > 0:
        dense_feat_mat = np.squeeze(np.array(dense_vecs))
        print "# dense feats = %d" % dense_feat_mat.shape[1]
        X = sp.hstack((sparse_feat_mat, dense_feat_mat))
    else:
        print "no dense feats"
        X = sparse_feat_mat
    return feat_lex, type_lex, X.tocsr(), np.asarray(ys), doc_indices, surfaces
