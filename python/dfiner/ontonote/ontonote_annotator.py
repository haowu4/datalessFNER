import yaml
from dfiner.datastructures import View, Constituent


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
        raise NotImplementedError("Not implemented.")

    def __init__(self,
                 config,
                 mention_view="ner_mention"):
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
            d = self.classifier.predict(doc, start, end)
            c = Constituent(start, end, self.TYPE_NAME, label2score=d)
            new_view.add_constituent(c)
        doc.user_data[self.TYPE_NAME] = new_view

    def pick_fine_type(self, type_dist, coarse_type):
        pass


if __name__ == '__main__':
    pass
