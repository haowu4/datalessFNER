# Define features:
import re

from nltk.stem.wordnet import WordNetLemmatizer
lmtzr = WordNetLemmatizer().lemmatize


class FeatureFunc(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, original_func):
        decorator_self = self

        def wrappee(*args, **kwargs):
            for feat in original_func(*args, **kwargs):
                yield ("%s=%s" % (decorator_self.name, feat), 1.0)
        return wrappee


class RealFeatureFunc(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, original_func):
        decorator_self = self

        def wrappee(*args, **kwargs):
            for feat, v in original_func(*args, **kwargs):
                yield ("%s=%s" % (decorator_self.name, feat), v)
        return wrappee


def word_shape_func(text):
    text = re.sub("[a-z]+", "a", text)
    text = re.sub("[A-Z]+", "A", text)
    text = re.sub("[0-9]+", "0", text)
    return text


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


