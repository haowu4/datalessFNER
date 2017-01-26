# -*- coding: utf-8 -*-

import sys
import codecs
import numpy as np
from nltk.corpus import wordnet as wn

quotes = {"\"", "“", "”"}


def read_embeddings(feature_embeddings_file):
    """

    :param feature_embeddings_file: embeddings file with the following format
        <feature>\t<emb_dim1> <emb_dim2> ... <emb_dimn>\n
    :return: feature2index and embeddings as numpy 2-d array
    """
    with codecs.open(feature_embeddings_file, 'r', 'utf-8') as f_in:
        feature2index = {}
        embeddings = []
        for line in f_in:
            tokens = line.strip().split("\t")
            if len(tokens) != 2:
                continue
            feature = tokens[0]
            embedding = map(float, tokens[1].split())
            feature2index[feature] = len(embeddings)
            embeddings.append(embedding)
    embeddings = np.array(embeddings)
    return feature2index, embeddings


def syn_to_offset_pos(synset):
    return "%d_%s" % (synset.offset(), synset.pos())


def syn_from_offset_pos(offset, pos):
    return wn._synset_from_pos_and_offset(pos, int(offset))


def read_synset_embeddings(synset_offset_pos_embeddings_file, only_noun=True):
    synset_offset_pos2index, embeddings = read_embeddings(
        synset_offset_pos_embeddings_file)
    # pdb.set_trace()
    synset2index, synset_embeddings = {}, []
    all_synsets = wn.all_synsets(wn.NOUN if only_noun else None)
    for synset in all_synsets:
        synset_offset_pos = "%d_%s" % (synset.offset(), synset.pos())
        if synset_offset_pos not in synset_offset_pos2index:
            continue
        embedding = embeddings[synset_offset_pos2index[synset_offset_pos]]
        synset2index[synset] = len(synset_embeddings)
        synset_embeddings.append(embedding)
    return synset2index, synset_embeddings


def span_tuple1_covers_span_tuple2(span_tuple1, span_tuple2):
    start1, end1 = span_tuple1
    start2, end2 = span_tuple2
    return start1 <= start2 and end1 >= end2


def fine_type_to_ontonote_types(fine_type):
    # validate this with statistics
    if fine_type.startswith("person"):
        return ["PERSON"]
    if fine_type.startswith("building"):
        return ["ORG", "FACILITY"]


def simple_decorator(decorator):
    '''This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.'''
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator


def get_size(obj, seen=None):
    """Recursively finds size of objects in bytes"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum((get_size(v, seen) for v in obj.values()))
        size += sum((get_size(k, seen) for k in obj.keys()))
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum((get_size(i, seen) for i in obj))
    return size


if __name__ == '__main__':
    embeddings_path = \
        "/shared/preprocessed/muddire2/Google/GoogleNews-vectors-negative300.combined_500k.txt"
    word2index, word_embeddings = read_embeddings(embeddings_path)
    assert len(word2index) == len(word_embeddings)

    synset_offset_pos_embeddings_path = \
        "/shared/preprocessed/muddire2/Google/synset_embeddings_300.txt"
    synset2index, synset_embeddings = read_synset_embeddings(synset_offset_pos_embeddings_path, only_noun=True)
    assert len(synset2index) == len(synset_embeddings)
