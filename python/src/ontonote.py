import os
from collections import defaultdict, OrderedDict
import json
import codecs
import numpy as np
from scipy.sparse import coo_matrix, hstack
from nltk.stem import WordNetLemmatizer
import re

class Mention(object):
    def __init__(self, start, end, label, tokens, doc_id = ""):
        self.start = start
        self.end = end
        self.label = label
        self.tokens = tokens
        self.surface = [tokens[i] for i in range(start,end)]
        self.ext_surface = [tokens[i] for i in range(max(start-1,0),min(end+1,len(tokens)))]

        self.doc_id = doc_id

    def __repr__(self):
        o = [("start",self.start),
            ("end",self.end),
            ("surface",self.surface),
            ("label",self.label),
            ("doc_id",self.doc_id),
            ("tokens",self.tokens)]

        return json.dumps(OrderedDict(o), indent=4)

def read_figer(file = "/home/haowu4/data/figer/exp.label"):
    tokens = []
    labels = []
    sentences = []
    with codecs.open(file, "r", "utf-8") as input:
        for i, line in enumerate(input):
            line = line.strip()
            if len(line) == 0:
                # New sentence
                if len(tokens) == 0:
                    continue
                sent = get_sentence(tokens, labels)
                for s in sent:
                    sentences.append(s)
                tokens = []
                labels = []
                continue
            line = line.split("\t")
            word, label = line[0], line[1]
            tokens.append(word)
            labels.append(label)

    if len(tokens) == 0:
        return sentences

    sent = get_sentence(tokens, labels)
    sentences.append(sent)
    tokens = []
    labels = []
    return sentences



def get_sentence(tokens, labels):
    entities = []
    current_labels = ""
    current_start = 0
    in_mention = False
    for i, (t, lab_str) in enumerate(zip(tokens, labels)):
        if lab_str.startswith("B"):
            if in_mention:
                entities.append(Mention(current_start, i, current_labels, tokens))
                in_mention = False
            current_start = i
            current_labels = lab_str.split("-")[1]
            in_mention = True

        if lab_str == "O":
            if in_mention:
                entities.append(Mention(current_start, i, current_labels, tokens))
                in_mention = False

    if in_mention:
        entities.append(Mention(current_start, len(labels), current_labels, tokens))

    return entities


def load_ontonotes(file):
    tokens = []
    labels = []
    sentences = []
    with codecs.open(file, "r", "utf-8") as input:
        for i, line in enumerate(input):
            if i < 1:
                continue
            line = line.strip()
            if len(line) == 0:
                # New sentence
                if len(tokens) == 0:
                    continue
                sent = get_sentence(tokens, labels)
                for s in sent:
                    sentences.append(s)
                tokens = []
                labels = []
                continue
            line = line.split("\t")
            word, label = line[5], line[0]
            tokens.append(word)
            labels.append(label)

    if len(tokens) == 0:
        return sentences

    sent = get_sentence(tokens, labels)
    sentences.append(sent)
    tokens = []
    labels = []
    return sentences


def load_all_data(base_folder):
    ret = []
    for f in os.listdir(base_folder):
        fn = os.path.join(base_folder,f)
        ms = load_ontonotes(fn)
        for m in ms:
            m.doc_id = f
            ret.append(m)
    return ret

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

def loadW2V(w2v_file, allowed = None):
    ret = {}
    err = 0
    with codecs.open(w2v_file, "r" , 'utf-8') as input:
        for line in input:
            line = line.strip()
            if len(line) == 0:
                continue
            try:
                w,vec = line.split("\t")
            except ValueError:
#                 print(line)
                err += 1
                continue
            if allowed is not None and w in allowed:
                vec = [float(v) for v in vec.split(" ")]
                ret[w] = np.array(vec)
    print("%d line failed" % err)
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

train_mentions= load_all_data("/home/haowu4/data/ontonotes_ner/ColumnFormat/Train/")
dev_mentions= load_all_data("/home/haowu4/data/ontonotes_ner/ColumnFormat/Dev/")
test_mentions= load_all_data("/home/haowu4/data/ontonotes_ner/ColumnFormat/Test/")
figer_datas = read_figer()

VOCABS = set()
mention_counter = 0
for mention in [train_mentions,dev_mentions,test_mentions, figer_datas]:
    for men in mention:
        mention_counter += 1
        for t in men.tokens:
            VOCABS.add(t)
print("%d mention loaded" % mention_counter)

print("%d word loaded" % len(VOCABS))

