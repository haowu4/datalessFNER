from nltk.corpus import wordnet as wn
from dfiner.datastructures import View, Constituent
from dfiner.annotators.fine_type_annotator import SynsetFineTyper
from dfiner.utils.utils import best_k_label
from dfiner.types.finer_type_system import FinerTypeSystem


class MentionEntailmentAnnotator(object):
    TYPE_NAME = "MentionEntail"
    def __init__(self,
                 config,
                 trust_k=1,
                 mention_view ="OntonoteType"
                 ):
        self.typer = SynsetFineTyper(config)
        self.trust_k = trust_k
        self.type_system = FinerTypeSystem.load_type_system(config)
        self.mention_view = mention_view

    def __call__(self, doc):
        new_view = View()
        view = doc.user_data[self.mention_view]
        for constituent in view.constituents:
            start = constituent.start
            end = constituent.end
            types = set()
            for w in doc[start: end]:
                for x in wn.synsets(w.text):
                    if x.pos() == "n":
                        tps_w = self.typer.get_fine_types("%d_n" % x.offset())
                        for t in tps_w:
                            types.add(t)
            ls = set(best_k_label(constituent.label2score, self.trust_k))
            mx_label2score = {}

            for t in types:
                for coarse_type in ls:
                    try:
                        if self.type_system.a_belongs_to_b(t, coarse_type):
                            mx_label2score[t] = 1.0
                    except KeyError:
                        continue

            c = Constituent(start,
                            end,
                            self.TYPE_NAME,
                            label2score=mx_label2score)
            new_view.add_constituent(c)
        doc.user_data[self.TYPE_NAME] = new_view
