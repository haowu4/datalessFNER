import os
import json
import codecs

import spacy

from dfiner.annotators import get_nlp_with_all_annotators, get_non_default_annotator

from dfiner.datastructures import View
from dfiner.utils import get_default_config


class GoldMentionView(View):
    GOLD_MENTION_VIEW_NAME = "gold_mention_view"

    def __init__(self):
        super(GoldMentionView, self).__init__(GoldMentionView.GOLD_MENTION_VIEW_NAME)


def get_sentence_doc(nlp, tokens, labels):
    gold_mention_view = GoldMentionView()
    current_label = ""
    current_start = 0
    in_mention = False
    for i, (t, lab_str) in enumerate(zip(tokens, labels)):
        if lab_str.startswith("B"):
            if in_mention:
                gold_mention_view.add_constituent_from_args(current_start, i, current_label)
            current_start = i
            current_label = lab_str.split("-")[1]
            in_mention = True

        if lab_str == "O":
            if in_mention:
                gold_mention_view.add_constituent_from_args(current_start, i, current_label)
                in_mention = False

    if in_mention:
        gold_mention_view.add_constituent_from_args(current_start, len(labels), current_label)

    doc = nlp.tokenizer.tokens_from_list(tokens)
    doc.user_data[GoldMentionView.GOLD_MENTION_VIEW_NAME] = gold_mention_view

    return doc


def load_ontonotes(nlp, file, max_docs=None):
    tokens = []
    labels = []
    docs = []
    with codecs.open(file, "r", "utf-8") as input:
        for i, line in enumerate(input):
            if i < 1:
                continue
            line = line.strip()
            if len(line) == 0:
                # New sentence
                if len(tokens) == 0:
                    continue
                sent_doc = get_sentence_doc(nlp, tokens, labels)
                docs.append(sent_doc)
                tokens = []
                labels = []
                if len(docs) >= max_docs:
                    break
                continue
            line = line.split("\t")
            word, label = line[5], line[0]
            tokens.append(word)
            labels.append(label)

    if len(tokens) == 0:
        return docs

    sent_doc = get_sentence_doc(tokens, labels)
    docs.append(sent_doc)
    return docs


def load_all_data(nlp, base_folder):
    all_docs = []
    for f in os.listdir(base_folder):
        fn = os.path.join(base_folder, f)
        docs = load_ontonotes(nlp, fn)
        for doc in docs:
            doc.user_data['doc_id'] = f
            all_docs.append(doc)
    return all_docs


if __name__ == '__main__':
    config = get_default_config()
    nlp = spacy.load('en')
    nlp.pipeline = [nlp.tagger]
    non_default_annotators = \
        get_non_default_annotator(nlp, config, ngram_length=5, mention_view=GoldMentionView.GOLD_MENTION_VIEW_NAME)
    test_mentions = load_ontonotes(nlp, config["ontonotes_test_path"], max_docs=100)
    for doc in test_mentions:
        for annotator in non_default_annotators:
            annotator(doc)
