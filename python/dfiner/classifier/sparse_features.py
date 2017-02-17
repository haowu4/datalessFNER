import re
from functools import wraps


def word_shape_func(text):
    text = re.sub("[a-z]+", "a", text)
    text = re.sub("[A-Z]+", "A", text)
    text = re.sub("[0-9]+", "0", text)
    return text


class FeatureFunc(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, original_func):
        decorator_self = self

        @wraps(original_func)
        def wrappee(*args, **kwargs):
            for feat in original_func(*args, **kwargs):
                yield ("%s=%s" % (self.name, feat), 1.0)

        return wrappee


class RealFeatureFunc(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, original_func):
        decorator_self = self

        @wraps(original_func)
        def wrappee(*args, **kwargs):
            for feat, v in original_func(*args, **kwargs):
                yield ("%s=%s" % (self.name, feat), v)

        return wrappee


@FeatureFunc("dep_feature")
def mention_details(doc, mention):
    start, end = mention.start, mention.end
    heads = [token.head for token in doc[start:end]]
    deps = [list(token.children) for token in doc[start:end]]
    for token, head, children in zip(doc[start:end], heads, deps):
        if not (head.i >= start and head.i < end):
            yield "<-%s- %s" % (token.dep_, head.lemma_)
            yield "<- %s" % (head.lemma_)
        for child in children:
            if not (child.i >= start and child.i < end):
                yield "-%s-> %s" % (child.dep_, child.lemma_)
                yield "-> %s" % (child.lemma_)


def word_before(pos):
    @FeatureFunc("word_before")
    def f(doc, mention):
        start, end = mention.start, mention.end
        for i in range(max(start - pos, 0), start):
            yield doc[i].text

    return f


def word_before_loc(pos):
    @FeatureFunc("word_before")
    def f(doc, mention):
        start, end = mention.start, mention.end
        for i in range(max(start - pos, 0), start):
            yield "%d-%s" % (start - i, doc[i].text)

    return f


def word_before_lemma(pos):
    @FeatureFunc("word_before_lemma")
    def f(doc, mention):
        start, end = mention.start, mention.end
        for i in range(max(start - pos, 0), start):
            yield doc[i].lemma_

    return f


def word_after(pos):
    @FeatureFunc("word_after")
    def f(doc, mention):
        start, end = mention.start, mention.end
        for i in range(end, min(end + pos, len(doc))):
            yield doc[i].text

    return f


def word_after_loc(pos):
    @FeatureFunc("word_after_loc")
    def f(doc, mention):
        start, end = mention.start, mention.end
        for i in range(end, min(end + pos, len(doc))):
            yield "%d-%s" % (i - end, doc[i].text)

    return f


def word_after_lemma(pos):
    @FeatureFunc("word_after_lemma")
    def f(doc, mention):
        start, end = mention.start, mention.end
        for i in range(end, min(end + pos, len(doc))):
            yield doc[i].lemma_

    return f


@FeatureFunc("wim")
def word_in_mention(doc, mention):
    start, end = mention.start, mention.end
    for token in doc[start:end]:
        yield token.text
        yield word_shape_func(token.text)


@FeatureFunc("wim_lemma")
def word_in_mention_lemma(doc, mention):
    start, end = mention.start, mention.end
    for token in doc[start:end]:
        yield token.lemma_


@FeatureFunc("wim_loc")
def word_in_mention_loc(doc, mention):
    start, end = mention.start, mention.end
    for i, x in enumerate(doc[start:end]):
        yield "f%d-%s" % (i, x.text)
        yield "b%d-%s" % ((end - start - 1) - i, x.text)


@FeatureFunc("wim_loc_lemma")
def word_in_mention_loc_lemma(doc, mention):
    start, end = mention.start, mention.end
    for i, x in enumerate(doc[start:end]):
        x = x.lemma_
        yield "f%d-%s" % (i, x)
        yield "b%d-%s" % ((end - start - 1) - i, x)


def wim_ngram(n=2):
    @FeatureFunc("wim_%dgram" % n)
    def f(doc, mention):
        start, end = mention.start, mention.end
        words = map(lambda token: token.text, doc[start:end])
        for ngram_tup in zip(*[words[i:] for i in xrange(n)]):
            yield "-".join(ngram_tup)
    f.__name__ = "wim_%dgram" % n

    return f


def wim_ngram_lemma(n=2):
    @FeatureFunc("wim_%dgram_lemma" % n)
    def f(doc, mention):
        start, end = mention.start, mention.end
        words = map(lambda token: token.lemma_, doc[start:end])
        for ngram_tup in zip(*[words[i:] for i in xrange(n)]):
            yield "-".join(ngram_tup)
    f.__name__ = "wim_%dgram_lemma" % n

    return f


@FeatureFunc("word_shape")
def word_shape(doc, mention):
    start, end = mention.start, mention.end
    t = " ".join([x.text for x in doc[start:end]])
    return [word_shape_func(t)]


@FeatureFunc("length")
def mention_length(doc, mention):
    start, end = mention.start, mention.end
    return ["%d" % (end - start)]


@FeatureFunc("prefix")
def prefix(doc, mention):
    start, end = mention.start, mention.end
    for w in doc[start:end]:
        for i in range(3, min(5, len(w.text))):
            yield w.text[:i]


@FeatureFunc("suffix")
def postfix(doc, mention):
    start, end = mention.start, mention.end
    for w in doc[start:end]:
        for i in range(3, min(5, len(w.text))):
            yield w.text[-i:]


# KB-Bias features
def kbbias(kbbias_annotator):
    @RealFeatureFunc("kbbias")
    def kbbias(doc, mention):
        surface = doc[mention.start:mention.end].text
        results = None
        if surface in kbbias_annotator.surface_to_type_dist:
            results = kbbias_annotator.surface_to_type_dist[surface]
        elif (surface[:4].lower() == 'the ') and \
                surface[4:] in kbbias_annotator.surface_to_type_dist:
            results = kbbias_annotator.surface_to_type_dist[surface[4:]]
        if results:
            return results.iteritems()
        else:
            return []

    return kbbias


@FeatureFunc("bias")
def constant_bias(doc, mention):
    start, end = mention.start, mention.end
    return ["bias"]


