

class KBBiasTypeAnnotator(object):

    TYPE_NAME = "KBBiasType"

    def __init__(self, mention_view="mention"):
        # surface_totype maps (surface, corase type) => fine type to fine type.
        self.surface_totype = {}

    def __call__(self, doc):
        pass


if __name__ == '__main__':
    main()