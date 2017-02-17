from collections import defaultdict


class Lexicon(object):
    def __init__(self):
        self.lexeme_to_index = {}
        self.lexeme_counter = defaultdict(int)
        self.lexeme_counter_per_type = defaultdict(lambda: defaultdict(int))

    def see_lexeme(self, lexeme, t=None):
        self.lexeme_counter[lexeme] += 1
        if t:
            self.lexeme_counter_per_type[lexeme][t] += 1
        if lexeme not in self.lexeme_to_index:
            self.lexeme_to_index[lexeme] = len(self.lexeme_to_index)

    def prune(self, min_support):
        self.lexeme_to_index = {}
        for lexeme in self.lexeme_counter:
            if self.lexeme_counter[lexeme] > min_support:
                self.lexeme_to_index[lexeme] = len(self.lexeme_to_index)

    def getOrNegOne(self, lexeme):
        if lexeme in self.lexeme_to_index:
            return self.lexeme_to_index[lexeme]
        else:
            return -1

    def reverse_lex(self):
        ret = [None] * len(self.lexeme_to_index)
        for k in self.lexeme_to_index:
            idx = self.lexeme_to_index[k]
            ret[idx] = k
        return ret

    @property
    def size(self):
        return len(self.lexeme_to_index)
