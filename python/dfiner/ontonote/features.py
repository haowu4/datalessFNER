# Define features:
import re
import numpy as np

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


@FeatureFunc("dep_feature")
def mention_details(doc, start, end):
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
    def f(doc, start, end):
        for i in range(max(start-pos,0), start):
            yield doc[i].text
#             yield word_shape_func(doc[i].text)
    return f

def word_before_loc(pos):
    @FeatureFunc("word_before")
    def f(doc, start, end):
        for i in range(max(start-pos,0), start):
            yield "%d-%s" % (start - i,doc[i].text)
    return f

def word_before_lemma(pos):
    @FeatureFunc("word_before_lemma")
    def f(doc, start, end):
        for i in range(max(start-pos,0), start):
            yield doc[i].lemma_
    return f


def word_after(pos):
    @FeatureFunc("word_after")
    def f(doc, start, end):
        for i in range(end, min(end+pos,len(doc))):
            yield doc[i].text
#             yield word_shape_func(doc[i].text)
    return f

def word_after_loc(pos):
    @FeatureFunc("word_after_loc")
    def f(doc, start, end):
        for i in range(end, min(end+pos,len(doc))):
            yield "%d-%s" % (i - end,doc[i].text)
    return f


def word_after_lemma(pos):
    @FeatureFunc("word_after_lemma")
    def f(doc, start, end):
        for i in range(end, min(end+pos,len(doc))):
            yield doc[i].lemma_

    return f

@FeatureFunc("wim")
def word_in_mention(doc, start, end):
    for x in doc[start:end]:
        yield x.text
        yield word_shape_func(x.text)

@FeatureFunc("wim_lemma")
def word_in_mention_lemma(doc, start, end):
    for x in doc[start:end]:
        yield x.lemma_


@FeatureFunc("wim_loc")
def word_in_mention_loc(doc, start, end):
    for i,x in enumerate(doc[start:end]):
        yield "f%d-%s" % (i,x.text)
        yield "b%d-%s" % ((end-start) - i,x.text)

@FeatureFunc("wim_loc_lemma")
def word_in_mention_loc_lemma(doc, start, end):
    for i,x in enumerate(doc[start:end]):
        x = x.lemma_
        yield "f%d-%s" % (i,x)
        yield "b%d-%s" % ((end-start)-i,x)



# @FeatureFunc("wim_ext")
# def wim_ext(doc, start, end):
#     for x in mention.ext_surface:
#         yield x
#         yield word_shape_func(x)

# @FeatureFunc("wim_ext_lemma")
# def wim_ext_lemma(doc, start, end):
#     for x in mention.ext_surface:
#         x = lmtzr(x)
#         yield x

@FeatureFunc("wim_bigram")
def wim_bigram(doc, start, end):
    for i,x in zip(doc[start:end-1], doc[start+1:end]):
        yield "%s-%s" % (i.text,x.text)

@FeatureFunc("wim_bigram_lemma")
def wim_bigram_lemma(doc, start, end):
    lms = [x.lemma_ for x in doc[start:end]]
    for i,x in zip(lms[:-1], lms[1:]):
        yield "%s-%s" % (i,x)



@FeatureFunc("word_shape")
def word_shape(doc, start, end):
    t = " ".join([x.text for x in doc[start:end]])
    return [word_shape_func(t)]

@FeatureFunc("length")
def mention_length(doc, start, end):
    return ["%d" % (end-start)]

@FeatureFunc("prefix")
def prefix(doc, start, end):
    for w in doc[start:end]:
        for i in range(3, min(5, len(w.text))):
            yield w.text[:i]

@FeatureFunc("surfix")
def postfix(doc, start, end):
    for w in doc[start:end]:
        for i in range(3, min(5, len(w.text))):
            yield w.text[-i:]

@FeatureFunc("bias")
def CONSTANT_BIAS(doc, start, end):
    return ["bias"]

# def gazzarteer(gas):
#     @FeatureFunc("gazzarteer")
#     def gazzarteer_wrappee(mention):
#         for gz_name in gas:
#             if doc:
#                 return

def getOrDefault(m, k, d):
    if k in m:
        return m[k]
    else:
        return d

def w2vBefore(ws, default_w2v, pos = 4):
    def wrappee(doc, start, end):
        words = []
        for i in range(start-pos, start):
            if i < 0:
                words.append(np.zeros(default_w2v.shape))
            else:
                words.append(getOrDefault(ws,doc[i].text,default_w2v))
        words.append(np.mean(words, axis=0))
        return np.hstack(words)
    return wrappee

