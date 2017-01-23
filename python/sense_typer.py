# -*- coding: utf-8 -*-

import codecs

import config
from nltk.corpus import wordnet as wn
from utils import syn_from_offset_pos


class SynsetFineTyper(object):

    def __init__(self, fine_type_to_synset_path):
        """

        :param fine_type_to_synset_path: Path to fine type to synset map
            Assumes the following convention for each line -

                 <fine_type>\t<synset_id_1> <synset_id_2> ... <synset_id_n>\n
            Ex:  person.politician	politician.n.01	politician.n.02	head_of_state.n.01	-sovereign.n.01

            synset_ids follow nltk convention and '-' sign indicates to exclude hyponym subtree rooted
            at that node.
        """
        self.entity_synset = wn.synset("entity.n.01")
        self.synset_to_type_positive, self.synset_to_type_negative = \
            self._read_synset_to_type(fine_type_to_synset_path)
        # we will do lazy population of synset_offset_pos_to_types
        self.synset_offset_pos_to_types = {}

    def get_fine_types(self, synset_offset_pos):
        """

        :param synset_offset_pos: input of the form "<offset>_<pos>" uniquely identifying a synset
        :return: returns any types whose nodes fall in the path from the synset to the root
        """
        offset, pos = synset_offset_pos.split("_")
        if pos != wn.NOUN:
            return set()
        if synset_offset_pos in self.synset_offset_pos_to_types:
            return self.synset_offset_pos_to_types[synset_offset_pos]
        synset = syn_from_offset_pos(offset, pos)
        queue = [synset]
        positive_fine_types = set()
        negative_fine_types = set()
        while len(queue) > 0:
            cur_synset = queue.pop(0)
            if cur_synset in self.synset_to_type_positive:
                positive_fine_types.add(self.synset_to_type_positive[cur_synset])
            if cur_synset in self.synset_to_type_negative:
                negative_fine_types.add(self.synset_to_type_negative[cur_synset])
            queue.extend(cur_synset.hypernyms())
        fine_types = positive_fine_types.difference(negative_fine_types)
        self.synset_offset_pos_to_types[synset_offset_pos] = fine_types
        return fine_types

    def _read_synset_to_type(self, fine_type_to_synsets_file):
        synset_to_type_positive = {}
        synset_to_type_negative = {}
        with codecs.open(fine_type_to_synsets_file, mode='r', encoding='utf-8') as f_in:
            for line in f_in:
                tokens = line.strip().split("\t")
                fine_type = tokens[0]
                for synset_id in tokens[1:]:
                    if synset_id.startswith("-"):
                        synset = wn.synset(synset_id[1:])
                        assert synset not in synset_to_type_negative
                        synset_to_type_negative[synset] = fine_type
                    else:
                        synset = wn.synset(synset_id)
                        assert synset not in synset_to_type_positive
                        synset_to_type_positive[synset] = fine_type
        return synset_to_type_positive, synset_to_type_negative


if __name__ == '__main__':
    # unit test

    finetyper = SynsetFineTyper(config.fine_type_to_synset_file)