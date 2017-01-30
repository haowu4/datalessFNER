import codecs
import gzip
import json
from dfiner.datastructures import View, Constituent


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
                 type_system,
                 mention_view="corase_type"):
        # surface_totype maps (surface, corase type) => fine type to fine type.
        self.surface_totype_dist = load_surface_to_typedist(
            config["mention_to_type_dist"])
        self.coarse_view_name = mention_view
        self.config = config
        self.type_system = type_system

    def __call__(self, doc):
        new_view = View()
        view = doc.user_data[self.coarse_view_name]
        for constituent in view.constituents:
            start = constituent.start
            end = constituent.end
            coarse_type = constituent.best_label_name
            surface = doc[start:end].text
            try:
                type_dist = self.surface_totype[surface]
                fine_type_name = pick_fine_type(type_dist, coarse_type)
                Constituent(start, end, TYPE_NAME, fine_type_name)
            except KeyError:
                continue

        doc.user_data[TYPE_NAME] = new_view

    def pick_fine_type(self, type_dist, coarse_type):
        pass


if __name__ == '__main__':
    main()