def w2vAfrer(ws, default_w2v, pos = 4):
    def wrappee(doc, start, end):
        words = []
        for i in range(end, end + pos):
            if i >= len(doc):
                words.append(np.zeros(default_w2v.shape))
            else:
                words.append(getOrDefault(ws,doc[i].text,default_w2v))
        words.append(np.mean(words, axis=0))
        return np.hstack(words)

    return wrappee

def w2vMention(ws, default_w2v):
    def wrappee(doc, start, end):
        if len(doc) == 0:
            print(mention)
        ms = [getOrDefault(ws, w.text, default_w2v) for w in doc]
        return np.mean(ms, axis=0)
    return wrappee

MAX_PATH_LEN = 4
UP = 1
DOWN = 2

def shortest_path((x, y)):
    """ Returns the shortest dependency path from x to y
    :param x: x token
    :param y: y token
    :return: the shortest dependency path from x to y
    """

    x_token = x
    y_token = y
    if not isinstance(x_token, spacy.tokens.token.Token):
        x_token = x_token.root
    if not isinstance(y_token, spacy.tokens.token.Token):
        y_token = y_token.root

    # Get the path from the root to each of the tokens
    hx = heads(x_token)
    hy = heads(y_token)

    # Get the lowest common head
    i = -1
    for i in xrange(min(len(hx), len(hy))):
        if hx[i] is not hy[i]:
            break

    if i == -1:
        lch_idx = 0
        if len(hy) > 0:
            lch = hy[lch_idx]
        elif len(hx) > 0:
            lch = hx[lch_idx]
        else:
            lch = None
    elif hx[i] == hy[i]:
        lch_idx = i
        lch = hx[lch_idx]
    else:
        lch_idx = i-1
        lch = hx[lch_idx]

    # The path from x to the lowest common head
    hx = hx[lch_idx+1:]
    if lch and check_direction(lch, hx, lambda h: h.lefts):
        return None
    hx = hx[::-1]

    # The path from the lowest common head to y
    hy = hy[lch_idx+1:]
    if lch and check_direction(lch, hy, lambda h: h.rights):
        return None

    return (x, hx, lch, hy, y)


def shortest_path2((x, y)):
    """ Returns the shortest dependency path from x to y
    :param x: x token
    :param y: y token
    :return: the shortest dependency path from x to y
    """

    x_token = x
    y_token = y
    if not isinstance(x_token, spacy.tokens.token.Token):
        x_token = x_token.root
    if not isinstance(y_token, spacy.tokens.token.Token):
        y_token = y_token.root

    # Get the path from the root to each of the tokens including the tokens
    hx = heads(x_token) + [x_token]
    hy = heads(y_token) + [y_token]

    # Get the lowest common head
    i = -1
    for i in xrange(min(len(hx), len(hy))):
        if hx[i] is not hy[i]:
            break

    # i cannot be -1 since the path should atleast have the ROOT as the common ancestor
    if hx[i] == hy[i]:
        lch_idx = i
        lch = hx[lch_idx]
    else:
        lch_idx = i-1
        lch = hx[lch_idx]

    # The path from x to the lowest common head
    hx = hx[lch_idx+1:-1]
    hx = hx[::-1]

    # The path from the lowest common head to y
    hy = hy[lch_idx+1:-1]

    return (x, hx, lch, hy, y)


def heads(token):
    """
    Return the heads of a token, from the root down to immediate head
    :param token:
    :return:
    """
    t = token
    hs = []
    while t is not t.head:
        t = t.head
        hs.append(t)
    return hs[::-1]


def direction(dir):
    """
    Print the direction of the edge
    :param dir: the direction
    :return: a string representation of the direction
    """
    # Up to the head
    if dir == UP:
        return '>'
    # Down from the head
    elif dir == DOWN:
        return '<'


def token_to_string(token):
    """
    Convert the token to string representation
    :param token:
    :return:
    """
    if not isinstance(token, spacy.tokens.token.Token):
        return ' '.join([t.string.strip().lower() for t in token])
    else:
        return token.string.strip().lower()


def token_to_lemma(token):
    """
    Convert the token to string representation
    :param token: the token
    :return: string representation of the token
    """
    if not isinstance(token, spacy.tokens.token.Token):
        return token_to_string(token)
    else:
        return token.lemma_.strip().lower()


