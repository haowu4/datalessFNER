from dfiner.utils.union_find import UnionFind
from spacy import symbols


class Node(object):

    __slots__ = ('lemma', 'pos', 'tag', 'strings')

    def __init__(self, lemma, pos, tag, strings=None):
        self.lemma = lemma
        self.pos = pos
        self.tag = tag
        # strings object
        self.strings = strings

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.strings:
            return "%s, %s, %s" % (self.strings[self.lemma], self.strings[self.pos], self.strings[self.tag])
        else:
            return "%s, %s, %s" % (self.lemma, self.pos, self.tag)


class Direction:
    IN, OUT = 0, 1
    names = {IN: "in", OUT: "out"}


class Step(object):

    __slots__ = ('targets', 'dep', 'dirn', 'acc', 'cons', 'cons_and', 'strings')

    def __init__(self, targets, dep, dirn, acc, cons, cons_and=True, strings=None):
        self.targets = targets
        self.dep = dep
        self.dirn = dirn
        self.acc = acc
        self.cons = cons
        self.cons_and = cons_and
        self.strings = strings

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        targets_str = str(self.targets)
        dep_str = self.strings[self.dep] if self.strings else str(self.dep)
        dirn_str = Direction.names[self.dirn]
        return "%s, %s, %s" % (targets_str, dep_str, dirn_str)


# check only if val1 is set
def check_match(val1, val2):
    if val1:
        return val1 == val2
    else:
        return True


def validate_match(target, match):
    if target:
        is_valid = check_match(target.lemma, match.lemma) \
                   and check_match(target.pos, match.pos) \
                   and check_match(target.tag, match.tag)
        return is_valid
    return True


def execute(path_iter, tokens):
    try:
        step = path_iter.next()
        matches = []
        cons_func = all if step.cons_and else any
        # print tokens, step.cons_and, cons_func
        if step.dirn is None:
            for token in tokens:
                if step.cons is None \
                        or cons_func([len(execute(iter(con_path), [token])) > 0
                                      for con_path in step.cons]):
                    matches.append(token)
        else:
            for token in tokens:
                if step.dirn == Direction.IN:
                    if not check_match(step.dep, token.dep):
                        continue
                    if step.cons is None \
                            or cons_func([len(execute(iter(con_path), [token])) > 0
                                          for con_path in step.cons]):
                        if (not step.targets) \
                                or any(validate_match(target, token.head)
                                       for target in step.targets):
                            matches.append(token.head)
                elif step.dirn == Direction.OUT:
                    for child in token.children:
                        if not check_match(step.dep, child.dep):
                            continue
                        if step.cons is None \
                                or cons_func([len(execute(iter(con_path), [token])) > 0
                                              for con_path in step.cons]):
                            if (not step.targets) \
                                    or any(validate_match(target, child)
                                           for target in step.targets):
                                matches.append(child)
                            if not step.acc:
                                break
                else:
                    raise ValueError("dir variable set to invalid value : %s" % step.dirn)
        return execute(path_iter, matches) if len(matches) > 0 else []
    except StopIteration:
        return tokens


def is_noun(token):
    return token.pos == symbols.NOUN or token.pos == symbols.PROPN


def get_conjs(token, only_noun=False):
    doc = token.doc
    uf = UnionFind(len(doc))
    for t in doc:
        if t.dep == symbols.conj:
            uf.union(t.i, t.head.i)

    def is_conj(t):
        return t != token and uf.find(t.i, token.i) and \
               ((not only_noun) or is_noun(t))

    return filter(is_conj, doc)


