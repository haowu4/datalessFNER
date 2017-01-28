# -*- coding: utf-8 -*-
import cPickle as pickle
import os

import numpy as np
import spacy
from nltk.corpus import wordnet as wn, stopwords
from dfiner.utils.utils import read_embeddings, syn_to_offset_pos, get_default_config


class AverageEmbeddingNSD(object):
    """The class provides noun sense disambiguation

    """

    def __init__(self, word_embeddings_path, synset_offset_pos_embeddings_path, stopwords_set=None):
        """

        :param word_embeddings_path: embeddings file with the following format
        <word>\t<emb_dim1> <emb_dim2> ... <emb_dimn>\n
        :param synset_offset_pos_embeddings_path: embeddings file with the following format
        <synset_offset_pos>\t<emb_dim1> <emb_dim2> ... <emb_dimn>\n
        """

        self._word2index, self._word_embeddings = read_embeddings(word_embeddings_path)
        self._synset_offset_pos2index, self._synset_embeddings = read_embeddings(synset_offset_pos_embeddings_path)
        self._stopwords_set = stopwords_set if stopwords_set else set(stopwords.words('english'))
        self.index2synset_offset_pos = {index: synset for synset, index in self._synset_offset_pos2index.iteritems()}

    def disambiguate_or_none(self, doc, target_span):
        """

        :param doc: spacy Doc - used here as a tokens generator object
        :param target_span: span (tuple - (start, end)) in tokens to perform WSD on
        :return: if context embedding was possible and synsets and their embedding exist
                 synset score dictionary (synset_index as key and score as value) is returned else None
        """

        start, end = target_span
        target_text = "_".join([token.text for token in doc[start:end]])
        target_token_syns = [syn_to_offset_pos(syn) for syn in wn.synsets(target_text, 'n')]
        if len(target_token_syns) == 0:
            # print("target token has no synsets in wordnet")
            return None
        context_embs = []
        for token_index, token in enumerate(doc):
            if (token_index < start or token_index >= end) \
                    and token.text in self._word2index \
                    and token.text.lower() not in self._stopwords_set:
                context_embs.append(self._word_embeddings[self._word2index[token.text]])
        if len(context_embs) == 0:
            # print("no content word got hit in word2index")
            return None
        context_emb = np.sum(context_embs, axis=0).flatten()
        context_emb /= np.linalg.norm(context_emb)
        syn_scores = {}
        for i, syn_offset_pos in enumerate(target_token_syns):
            if syn_offset_pos in self._synset_offset_pos2index:
                syn_emb = self._synset_embeddings[self._synset_offset_pos2index[syn_offset_pos]]
                norm = np.linalg.norm(syn_emb)
                syn_emb /= (norm if norm > 0 else 1.)
                syn_scores[self._synset_offset_pos2index[syn_offset_pos]] = syn_emb.dot(context_emb)
            else:
                syn_scores[self._synset_offset_pos2index[syn_offset_pos]] = 0.
        return syn_scores

    def save_to_pickle(self, pickle_path):
        with open(pickle_path, "wb") as f_out:
            pickle.dump((self._synset_offset_pos2index, self._synset_embeddings, self._word2index, self._word_embeddings,
                         self._stopwords_set, self.index2synset_offset_pos), f_out, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load_instance_from_pickle(cls, pickle_path):
        with open(pickle_path) as f_in:
            data = pickle.load(f_in)
        instance = cls.__new__(cls)
        (instance._synset_offset_pos2index, instance._synset_embeddings, instance._word2index,
         instance._word_embeddings, instance._stopwords_set, instance.index2synset_offset_pos) = data
        return instance


class NounSenseAnnotator(object):
    """Can be used as a member of pipeline for adding noun sense annotation to the doc object

    This takes in a doc, checks all noun ngrams (where the starting and ending word is a NOUN) for
     hits in wordnet and uses the Noun Sense Disambiguation object passed to it to get sense scores
     for each of these noun ngrams.

     The scores are are added to doc.user_data with NSD_VIEW as key and list of tuples of the form
     ((start_ngram, end_ngram), {sense1: score, ..., sensen: score})

    """

    NSD_VIEW = "nsd_view"
    INDEX_TO_OFFSET_POS = "index_to_offset_pos"

    def __init__(self, nsd, ngram=2):
        self.nsd = nsd
        self.index2synset_offset_pos = nsd.index2synset_offset_pos
        self.ngram_length = ngram

    def __call__(self, doc):
        doc_len = len(doc)
        nsd_view = []
        doc.user_data[self.NSD_VIEW] = nsd_view
        starts_with_NN = [token.tag_.startswith("NN") for token in doc]
        i = 0
        while i <= doc_len-1:
            for n in xrange(self.ngram_length, 0, -1):
                start, end = i, i+n
                # ensure ngram is within doc and
                # first and last one is noun (Random rule I came up with. Validate this)
                if end > doc_len or not (starts_with_NN[start] and starts_with_NN[end-1]):
                    continue
                span_tuple = (start, end)
                if self.check_and_add_ngram_sense_scores(doc, i, n, nsd_view):
                    break
            # whether break happened or not the n is the number to skip forward to
            i += n
        doc.user_data[self.INDEX_TO_OFFSET_POS] = self.index2synset_offset_pos

    def check_and_add_ngram_sense_scores(self, doc, i, n, view):
        span_tuple = (i, i+n)
        ngram_sense_scores = self.nsd.disambiguate_or_none(doc, span_tuple)
        if ngram_sense_scores:
            view.append((span_tuple, ngram_sense_scores))
            return True
        else:
            return False


if __name__ == '__main__':

    # default config
    default_config = get_default_config()

    nsd = None
    nsd_cache_path = default_config["nsd_cache_path"]
    embeddings_path = default_config["embeddings_path"]
    synset_offset_pos_embeddings_path = default_config["synset_offset_pos_embeddings_path"]
    if os.path.isfile(nsd_cache_path):
        try:
            nsd = AverageEmbeddingNSD.load_instance_from_pickle(nsd_cache_path)
        except:
            print("Encountered error while loading pickle from " + nsd_cache_path)
    nsd = nsd if nsd else AverageEmbeddingNSD(embeddings_path, synset_offset_pos_embeddings_path)

    def create_pipeline(nlp):
        return [nlp.tagger, nlp.entity, nlp.parser, NounSenseAnnotator(nsd)]

    nlp = spacy.load('en', create_pipeline=create_pipeline)
    doc = nlp("Barack Hussein Obama II (US Listeni/bəˈrɑːk huːˈseɪn oʊˈbɑːmə/ bə-rahk hoo-sayn oh-bah-mə;[1][2] born August 4, 1961) is an American politician who served as the 44th President of the United States from 2009 to 2017. Obama is a member of the Democratic Party, and was the first African American and first person born outside the contiguous United States to serve as president.".decode("utf-8"))

    print(doc.user_data[NounSenseAnnotator.NSD_VIEW])
