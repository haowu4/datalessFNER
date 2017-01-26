import codecs
import json

import config
import spacy
from fine_type_annotator import get_nlp_with_fine_annotator
from hyp_pattern import HypPatterns

GOLD_MENTION_VIEW = "gold_mention_view"


def load_figer_data(data_path, nlp):
    with codecs.open(data_path, 'r', 'utf-8') as f_in:
        data = map(json.loads, map(unicode.strip, f_in.readlines()))

    docs = [nlp.tokenizer.tokens_from_list(datum[u"tokens"]) for datum in data]
    for doc, datum in zip(docs, data):
        doc.user_data[GOLD_MENTION_VIEW] = []
        for mention in datum[u"mentions"]:
            doc.user_data[GOLD_MENTION_VIEW].append(((mention[u"start"], mention[u"end"]), set(mention[u"labels"])))

    for annotator in nlp.pipeline:
        _ = [annotator(doc) for doc in docs]

    return docs


if __name__ == '__main__':

    # nlp = get_nlp_with_fine_annotator(use_view=GOLD_MENTION_VIEW)
    nlp = spacy.load('en')
    figer_docs = load_figer_data(config.figer_test_json, nlp)
    hyp_patterns = HypPatterns(nlp)


    def print_example(doc):
        print doc
        for (pattern_name, results) in hyp_patterns.apply_all_patterns_on_doc(doc, add_conjs=True).iteritems():
            print ""
            print pattern_name + " :"
            for token, matches in results:
                print "  %d: %s <= %s" % (token.i, token, matches)
        print "="*80

    for doc in figer_docs:
        print_example(doc)
        print ""

