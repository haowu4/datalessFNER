import os
import json
import codecs
from collections import OrderedDict


class Mention(object):
    def __init__(self, start, end, label, tokens, doc_id=""):
        self.start = start
        self.end = end
        self.label = label
        self.tokens = tokens
        self.surface = [tokens[i] for i in range(start, end)]
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
        fn = os.path.join(base_folder, f)
        ms = load_ontonotes(fn)
        for m in ms:
            m.doc_id = f
            ret.append(m)
    return ret


def loadW2V(w2v_file, allowed=None):
    ret = {}
    err = 0
    with codecs.open(w2v_file, "r", 'utf-8') as input:
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


def get_data():
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

