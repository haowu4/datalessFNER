import yaml
from dfiner.datastructures import View, Constituent
from dfiner.ontonote.features import get_default_feature
from dfiner.ontonote.features import get_default_dense_feature
from dfiner.utils.utils import load_pickle
from sklearn.externals import joblib
from dfiner.ontonote.mention_classifier import MentionClassifier


class OntonoteTypeAnnotator(object):
    TYPE_NAME = "OntonoteType"

    @staticmethod
    def load_yaml(config):
        file = config["ontonote_to_figer_map"]
        ret = None
        with open(file) as input:
            ret = yaml.load(input.read())
        return ret

    @staticmethod
    def load_classifier(config):

        w2v_dict = load_pickle(config["w2v_dict"])
        w2v_mean = load_pickle(config["w2v_mean"])

        lex = load_pickle(config["ontonote-lex"])
        type_lex = load_pickle(config["ontonote-lex-type"])
        model = joblib.load(config["ontonote-model"])

        return MentionClassifier(model,
                                 get_default_feature(),
                                 get_default_dense_feature(w2v_dict, w2v_mean),
                                 lex, type_lex
                                 )

    def __init__(self,
                 config,
                 mention_view="gold_mention_view"):
        # surface_totype maps (surface, corase type) => fine type to fine type.
        self.surface_totype_dist = self.load_yaml(config)
        self.classifier = self.load_classifier(config)
        self.config = config
        self.mention_view = mention_view

    def __call__(self, doc):
        new_view = View()
        view = doc.user_data[self.mention_view]
        for constituent in view.constituents:
            start = constituent.start
            end = constituent.end
            label = self.classifier.classify(doc, start, end)
            try:
                label = self.surface_totype_dist[label]
            except KeyError:
                continue
            c = Constituent(start,
                            end,
                            self.TYPE_NAME,
                            label2score={label: 1.0})
            new_view.add_constituent(c)
        doc.user_data[self.TYPE_NAME] = new_view