class HypPatterns(object):

    _noun_targets = [Node(None, symbols.PROPN, None), Node(None, symbols.NOUN, None)]
    _verb_targets = [Node(None, symbols.VERB, None)]

    def __init__(self, nlp):
        self.strings = nlp.vocab.strings
        self._patterns = {}
        self.init_patterns()

    def add_prep_of_to_path(self, path, pre=True):
        path = list(path)
        if pre:
            path.insert(0, Step(self._noun_targets, symbols.prep, Direction.IN, True, None))
            path.insert(0, Step([Node(self.strings["of"], None, self.strings["IN"])],
                                symbols.pobj, Direction.IN, True, None))
        else:
            path.append(Step([Node(self.strings["of"], None, self.strings["IN"])],
                             symbols.prep, Direction.OUT, True, None))
            path.append(Step(self._noun_targets, symbols.pobj, Direction.OUT, True, None))

        return path

    def init_patterns(self):

        # hearst1
        # {Presidents} such as [Obama] and [Bush]
        path = list()
        path.append(Step([Node(self.strings["as"], None, self.strings["IN"])],
                         symbols.prep, Direction.OUT, True, None))
        constraints = [ [Step([Node(self.strings["such"], None, self.strings["JJ"])],
                              symbols.amod, Direction.OUT, True, None)] ]
        path.append(Step(self._noun_targets, symbols.pobj, Direction.OUT, True, constraints))

        self._patterns["hearst1"] = path
        self._patterns["hearst1_of"] = self.add_prep_of_to_path(path)

        # hearst2
        # {Presidents} like [Obama] (and) [Bush]
        path = list()
        path.append(Step([Node(self.strings["like"], None, self.strings["IN"])],
                         symbols.prep, Direction.OUT, True, None))
        path.append(Step(self._noun_targets, symbols.pobj, Direction.OUT, True, None))

        self._patterns["hearst2"] = path
        self._patterns["hearst2_of"] = self.add_prep_of_to_path(path)

        # hearst3
        # Obama (and) other {presidents}
        path = list()
        constraints = [ [Step([Node(self.strings["other"], None, self.strings["JJ"])],
                              symbols.amod, Direction.OUT, True, None)] ]
        path.append(Step(None, Node, None, True, constraints))
        path.append(Step(self._noun_targets, symbols.conj, Direction.IN, True, None))
        self._patterns["hearst3"] = path

        # hearst4
        # {Presidents} including [Obama] (and) [Bush]
        #
        # negative ex:
        # The agency's thirty day intensive inspection found several serious deficiencies in
        # (Valujet operations) including The airline's (failure) to
        # establish the air worthiness of some of its aircraft.
        #
        # can't handle above one now.
        #
        path = list()
        path.append(Step([Node(self.strings["include"], symbols.VERB, None)],
                         symbols.prep, Direction.OUT, True, None))
        path.append(Step(self._noun_targets, symbols.pobj, Direction.OUT, True, None))

        self._patterns["hearst4"] = path
        self._patterns["hearst4_of"] = self.add_prep_of_to_path(path)

        # hearst4 verb
        # An FBI list of 22 "most wanted {terrorists}"
        # includes a Sheikh Ahmed Salim [Swedan] and adds
        # various aliases, including "Ahmed the Tall."
        path = list()
        path.append(Step([Node(self.strings["include"], symbols.VERB, None)],
                         symbols.nsubj, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.dobj, Direction.OUT, True, None))

        self._patterns["hearst4_verb"] = path
        self._patterns["hearst4_verb_of"] = self.add_prep_of_to_path(path)

        # hearst4 through verb
        # The fresh battles came hours after LTTE gunmen stormed a police post
        # in government-controlled Mannar Island off the northwestern coast,
        # killing at least nine policemen, including an officer,
        # and wounding 10 others, police said."
        path = list()
        path.append(Step(self._verb_targets,
                         symbols.dobj, Direction.IN, True, None))
        path.append(Step([Node(self.strings["include"], symbols.VERB, None)],
                         symbols.prep, Direction.OUT, True, None))
        path.append(Step(self._noun_targets, symbols.pobj, Direction.OUT, True, None))

        self._patterns["hearst4_thr_verb"] = path

        # hearst 5
        # Obama, like all presidents, works at the White house
        path = list()
        constraints = [[
                           Step([Node(self.strings[lemma], None, None)],
                                None, Direction.OUT, False, None)
                       ] for lemma in ["all", "every", "any", "each"]]
        constraints += [[
            Step([Node(self.strings["other"], None, None)],
                 None, Direction.OUT, False, None)
        ]]
        path.append(Step([Node(self.strings["like"], None, self.strings["IN"]),
                          Node(self.strings["unlike"], None, self.strings["IN"])],
                         symbols.pobj, Direction.IN, True, constraints, False))
        path.append(Step(self._verb_targets,
                         symbols.prep, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.nsubj, Direction.OUT, True, None))
        self._patterns["hearst5"] = path

        # hearst copular
        # [Obama] is the {president}
        path = list()
        path.append(Step([Node(self.strings["be"], symbols.VERB, None)],
                         symbols.attr, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.nsubj, Direction.OUT, True, None))
        self._patterns["hearst_copular"] = path

        # hearst reverse copular
        # The {president} is Obama.
        path = list()
        path.append(Step([Node(self.strings["be"], symbols.VERB, None)],
                         symbols.nsubj, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.attr, Direction.OUT, True, None))
        self._patterns["hearst_rev_copular"] = path

        # hearst appos
        # [Obama], the US {president}, was born in Hawai
        path = list()
        path.append(Step(self._noun_targets, symbols.appos, Direction.IN, True, None))
        self._patterns["hearst_appos"] = path

        # hearst noun compound modifier
        # Today's talk was given Republican {Senator} John [McCain].
        path = list()
        path.append(Step(self._noun_targets, self.strings["compound"], Direction.IN, False, None))
        self._patterns["hearst_ncompmod"] = path

        # hearst among
        # Joe [Biden] among other vice {presidents}.
        path = list()
        path.append(Step([Node(self.strings["among"], None, self.strings["IN"])],
                         symbols.pobj, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.prep, Direction.IN, True, None))
        self._patterns["hearst_among"] = path

        # hearst among through verb
        # Clinton counts Joe [Biden] among other vice {presidents}.
        path = list()
        path.append(Step([Node(self.strings["among"], None, self.strings["IN"])],
                         symbols.pobj, Direction.IN, True, None))
        path.append(Step(self._verb_targets, symbols.prep, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.dobj, Direction.OUT, True, None))
        self._patterns["hearst_among_thr_verb"] = path

        # hearst enough
        # [Messi] is enough of a {player}.
        path = list()
        path.append(Step([Node(self.strings["of"], None, self.strings["IN"])],
                         symbols.pobj, Direction.IN, True, None))
        path.append(Step([Node(self.strings["enough"], None, self.strings["JJ"])],
                         symbols.prep, Direction.IN, True, None))
        path.append(Step(self._verb_targets, symbols.acomp, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.nsubj, Direction.OUT, True, None))
        self._patterns["hearst_enough"] = path

        # hearst as
        # [Obama] as a {senator}.
        path = list()
        constraints = [[Step([Node(None, symbols.DET, None)],
                             symbols.det, Direction.OUT, False, None)]]
        path.append(Step([Node(self.strings["as"], None, self.strings["IN"])],
                         symbols.pobj, Direction.IN, True, constraints))
        path.append(Step(self._noun_targets, symbols.prep, Direction.IN, True, None))
        self._patterns["hearst_as"] = path

        # hearst as with prep_of attachment
        # The emergence of [USA] as a global {superpower} concided with the rise of USSR.
        # use previous path
        # WRONG
        self._patterns["hearst_as_of"] = self.add_prep_of_to_path(self._patterns["hearst_as"], pre=False)

        # hearst as verb
        # [Michelle] was working as a {model}.
        path = list()
        path.append(Step([Node(self.strings["as"], None, self.strings["IN"])],
                         symbols.pobj, Direction.IN, True, None))
        path.append(Step(self._verb_targets, symbols.prep, Direction.IN, True, None))
        path.append(Step(self._noun_targets, symbols.nsubj, Direction.OUT, True, None))
        self._patterns["hearst_as_verb"] = path

        # custom patterns
        # Today's talk was given {Republican} Senator John [McCain].
        path = list()
        path.append(Step(self._noun_targets, symbols.amod, Direction.IN, False, None))
        path.append(Step(self._noun_targets, self.strings["compound"], Direction.IN, False, None))
        self._patterns["custom_amod_ncompmod"] = path

    def apply_pattern_on_token(self, pattern_name, token, add_conjs=True, detect_conjs=True):
        assert pattern_name in self._patterns, "given pattern name - %s missing from the existing patterns" % pattern_name
        try:
            tokens = [token]
            if detect_conjs:
                tokens += get_conjs(token)
            matches = filter(lambda match: match != token, execute(iter(self._patterns[pattern_name]), tokens))
            conjs = []
            if add_conjs:
                conjs = \
                    [conj for match in matches
                     for conj in get_conjs(match, only_noun=True)
                     if conj != match and conj != token]
            return matches + conjs
        except:
            print "got error while executing the pattern : %s" % pattern_name

    def apply_pattern_on_doc(self, pattern_name, doc, add_conjs=True):
        assert pattern_name in self._patterns, "given pattern name - %s missing from the existing patterns" % pattern_name
        results = []
        for token in doc:
            matches = self.apply_pattern_on_token(pattern_name, token, add_conjs)
            if len(matches) > 0:
                results.append((token, matches))

        return results

    def apply_all_patterns_on_doc(self, doc, add_conjs=True):
        pattern_results = {}
        for pattern_name in self._patterns.keys():
            results = self.apply_pattern_on_doc(pattern_name, doc, add_conjs)
            if len(results) > 0:
                pattern_results[pattern_name] = results

        return pattern_results


