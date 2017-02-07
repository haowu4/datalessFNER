import numpy as np


def getOrDefault(m, k, d):
    if k in m:
        return m[k]
    else:
        return d


def w2vBefore(w2v_dict, default_w2v, pos=4):
    def w2vBefore(doc, mention):
        word_vecs = []
        for i in range(mention.start - pos, mention.start):
            if i < 0:
                word_vecs.append(np.zeros(default_w2v.shape))
            else:
                word_vecs.append(getOrDefault(w2v_dict, doc[i].text, default_w2v))
        word_vecs.append(np.mean(word_vecs, axis=0))
        return np.hstack(word_vecs)

    return w2vBefore


def w2vAfter(w2v_dict, default_w2v, pos=4):
    def w2vAfter(doc, mention):
        word_vecs = []
        for i in range(mention.end, mention.end + pos):
            if i >= len(mention.tokens):
                word_vecs.append(np.zeros(default_w2v.shape))
            else:
                word_vecs.append(getOrDefault(w2v_dict, doc[i].text, default_w2v))
        word_vecs.append(np.mean(word_vecs, axis=0))
        return np.hstack(word_vecs)

    return w2vAfter


def w2vMention(w2v_dict, default_w2v):
    def w2vMention(doc, mention):
        if mention.start == mention.end:
            print(doc)
        mean_vecs = [getOrDefault(w2v_dict, token.text, default_w2v) for token in doc[mention.start:mention.end]]
        return np.mean(mean_vecs, axis=0)

    return w2vMention


def topicSentence(sentEmbeddingFunc, feature_name):
    def topicSentence(doc, mention):
        tokenized_doc = [token.text for token in doc]
        return sentEmbeddingFunc(tokenized_doc)

    topicSentence.__name__ = feature_name
    return topicSentence