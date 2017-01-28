import spacy
from dfiner.annotators.annotator_helpers.hyp_pattern import HypPatterns


class HypPatternAnnotator(object):

    HYP_VIEW = "hyp_view"

    def __init__(self, nlp):
        self.hyp_pattern_extractor = HypPatterns(nlp)

    def __call__(self, doc):
        doc.user_data[self.HYP_VIEW] = self.hyp_pattern_extractor.apply_all_patterns_on_doc(doc)


if __name__ == '__main__':

    def create_pipeline(nlp):
        return [nlp.tagger, nlp.entity, nlp.parser, HypPatternAnnotator(nlp)]

    nlp = spacy.load('en', create_pipeline=create_pipeline)