if __name__ == '__main__':

    strings = ["The AAAS is the largest scientific society "
               "in the world and publishes journals such as "
               "Science , and Science Translational Medicine.",

               "Presidents such as Obama and Bush",

               "Agar is a substance prepared from a mixture of "
               "red algae, such as Gelidium, for laboratory or industrial use.",

               "Presidents like Obama and Bush",

               "Combinations of elements like Iron and Oxygen produces compounds",

               "Bush, Obama and other presidents",

               "Presidents including Bush and Obama were present at the ceremony",

               "The fresh battles came hours after LTTE gunmen "
               "stormed a police post in government-controlled "
               "Mannar Island off the northwestern coast, "
               "killing at least nine policemen, including an officer, "
               "and wounding 10 others, police said.",

               "Presidents include Bush and Obama",

               "An FBI list of 22 \"most wanted terrorists\" "
               "includes a Sheikh Ahmed Salim Swedan and adds "
               "various aliases, including \"Ahmed the Tall.\"",

               "Obama, the president, was born in Hawaii.",

               "Obama is the president.",

               "The president is Mr. Obama."
               ]

    hearst_funcs = ['hearst1', 'hearst1', 'hearst1_of',
                    'hearst2', 'hearst2_of',
                    'hearst3',
                    'hearst4', 'hearst4_thr_verb', 'hearst4_verb', 'hearst4_verb_of',
                    'hearst_appos',
                    'hearst_copular', 'hearst_rev_copular']

    # nlp = spacy.load('en')
    # hyp_patterns = HypPatterns(nlp)
    #
    # def print_example(hearst_pattern_name, string):
    #     doc = nlp(string.decode('utf-8'))
    #     print string
    #     for (token, matches) in hyp_patterns.apply_pattern_on_doc(hearst_pattern_name, doc, add_conjs=True):
    #         print "%d: %s <= %s" % (token.i, token, matches)
    #
    # print "\n" * 3
    # for string, hearst_pattern_name in zip(strings, hearst_funcs):
    #     print_example(hearst_pattern_name, string)
    #     print ""
