from collections import defaultdict
import cPickle as pickle

from dfiner.utils import reverse_dict


class Lexicon(object):
    def __init__(self, d=None):
        if d is None:
            self._lexeme_to_index = {}
            self._lexeme_counter = defaultdict(int)
            self._index_to_lexeme = {}
        else:
            self._lexeme_to_index = d['lexeme_to_index']
            self._lexeme_counter = d['lexeme_counter']
            self._index_to_lexeme = reverse_dict(self._lexeme_to_index)
        self._allow_new_lexemes = True

    @property
    def allow_new_lexemes(self):
        return self._allow_new_lexemes

    @allow_new_lexemes.setter
    def allow_new_lexemes(self, value):
        assert isinstance(value, bool)
        self._allow_new_lexemes = value

    def prune(self, min_support):
        self._lexeme_to_index = {}
        for lexeme in self._lexeme_counter:
            if self._lexeme_counter[lexeme] >= min_support:
                self._lexeme_to_index[lexeme] = len(self._lexeme_to_index)
        self._index_to_lexeme = reverse_dict(self._lexeme_to_index)
        self.allow_new_lexemes = False

    def __getitem__(self, item):
        if isinstance(item, str) or isinstance(item, unicode):
            lexeme = item
            if self.allow_new_lexemes:
                if lexeme not in self._lexeme_to_index:
                    self._lexeme_to_index[lexeme] = lexeme_index = len(self._lexeme_to_index)
                    self._index_to_lexeme[lexeme_index] = lexeme
            return self._lexeme_to_index.get(lexeme, -1)
        elif isinstance(item, int):
            return self._index_to_lexeme.get(item, None)
        else:
            raise ValueError("unknown key passed to __getitem__ = %s" % item)

    @property
    def size(self):
        return len(self._lexeme_to_index)

    def _get_save_dict(self):
        return {
            'lexeme_to_index': self._lexeme_to_index,
            'lexeme_counter': self._lexeme_counter
        }

    def save_lexicon(self, save_path):
        with open(save_path, 'wb') as f_out:
            pickle.dump(self._get_save_dict(), f_out, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load_from_path(cls, load_path):
        with open(load_path, 'rb') as f_in:
            d = pickle.load(f_in)

        lexicon = cls(d)
        return lexicon
