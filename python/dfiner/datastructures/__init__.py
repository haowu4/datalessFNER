# cog-comp style constituent with token offsets - [start, end)
class Constituent(object):
    __slots__ = ('start', 'end', 'name', 'score', 'label2score',
                 'best_label_name', 'outgoing_relations', 'incoming_relations')

    def __init__(self, start, end,
                 name=None,
                 score=None,
                 label2score=None,
                 outgoing_relations=None,
                 incoming_relations=None):
        self.start = start
        self.end = end
        self.name = name
        self.score = score
        self.label2score = label2score
        self.best_label_name = max(
            label2score.keys(), key=lambda x: label2score[x])
        self.outgoing_relations = None
        self.incoming_relations = None

    @staticmethod
    def hash(start, end, name):
        return start * 41 + end * 43 + (name.__hash__() * 53 if name else 0)

    def __hash__(self):
        return self.hash(self.start, self.end, self.name)

    def __eq__(self, other):
        return self.start == other.start and self.end == other.end and self.name == other.label

    def __ne__(self, other):
        return not self.__eq__(other)


class TokenConstituent(Constituent):
    __slots__ = []

    def __init__(self, index, name='', label2score=None):
        super(TokenConstituent, self).__init__(index, index + 1, name, label2score)


class Relation(object):
    __slots__ = 'source', 'target', 'relation_name', 'score', 'label2score'

    def __init__(self):
        raise NotImplementedError("Cannot instantiate a relation. Call ")

    def __hash__(self):
        return self.source.__hash__() * 41 + self.target.__hash__() * 43 + self.relation_name.__hash__() * 53

    @classmethod
    def add_relation_between_constituents(cls, source, target, relation_name, score=None, label2score=None):
        relation = cls.__new__(cls)
        relation.source = source
        relation.target = target
        relation.relation_name = relation_name
        relation.score = score
        relation.label2score = label2score
        if source.outgoing_relations is None:
            source.outgoing_relations = []
        if target.incoming_relations is None:
            target.incoming_relations = []
        # register relation to source
        source.outgoing_relations.append(relation)
        # register relation to target
        target.incoming_relations.append(relation)


class View(object):
    __slots__ = 'view_name', '_constituents_map'

    def __init__(self, view_name=''):
        self.view_name = view_name
        self._constituents_map = {}

    def add_constituent_from_args(self, start, end, name=None, score=None, label2score=None):
        hash = Constituent.hash(start, end, name)
        if hash not in self._constituents_map:
            self._constituents_map[hash] = Constituent(start, end, name, score, label2score)
        return hash

    def add_constituent(self, constituent):
        constituent_hash = constituent.__hash__()
        if constituent_hash not in self._constituents_map:
            self._constituents_map[constituent_hash] = constituent
        return constituent_hash

    def add_constituents(self, constituents):
        for constituent in constituents:
            self.add_constituent(constituent)
        return None

    def get_constituent_from_args_or_none(self, start, end, name=None, score=None, label2score=None):
        hash = Constituent.hash(start, end, name)
        return self._constituents_map.get(hash, None)

    def get_constituent_from_args_or_create(self, start, end, name=None, score=None, label2score=None):
        constituent_hash = self.add_constituent_from_args(start, end, name, score, label2score)
        return self._constituents_map[constituent_hash]

    def add_token_constituent_from_args(self, index, name=None, score=None, label2score=None):
        return self.add_constituent_from_args(index, index + 1, name, score, label2score)

    def add_token_constituent(self, token_constituent):
        return self.add_constituent(token_constituent)

    def add_token_constituents(self, token_constituents):
        return self.add_constituents(token_constituents)

    def get_token_constituent_from_args_or_create(self, index, name=None, score=None, label2score=None):
        constituent_hash = self.add_token_constituent_from_args(index, name, score, label2score)
        return self._constituents_map[constituent_hash]

    @property
    def constituents(self):
        return self._constituents_map.values()