w2vdict=loadW2V("/home/haowu4/data/autoextend/GoogleNews-vectors-negative300.combined_500k.txt", VOCABS)
print("%d words have w2v" % len(w2vdict))

default_w2v_mean = np.mean(list(w2vdict.values()), axis=0)
default_w2v_zero = np.zeros(default_w2v_mean.shape)

# Define features:

from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer().lemmatize


def word_shape_func(text):
    text = re.sub("[a-z]+", "a" ,text)
    text = re.sub("[A-Z]+", "A" ,text)
    text = re.sub("[0-9]+", "0" ,text)
    return text


class FeatureFunc(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, original_func):
        decorator_self = self
        def wrappee( *args, **kwargs):
            for feat in original_func(*args,**kwargs):
                yield ("%s=%s" % (self.name, feat), 1.0)
        return wrappee

class RealFeatureFunc(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, original_func):
        decorator_self = self
        def wrappee( *args, **kwargs):
            for feat,v in original_func(*args,**kwargs):
                yield ("%s=%s" % (self.name, feat), v)
        return wrappee

def word_before(pos):
    @FeatureFunc("word_before")
    def f(mention):
        for i in range(max(mention.start-pos,0), mention.start):
            yield mention.tokens[i]
            yield word_shape_func(mention.tokens[i])
    return f

def word_before_loc(pos):
    @FeatureFunc("word_before")
    def f(mention):
        for i in range(max(mention.start-pos,0), mention.start):
            yield "%d-%s" % (mention.start - i,mention.tokens[i])
    return f

def word_before_lemma(pos):
    @FeatureFunc("word_before_lemma")
    def f(mention):
        for i in range(max(mention.start-pos,0), mention.start):
            yield lmtzr(mention.tokens[i])
    return f


def word_after(pos):
    @FeatureFunc("word_after")
    def f(mention):
        for i in range(mention.end, min(mention.end+pos,len(mention.tokens))):
            yield mention.tokens[i]
            yield word_shape_func(mention.tokens[i])
    return f

def word_after_loc(pos):
    @FeatureFunc("word_after_loc")
    def f(mention):
        for i in range(mention.end, min(mention.end+pos,len(mention.tokens))):
            yield "%d-%s" % (i - mention.end,mention.tokens[i])
    return f


def word_after_lemma(pos):
    @FeatureFunc("word_after_lemma")
    def f(mention):
        for i in range(mention.end, min(mention.end+pos,len(mention.tokens))):
            yield lmtzr(mention.tokens[i])

    return f

@FeatureFunc("wim")
def word_in_mention(mention):
    for x in mention.surface:
        yield x
        yield word_shape_func(x)

@FeatureFunc("wim_lemma")
def word_in_mention_lemma(mention):
    for x in mention.surface:
        yield lmtzr(x)


@FeatureFunc("wim_loc")
def word_in_mention_loc(mention):
    for i,x in enumerate(mention.surface):
        yield "f%d-%s" % (i,x)
        yield "b%d-%s" % (len(mention.surface) - i,x)

@FeatureFunc("wim_loc_lemma")
def word_in_mention_loc_lemma(mention):
    for i,x in enumerate(mention.surface):
        x = lmtzr(x)
        yield "f%d-%s" % (i,x)
        yield "b%d-%s" % (len(mention.surface) - i,x)



@FeatureFunc("wim_ext")
def wim_ext(mention):
    for x in mention.ext_surface:
        yield x
        yield word_shape_func(x)

@FeatureFunc("wim_ext_lemma")
def wim_ext_lemma(mention):
    for x in mention.ext_surface:
        x = lmtzr(x)
        yield x

@FeatureFunc("wim_bigram")
def wim_bigram(mention):
    for i,x in zip(mention.surface[:-1], mention.surface[1:]):
        yield "%s-%s" % (i,x)

@FeatureFunc("wim_bigram_lemma")
def wim_bigram_lemma(mention):
    lms = [lmtzr(x) for x in mention.surface]
    for i,x in zip(lms[:-1], lms[1:]):
        yield "%s-%s" % (i,x)



@FeatureFunc("word_shape")
def word_shape(mention):
    t = " ".join(mention.surface)
    return [word_shape_func(t)]

@FeatureFunc("length")
def mention_length(mention):
    return ["%d" % len(mention.surface)]

@FeatureFunc("prefix")
def prefix(mention):
    for w in mention.surface:
        for i in range(1, min(4, len(w))):
            yield w[:i]

