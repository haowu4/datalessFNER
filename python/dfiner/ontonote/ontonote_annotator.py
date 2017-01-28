
class OntonoteAnnotator(object):

    TYPE_NAME = "Ontonote"

    def __init__(self,
                 model_file,
                 mention_view="ner_mention"):
        self.mention_view = mention_view

    def __call__(self, doc):
        pass

    def extract_features(self, doc):
        pass

    def load_model(self):
        pass