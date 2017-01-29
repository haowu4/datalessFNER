import spacy
from dfiner.datastructures import Relation, View
from dfiner.annotators.annotator_helpers.hyp_pattern import HypPatterns


class HypView(View):
    HYP_VIEW_NAME = 'HypView'

    def __init__(self):
        super(HypView, self).__init__(HypView.HYP_VIEW_NAME)


class HypPatternAnnotator(object):

    HYP_VIEW = "hyp_view"

    def __init__(self, nlp):
        self.hyp_pattern_extractor = HypPatterns(nlp)

    def __call__(self, doc):
        hyp_view = HypView()
        for pattern_name, results in self.hyp_pattern_extractor.apply_all_patterns_on_doc(doc).iteritems():
            for source_index, target_indices in results:
                source_constituent = hyp_view.get_token_constituent_from_args_or_create(source_index)
                for target_index in target_indices:
                    target_constituent = hyp_view.get_token_constituent_from_args_or_create(target_index)
                    Relation.add_relation_between_constituents(
                        source_constituent, target_constituent, pattern_name)
        doc.user_data[self.HYP_VIEW] = hyp_view


if __name__ == '__main__':

    def create_pipeline(nlp):
        return [nlp.tagger, nlp.entity, nlp.parser, HypPatternAnnotator(nlp)]

    nlp = spacy.load('en', create_pipeline=create_pipeline)