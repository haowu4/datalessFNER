# -*- coding: utf-8 -*-


def generate_vecs(objs,
                  typ_function,
                  feature_func,
                  dense_real_vec_features=[],
                  lex=None,
                  type_lex=None):
    len_x = len(objs)

    if lex is None:
        lex = Lexicon()
        for x in objs:
            for ff in feature_func:
                for k, v in ff(x):
                    lex.see_feature(k)
        lex.prune(10)

    if type_lex is None:
        type_lex = Lexicon()
        for x in objs:
            y = typ_function(x)
            type_lex.see_feature(y)

    row_ids = []
    col_ids = []
    vs = []

    dense_vecs = []

    ys = []

    for i, x in enumerate(objs):
        for ff in feature_func:
            for k, v in ff(x):
                idx = lex.getOrNegOne(k)
                if idx > -1:
                    row_ids.append(i)
                    col_ids.append(idx)
                    vs.append(v)

        if len(dense_real_vec_features) > 0:
            ds = []
            for dff in dense_real_vec_features:
                v = dff(x)
                ds.append(v)
#             print(len(ds))
            denv = np.hstack((ds))
            dense_vecs.append(denv)

        ys.append(type_lex.getOrNegOne(typ_function(x)))

    sp = (len_x, lex.curr)
    print(sp)
    xs = coo_matrix((vs, (row_ids, col_ids)), shape=sp)
    print("dense_vecs[0].shape", dense_vecs[0].shape)
    dense_vecs = np.vstack(dense_vecs)
    print("dense_vecs.shape", dense_vecs.shape)
    if len(dense_real_vec_features) > 0:
        print("shapes : ", xs.shape, dense_vecs.shape, )
        xs = hstack((xs, dense_vecs))
    return lex, type_lex, xs.tocsr(), np.asarray(ys)


class MentionClassifier(object):

    def __init__(self, feature_functions, dense_feature_functions):
        pass

    def train(self, typ_function):
        lex, type_lex, xs_train, ys_train = generate_vecs(train_mentions,
                                              typ_func,
                                              features,
                                              dense_feature)

        _,_, xs_test, ys_test = generate_vecs(test_mentions,
                                    typ_func,
                                    features,
                                    dense_feature,
                                    lex,
                                    type_lex)

        _,_, xs_dev, ys_dev = generate_vecs(dev_mentions,
                                    typ_func,
                                    features,
                                    dense_feature,
                                    lex,
                                    type_lex)

        _,_, xs_figer, _ = generate_vecs(figer_datas,
                                    lambda m : "LOC",
                                    features,
                                    dense_feature,
                                    lex,
                                    type_lex)