@FeatureFunc("surfix")
def postfix(mention):
    for w in mention.surface:
        for i in range(1, min(4, len(w))):
            yield w[-i:]

@FeatureFunc("bias")
def CONSTANT_BIAS(mention):
    return ["bias"]

# def gazzarteer(gas):
#     @FeatureFunc("gazzarteer")
#     def gazzarteer_wrappee(mention):
#         for gz_name in gas:
#             if mention.surface:
#                 return

def getOrDefault(m, k, d):
    if k in m:
        return m[k]
    else:
        return d

def w2vBefore(ws, default_w2v, pos = 4):
    def wrappee(mention):
        words = []
        for i in range(mention.start-pos, mention.start):
            if i < 0:
                words.append(np.zeros(default_w2v.shape))
            else:
                words.append(getOrDefault(ws,mention.tokens[i],default_w2v))
        words.append(np.mean(words, axis=0))
        return np.hstack(words)
    return wrappee

def w2vAfrer(ws, default_w2v, pos = 4):
    def wrappee(mention):
        words = []
        for i in range(mention.end + 1, mention.end + pos + 1):
            if i >= len(mention.tokens):
                words.append(np.zeros(default_w2v.shape))
            else:
                words.append(getOrDefault(ws,mention.tokens[i],default_w2v))
        words.append(np.mean(words, axis=0))
        return np.hstack(words)

    return wrappee

def w2vMention(ws, default_w2v):
    def wrappee(mention):
        if len(mention.surface) == 0:
            print(mention)
        ms = [getOrDefault(ws,w,default_w2v) for w in mention.surface]
        return np.mean(ms, axis=0)
    return wrappee

features = [CONSTANT_BIAS,
            word_before(4), word_before_lemma(4),
            word_after(4), word_after_lemma(4),
            word_in_mention, word_in_mention_lemma,
            word_in_mention_loc, word_in_mention_loc_lemma,
            wim_bigram, wim_bigram_lemma,
            wim_ext, wim_ext_lemma,
            word_shape,
            mention_length,
            prefix,
            postfix,
           ]

default_w2v

dense_feature = [w2vBefore(w2vdict, default_w2v),
                 w2vAfrer(w2vdict, default_w2v),
                 w2vMention(w2vdict, default_w2v)]

def typ_func(m):
    return m.label

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

from sklearn.metrics import f1_score, confusion_matrix
from sklearn import linear_model, datasets, svm, ensemble

logreg = ensemble.BaggingClassifier(base_estimator=linear_model.Perceptron())
# logreg = ensemble.GradientBoostingClassifier()
logreg.fit(xs_train, ys_train)
y_pred = logreg.predict(xs_test)


print("Binary f1  %.3f" % (f1_score(ys_test, y_pred)))

f1 = f1_score(ys_test, y_pred, average=None).tolist()
print(f1)
rd = {type_lex.m[x]:x for x in type_lex.m}

class_names = [None] * len(rd)
for i in range(len(rd)):
    class_names[i] = rd[i]

for k,v in sorted([(rd[k], f1[k]) for k in rd], key=lambda a:a[1], reverse=True):
    print("%15s : %.3f" % (k,v))

counter = 0
for i,m in enumerate(test_mentions):
    if y_pred[i] == ys_test[i]:
        continue
    if m.label == "FAC":
#         print(rd[y_pred[i]],m)
        counter += 1
    if counter == 10:
        break


y_pred_figer = logreg.predict(xs_figer)
matches =  defaultdict(int)
alllabel_matches =  defaultdict(int)

match_examples =  defaultdict(list)
all_labels = 0
for i in range(len(figer_datas)):
    preded = rd[y_pred_figer[i]]
    fine_types = sorted(figer_datas[i].label.split(","))
    alllabel_matches[(preded,",".join(fine_types))] += 1
    for l in fine_types:
        all_labels += 1
        matches[(preded, l)] += 1
        match_examples[(preded, l)].append(figer_datas[i])

figer_len = float(len(figer_datas))
for k in sorted(matches.keys(), key=lambda x : matches[x], reverse=True):
    print(k, "\t\t",matches[k],"\t\t",matches[k]/figer_len)

def get_example(i):
    print(match_examples[('ORG', '/location/city')][i])
get_example(6)

figer_len = float(len(figer_datas))
for k in sorted(alllabel_matches.keys(), key=lambda x : alllabel_matches[x], reverse=True):
    print(k, "\t\t",alllabel_matches[k],"\t\t",alllabel_matches[k]/figer_len)