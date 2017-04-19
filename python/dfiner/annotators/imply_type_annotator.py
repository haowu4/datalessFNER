from dfiner.datastructures import View, Constituent
from dfiner.types.finer_type_system import FinerTypeSystem
from collections import defaultdict

class ImplicationTypeAnnotator(object):

    TYPE_NAME = "ImplicationType"

    @staticmethod
    def implys(type_name):
        return None

    def __init__(self,
                 config,
                 mention_views=["coarse_type", True]):
        self.baseview = mention_views
        self.config = config
        self.type_system = FinerTypeSystem.load_type_system(config)

    def __call__(self, doc):
        type_dict = defaultdict(set)
        for v, use_all_label in self.baseview:
            view = doc.user_data[v]
            for constituent in view.constituents:
                start = constituent.start
                end = constituent.end
                if use_all_label:
                    for t in constituent.label2score:
                        nt = ImplicationTypeAnnotator.implys(t)
                        if nt:
                            type_dict[(start, end)].append(nt)
                else:
                    t = constituent.best_label_name
                    nt = ImplicationTypeAnnotator.implys(t)
                    if nt:
                        type_dict[(start, end)].append(nt)

        new_view = View()
        for (start, end) in type_dict:
            label2score = {}
            for t in type_dict[(start, end)]:
                label2score[t] = 1.0
                c = Constituent(start,
                                end,
                                self.TYPE_NAME,
                                label2score=label2score)
            new_view.add_constituent(c)

        doc.user_data[self.TYPE_NAME] = new_view

    def pick_fine_type_or_none(self, type_dist, coarse_type):
        consistent_types = {}
        max_prob = 0.0
        recale = 0.0
        best_type = None
        for t in type_dist:
            if self.type_system.a_belongs_to_b(t, coarse_type):
                p = type_dist[t]
                recale += p
                if p > max_prob:
                    max_prob = p
                    best_type = t
                consistent_types[t] = p

        if len(consistent_types) == 0:
            return None

        if len(consistent_types) == 1:
            if max_prob > 0.4:
                return best_type
            else:
                return None

        sorted_entry = sorted(consistent_types.keys(),
                              key=lambda x: consistent_types[x],
                              reverse=True)

        second_best_key = sorted_entry[1]
        if (max_prob - consistent_types[second_best_key]) / recale > 0.8:
            return best_type


if __name__ == '__main__':
    pass