def clean_path((x, hx, lch, hy, y), entity_on_left=True, include_target_pos=False):
    """
    Filter out long paths and pretty print the short ones
    :return: the string representation of the path
    """

    def argument_to_string(token, edge_name, include_pos=False):
        """
        Converts the argument token (X or Y) to an edge string representation
        :param token: the X or Y token
        :param edge_name: 'X' or 'Y'
        :return:
        """
        if not isinstance(token, spacy.tokens.token.Token):
            token = token.root

        if include_pos:
            return '/'.join([edge_name, token.pos_, token.dep_ if token.dep_ != '' else 'ROOT'])
        else:
            return '/'.join([edge_name, token.dep_ if token.dep_ != '' else 'ROOT'])

    def edge_to_string(token, is_head=False, is_lexicalized=True):
        """
        Converts the token to an edge string representation
        :param token: the token
        :return: the edge string
        """
        t = token
        if not isinstance(token, spacy.tokens.token.Token):
            t = token.root

        if is_lexicalized:
            return '/'.join([token_to_lemma(token), t.dep_ if t.dep_ != '' and not is_head else 'ROOT'])
        else:
            return '/'.join([t.pos_, t.dep_ if t.dep_ != '' and not is_head else 'ROOT'])


    lch_lex_lst = []
    lch_pos_lst = []

    # X is the head
    if isinstance(x, spacy.tokens.token.Token) and lch == x:
        dir_x = ''
        dir_y = direction(DOWN)
    # Y is the head
    elif isinstance(y, spacy.tokens.token.Token) and lch == y:
        dir_x = direction(UP)
        dir_y = ''
    # X and Y are not heads
    else:
        lch_lex_lst = [edge_to_string(lch, is_head=True, is_lexicalized=True)] if lch else []
        lch_pos_lst = [edge_to_string(lch, is_head=True, is_lexicalized=False)] if lch else []
        dir_x = direction(UP)
        dir_y = direction(DOWN)

    len_path = len(hx) + len(hy) + len(lch_lex_lst)

    if len_path <= MAX_PATH_LEN:
#     if True:
        mid_lex_path = (
            [edge_to_string(token, is_lexicalized=True) + direction(UP) for token in hx] +
            lch_lex_lst +
            [direction(DOWN) + edge_to_string(token, is_lexicalized=True) for token in hy]
        )

        mid_pos_path = (
            [edge_to_string(token, is_lexicalized=False) + direction(UP) for token in hx] +
            lch_pos_lst +
            [direction(DOWN) + edge_to_string(token, is_lexicalized=False) for token in hy]
        )

        if entity_on_left:
            yield '_'.join(['ENT' + dir_x] + mid_lex_path +
                           [dir_y + argument_to_string(y, y.lemma_, include_pos=include_target_pos)])
            yield '_'.join(['ENT' + dir_x] + mid_pos_path +
                           [dir_y + argument_to_string(y, y.lemma_, include_pos=include_target_pos)])
        else:
            yield '_'.join([argument_to_string(x, x.lemma_, include_pos=include_target_pos) + dir_x] +
                           mid_lex_path + [dir_y + 'ENT'])
            yield '_'.join([argument_to_string(x, x.lemma_, include_pos=include_target_pos) + dir_x] +
                           mid_pos_path + [dir_y + 'ENT'])
    else:
        return
        yield

@FeatureFunc("prp_wh_dep_feat")
def mention_pronoun_wh_dep(doc, start, end):
    PRP_SYM = nlp.vocab.strings["PRP"]
    WH_SYM = nlp.vocab.strings["WP"]
    prp_tokens = [token for token in doc if token.tag == PRP_SYM]
    wh_tokens = [token for token in doc if token.tag == WH_SYM]
    for mention_token in doc[start:end]:
        for target_token in prp_tokens + wh_tokens:
            path = shortest_path2((mention_token, target_token))
            for cleaned_path in clean_path(path):
                yield cleaned_path


def get_default_feature():
    default_features = [CONSTANT_BIAS,
                        mention_details,
                        word_in_mention, word_in_mention_lemma,
                        word_in_mention_loc, word_in_mention_loc_lemma,
                        wim_bigram, wim_bigram_lemma]
    return default_features


def get_default_dense_feature(w2vdict, dv):
    default_features = [w2vMention(w2vdict, dv)]
    return default_features
