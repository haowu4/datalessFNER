import codecs
import numpy as np


def loadW2V(w2v_file, allowed = None):
    ret = {}
    err = 0
    with codecs.open(w2v_file, "r" , 'utf-8') as f_in:
        for line in f_in:
            line = line.strip()
            if len(line) == 0:
                continue
            try:
                w, vec = line.split("\t")
            except ValueError:
                err += 1
                continue
            if allowed is not None and w in allowed:
                vec = [float(v) for v in vec.split(" ")]
                ret[w] = np.array(vec)
    print("%d line failed" % err)
    return ret


def get_feat_template_name(feat_func):
    return feat_func.__name__


def get_vocab_from_docs(docs):
    vocab = set()
    for doc in docs:
        for token in doc:
            vocab.add(token.text)
    return vocab


def count_total_constituents_from_docs(docs, viewname):
    key_errors = 0
    num_constituents = 0
    for doc in docs:
        try:
            num_constituents += len(doc.user_data[viewname])
        except KeyError:
            key_errors += 1
    if key_errors > 0:
        print("WARNING: %d docs didn't have %s" % (key_errors, viewname))
    return num_constituents
