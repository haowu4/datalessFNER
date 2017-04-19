import codecs
import gzip
import json
from dfiner.datastructures import View, Constituent
from dfiner.types.finer_type_system import FinerTypeSystem
import pandas as pd


class KBBiasTypeAnnotator(object):

    TYPE_NAME = "KBBiasType"

    @staticmethod
    def load_surface_to_typedist(fname):
        ret = {}
        with gzip.open(fname, 'rb') as zf:
            reader = codecs.getreader("utf-8")
            contents = reader(zf)
            for line in contents:
                obj = json.loads(line)
                ret[obj['surface']] = obj["type_dist"]
        return ret

    def __init__(self,
                 config,
                 mention_view="coarse_type"):
        # surface_to_type_dist maps
        #       (surface, coarse type) => fine type to fine type.
        self.surface_to_type_dist = self.load_surface_to_typedist(
            config["mention_to_type_dist"])
        self.coarse_view_name = mention_view
        self.config = config
        self.type_system = FinerTypeSystem.load_type_system(config)
        # self.cities_names = set(pd.read_csv(config["common_us_city_path"], names=["Name", "State", "Pop"])["Name"].tolist())

    def __call__(self, doc):
        new_view = View()
        view = doc.user_data[self.coarse_view_name]
        for constituent in view.constituents:
            start = constituent.start
            end = constituent.end
            coarse_type = constituent.best_label_name
            surface = doc[start:end].text
            # if surface in self.cities_names:
            #         c = Constituent(start,
            #                         end,
            #                         self.TYPE_NAME,
            #                         label2score={"location.city": 1.0})
                    
                    # new_view.add_constituent(c)
            try:
                type_dist = self.surface_to_type_dist[surface]
                fine_type_name = self.pick_fine_type_or_none(type_dist,
                                                             coarse_type)
                if fine_type_name:
                    c = Constituent(start,
                                    end,
                                    self.TYPE_NAME,
                                    label2score={fine_type_name: 1.0})
                    new_view.add_constituent(c)
            except KeyError:
                continue

        doc.user_data[self.TYPE_NAME] = new_view

    def pick_fine_type_or_none(self, type_dist, coarse_type):
        consistent_types = {}
        max_prob = 0.0
        rescale = 0.0
        best_type = None
        for t in type_dist:
            if self.type_system.a_belongs_to_b(t, coarse_type):
                p = type_dist[t]
                rescale += p
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

        if (max_prob - consistent_types[second_best_key]) / rescale > 0.8:
            return best_type

        best_key = sorted_entry[1]
        if best_key == "organization.company":
            if consistent_types[second_best_key] > 0.35:
                return second_best_key

        if second_best_key == "organization.company":
            return best_key


if __name__ == '__main__':
    pass
