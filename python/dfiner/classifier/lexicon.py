
class Lexicon(object):

    def __init__(self):
        self.curr = 0
        self.m = {}
        self.counter = defaultdict(int)

    def see_feature(self, f):
        self.counter[f] += 1
        if f not in self.m:
            self.m[f] = self.curr
            self.curr += 1

    def prune(self, min_support):
        self.curr = 0
        self.m = {}
        for k in self.counter:
            if self.counter[k] > min_support:
                self.m[k] = self.curr
                self.curr += 1

    def getOrNegOne(self, f):
        if f in self.m:
            return self.m[f]
        else:
            return -1

    def getOneHot(self, f):
        ret = np.zeros((self.curr))
        if f in self.m:
            ret[self.m[f]] = 1.0
        return ret


def generate_vecs(objs,
                  typ_function,
                  feature_func,
                  dense_real_vec_features = [],
                  lex = None,
                  type_lex = None
                 ):
    len_x = len(objs)

    if lex is None:
        lex = Lexicon()
        for x in objs:
            for ff in feature_func:
                for k,v in ff(x):
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
            for k,v in ff(x):
                idx = lex.getOrNegOne(k)
                if idx > -1:
                    row_ids.append(i)
                    col_ids.append(idx)
                    vs.append(v)

        if len(dense_real_vec_features) > 0:
            ds = []
            for dff in dense_real_vec_features:
                v  = dff(x)
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
