# -*- coding: utf-8 -*-

import os

import spacy
from dfiner.annotators.annotator_helpers.sense_typer import SynsetFineTyper
from dfiner.annotators.nsd_annotator import NounSenseAnnotator, AverageEmbeddingNSD
from dfiner.utils.utils import quotes, get_default_config


def distance_filter(doc, mention_span_tuple, trigger_tuples, max_distance=5):
    mention_start, mention_end = mention_span_tuple

    def is_close(trigger_tuple):
        (trigger_start, trigger_end), _ = trigger_tuple
        return not (trigger_start < mention_start - max_distance or
                    trigger_end > mention_end + max_distance)

    return filter(is_close, trigger_tuples)


def quotation_filter(doc, mention_span_tuple, trigger_tuples):
    mention_start, mention_end = mention_span_tuple

    def is_quote_in_middle(trigger_tuple):
        (trigger_start, trigger_end), _ = trigger_tuple
        for i in xrange(mention_start+1, trigger_start):
            if doc[i].text in quotes:
                return False
        for i in xrange(trigger_start+1, mention_start):
            if doc[i].text in quotes:
                return False
        return True

    return filter(is_quote_in_middle, trigger_tuples)


class RuleBasedFineTypeAnnotator(object):

    FINE_TYPE_VIEW = "fine_type_view"

    def __init__(self, sense_typer, use_view=None):
        """

        :param sense_typer: Instance of SynsetFineTyper - converts a given offset_pos string outputs fine types.
        :param use_view: View to be used for mentions. If not given uses inbuilt entity detection for mentions.
        """
        self.sense_typer = sense_typer
        self.use_view = use_view

    def __call__(self, doc):
        # doc should have NSD_VIEW
        if not NounSenseAnnotator.NSD_VIEW in doc.user_data:
            raise ValueError("NSD_VIEW missing from doc.user_data")
        if not NounSenseAnnotator.INDEX_TO_OFFSET_POS in doc.user_data:
            raise ValueError("INDEX_TO_OFFSET_POS missing from doc.user_data")
        if self.use_view and self.use_view not in doc.user_data:
            raise ValueError(self.use_view + " missing from doc.user_data")
        nsd_view = doc.user_data[NounSenseAnnotator.NSD_VIEW]
        fine_ent_view = []
        if self.use_view:
            view = doc.user_data[self.use_view]
            for mention_span_tuple, _ in view:
                filtered_trigger_tuples = \
                    quotation_filter(doc, mention_span_tuple, distance_filter(doc, mention_span_tuple, nsd_view))
                # Currently set for high recall. So outputs all the fine types of all trigger words after filtering
                fine_types = set()
                for trigger_tuple in filtered_trigger_tuples:
                    _, sense_scores = trigger_tuple
                    # sense is same as synset_offset_pos
                    for synset_index in sense_scores:
                        offset_pos =  doc.user_data[NounSenseAnnotator.INDEX_TO_OFFSET_POS][synset_index]
                        for fine_type in self.sense_typer.get_fine_types(offset_pos):
                            fine_types.add(fine_type)
                if len(fine_types) > 0:
                    fine_ent_view.append((mention_span_tuple, fine_types))
        else:
            for ent in doc.ents:
                ent_span_tuple = (ent.start, ent.end)
                filtered_trigger_tuples = quotation_filter(doc, ent_span_tuple,
                                                           distance_filter(doc, ent_span_tuple, nsd_view))
                # Currently set for high recall. So outputs all the fine types of all trigger words after filtering
                fine_types = set()
                for trigger_tuple in filtered_trigger_tuples:
                    _, sense_scores = trigger_tuple
                    # sense is same as synset_offset_pos
                    for synset_index in sense_scores:
                        offset_pos =  doc.user_data[NounSenseAnnotator.INDEX_TO_OFFSET_POS][synset_index]
                        for fine_type in self.sense_typer.get_fine_types(offset_pos):
                            fine_types.add(fine_type)
                if len(fine_types) > 0:
                    fine_ent_view.append((ent_span_tuple, fine_types))

        doc.user_data[self.FINE_TYPE_VIEW] = fine_ent_view


def get_nlp_with_fine_annotator(config, use_view=None):
    sense_typer = SynsetFineTyper(config["figer_type_senses"])

    nsd_cache_path = default_config["nsd_cache_path"]
    embeddings_path = default_config["embeddings_path"]
    synset_offset_pos_embeddings_path = default_config["synset_offset_pos_embeddings_path"]

    nsd = None
    if os.path.isfile(nsd_cache_path):
        try:
            nsd = AverageEmbeddingNSD.load_instance_from_pickle(nsd_cache_path)
        except:
            print("Encountered error while loading pickle from " + nsd_cache_path)

    nsd = nsd if nsd else AverageEmbeddingNSD(embeddings_path, synset_offset_pos_embeddings_path)

    def create_pipeline(nlp):
        return [nlp.tagger, nlp.entity, nlp.parser, NounSenseAnnotator(nsd),
                RuleBasedFineTypeAnnotator(sense_typer, use_view)]
    nlp = spacy.load('en', create_pipeline=create_pipeline)

    return nlp


if __name__ == '__main__':

    # use default config
    default_config = get_default_config()
    nlp = get_nlp_with_fine_annotator(default_config)

    doc = nlp(
        "Barack Hussein Obama II (US Listeni/bəˈrɑːk huːˈseɪn oʊˈbɑːmə/ bə-rahk hoo-sayn oh-bah-mə;[1][2] born August 4, 1961) is an American politician who served as the 44th President of the United States from 2009 to 2017. Obama is a member of the Democratic Party, and was the first African American and first person born outside the contiguous United States to serve as president.".decode(
            "utf-8"))
