import os

from dfiner.annotators.annotator_helpers.sense_typer import SynsetFineTyper
from dfiner.annotators.nsd_annotator import AverageEmbeddingNSD, NounSenseAnnotator
from dfiner.annotators.fine_type_annotator import RuleBasedFineTypeAnnotator
from dfiner.annotators.hyp_pattern_annotator import HypPatternAnnotator


def get_non_default_annotator(nlp, config, ngram_length=5, mention_view=None):
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

    pipeline = [
        HypPatternAnnotator(nlp),
        NounSenseAnnotator(nsd, ngram_length),
        RuleBasedFineTypeAnnotator(sense_typer, mention_view)
    ]

    return pipeline


def get_nlp_with_all_annotators(nlp, config, ngram_length=5, mention_view=None):
    non_default_pipeline = get_non_default_annotator(nlp, config, ngram_length, mention_view)
    pipeline = [nlp.tagger, nlp.entity, nlp.parser] + non_default_pipeline

    nlp.pipeline = pipeline

    return nlp
