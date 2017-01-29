# -*- coding: utf-8 -*-

import os

import spacy
from dfiner.annotators.annotator_helpers.sense_typer import SynsetFineTyper
from dfiner.annotators.nsd_annotator import NounSenseAnnotator, AverageEmbeddingNSD, NSDView
from dfiner.datastructures import View
from dfiner.utils import quotes, get_default_config


def distance_filter(doc, mention_span_tuple, constituents, max_distance=5):
    mention_start, mention_end = mention_span_tuple

    def is_close(constituent):
        trigger_start, trigger_end = constituent.start, constituent.end
        return not (trigger_start < mention_start - max_distance or
                    trigger_end > mention_end + max_distance)

    return filter(is_close, constituents)


def quotation_filter(doc, mention_span_tuple, constituents):
    mention_start, mention_end = mention_span_tuple

    def is_quote_in_middle(constituent):
        trigger_start, trigger_end = constituent.start, constituent.end
        for i in xrange(mention_start+1, trigger_start):
            if doc[i].text in quotes:
                return False
        for i in xrange(trigger_start+1, mention_start):
            if doc[i].text in quotes:
                return False
        return True

    return filter(is_quote_in_middle, constituents)


class FineTypeView(View):
    FINE_TYPE_VIEW_NAME = 'fine_type_view'

    def __init__(self):
        super(FineTypeView, self).__init__(FineTypeView.FINE_TYPE_VIEW_NAME)


class RuleBasedFineTypeAnnotator(object):

    def __init__(self, sense_typer, mention_view=None):
        """

        :param sense_typer: Instance of SynsetFineTyper - converts a given offset_pos string outputs fine types.
        :param mention_view: View to be used for mentions. If not given uses inbuilt entity detection for mentions.
        """
        self.sense_typer = sense_typer
        self.mention_view = mention_view

    def __call__(self, doc):
        # doc should have NSD_VIEW
        if NSDView.NSD_VIEW_NAME not in doc.user_data:
            raise ValueError("%s view missing from doc.user_data" % NSDView.NSD_VIEW_NAME)
        if self.mention_view and self.mention_view not in doc.user_data:
            raise ValueError(self.mention_view + " view missing from doc.user_data")
        nsd_view = doc.user_data[NSDView.NSD_VIEW_NAME]
        fine_ent_view = FineTypeView()
        if self.mention_view:
            view = doc.user_data[self.mention_view]
            for mention_constituent in view.constituents:
                mention_span_tuple = (mention_constituent.start, mention_constituent.end)
                filtered_constituents = \
                    quotation_filter(doc, mention_span_tuple, distance_filter(doc, mention_span_tuple,
                                                                              nsd_view.constituents))
                # Currently set for high recall. So outputs all the fine types of all trigger words after filtering
                fine_types = set()
                for constituent in filtered_constituents:
                    sense_scores = constituent.label2score
                    # sense is same as synset_offset_pos
                    for offset_pos in sense_scores:
                        for fine_type in self.sense_typer.get_fine_types(offset_pos):
                            fine_types.add(fine_type)
                if len(fine_types) > 0:
                    fine_ent_view.add_constituent_from_args(mention_span_tuple[0], mention_span_tuple[1],
                                                            label2score={fine_type: 1. for fine_type in fine_types})
        else:
            for ent in doc.ents:
                ent_span_tuple = (ent.start, ent.end)
                filtered_constituents = quotation_filter(doc, ent_span_tuple,
                                                           distance_filter(doc, ent_span_tuple, nsd_view.constituents))
                # Currently set for high recall. So outputs all the fine types of all trigger words after filtering
                fine_types = set()
                for constituent in filtered_constituents:
                    sense_scores = constituent.label2score
                    # sense is same as synset_offset_pos
                    for offset_pos in sense_scores:
                        for fine_type in self.sense_typer.get_fine_types(offset_pos):
                            fine_types.add(fine_type)
                if len(fine_types) > 0:
                    fine_ent_view.add_constituent_from_args(ent.start, ent.end,
                                                            label2score={fine_type: 1. for fine_type in fine_types})

        doc.user_data[FineTypeView.FINE_TYPE_VIEW_NAME] = fine_ent_view


def get_nlp_with_fine_annotator(config, mention_view=None):
    sense_typer = SynsetFineTyper(config["figer_type_senses"])

    nsd_cache_path = config["nsd_cache_path"]
    embeddings_path = config["embeddings_path"]
    synset_offset_pos_embeddings_path = config["synset_offset_pos_embeddings_path"]

    nsd = None
    if os.path.isfile(nsd_cache_path):
        try:
            nsd = AverageEmbeddingNSD.load_instance_from_pickle(nsd_cache_path)
        except:
            print("Encountered error while loading pickle from " + nsd_cache_path)

    nsd = nsd if nsd else AverageEmbeddingNSD(embeddings_path, synset_offset_pos_embeddings_path)

    def create_pipeline(nlp):
        return [nlp.tagger, nlp.entity, nlp.parser, NounSenseAnnotator(nsd),
                RuleBasedFineTypeAnnotator(sense_typer, mention_view)]
    nlp = spacy.load('en', create_pipeline=create_pipeline)

    return nlp


if __name__ == '__main__':

    # use default config
    default_config = get_default_config()
    nlp = get_nlp_with_fine_annotator(default_config)

    doc = nlp(
        "Barack Hussein Obama II (US Listeni/bəˈrɑːk huːˈseɪn oʊˈbɑːmə/ bə-rahk hoo-sayn oh-bah-mə;[1][2] born August 4, 1961) is an American politician who served as the 44th President of the United States from 2009 to 2017. Obama is a member of the Democratic Party, and was the first African American and first person born outside the contiguous United States to serve as president.".decode(
            "utf-8"))
