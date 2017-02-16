import sys
from collections import defaultdict
import json
import yaml
from pdb import set_trace as bp

class Label(object):
    def __init__(self, start, end, labels):
        self.start = start
        self.end = end
        self.labels = frozenset(labels)

    def match(self, other):
        if not self.start == other.start:
            return False

        if not self.end == other.end:
            return False

        if not self.labels == other.labels:
            return False

    def to_tuple(self, doc_id):
        return (doc_id, self.start, self.end, self.labels)


class Sentence(object):
    def __init__(self, tokens, entities):
        self.tokens = tokens
        self.entities = entities
        self.entities_map = defaultdict(set)
        for entity in entities:
            self.entities_map[(entity.start, entity.end)] = entity.labels

        self.readable_entities_map = defaultdict(list)
        for entity in entities:
            self.readable_entities_map["%d-%d" % (entity.start, entity.end)] = list(entity.labels)

def get_sentence(tokens, labels, ty_maps = None):
    entities = []
    current_labels = []
    current_start = 0
    in_mention = False
    for i, (t, lab_str) in enumerate(zip(tokens, labels)):
        if lab_str.startswith("B"):
            if in_mention:
                if len(current_labels) > 0:
                    entities.append(Label(current_start, i, current_labels))
                in_mention = False
            current_start = i
            current_labels = lab_str.split("-")[1].split(",")

            if ty_maps:
                mapped_labels = set()
                for l in current_labels:
                    if l in ty_maps:
                        mapped_labels.add(l)
                current_labels = list(mapped_labels)
            in_mention = True

        if lab_str == "O":
            if in_mention:
                entities.append(Label(current_start, i, current_labels))
                in_mention = False

    if in_mention:
        entities.append(Label(current_start, i, current_labels))
        in_mention = False

    return Sentence(tokens, entities)


def load_labels(file, ty_maps = None):
    tokens = []
    labels = []
    ss = []
    with open(file) as input:
        for line in input:
            line = line.strip()
            if len(line) == 0:
                # New sentence
                s = get_sentence(tokens, labels, ty_maps)
                ss.append(s)
                tokens = []
                labels = []
                continue
            line = line.split("\t")
            word, label = line[0], line[1]
            tokens.append(word)
            labels.append(label)

    if len(tokens) > 0:
        s = get_sentence(tokens, labels, ty_maps)
        ss.append(s)

    return ss


def analysis(gold_sentences, pred_sentences):
    a = defaultdict(int)
    b = defaultdict(list)
    for sent_id in range(len(gold_sentences)):
        predicted_sent = pred_sentences[sent_id]
        gold_sent = gold_sentences[sent_id]

        for e in predicted_sent.entities_map:
            te = gold_sent.entities_map[e]
            te_hat = predicted_sent.entities_map[e]

            te = ",".join(sorted(list(te)))
            te_hat = ",".join(sorted(list(te_hat)))
            a["%s---%s" % (te, te_hat)] += 1
            b["%s---%s" % (te, te_hat)].append({
                "tokens": gold_sent.tokens,
                "pred": predicted_sent.readable_entities_map,
                "gold": gold_sent.readable_entities_map
            })

    return a, b


def eval_strict(gold_sentences, pred_sentences):
    c = 0.0
    p_den = 0.0
    r_den = 0.0

    counter = 0

    for sent_id in range(len(gold_sentences)):
        # p_den += len(pred_sentences[sent_id].entities)
        # r_den += len(gold_sentences[sent_id].entities)
        predicted_sent = pred_sentences[sent_id]
        gold_sent = gold_sentences[sent_id]
        counter += len(predicted_sent.entities_map)
        # print(predicted_sent)
        # print(predicted_sent.entities_map)
        # bp()
        # if counter > 10:
        #     sys.exit(1)
        for e in predicted_sent.entities_map:
            te = gold_sent.entities_map[e]
            te_hat = predicted_sent.entities_map[e]
            intersect = te.intersection(te_hat)
            if len(intersect) == len(te_hat):
                if len(intersect) == len(te):
                    c += 1.0
            p_den += 1.0
            r_den += 1.0

    p = c / p_den
    r = c / r_den
    print(counter)
    print(c, p_den, r_den)
    return p, r, 2 * p * r / (p + r)


def eval_loose_macro(gold_sentences, pred_sentences):
    p_non = 0.0
    r_non = 0.0
    p_den = 0.0
    r_den = 0.0

    for sent_id in range(len(gold_sentences)):
        # p_den += len(pred_sentences[sent_id].entities)
        # r_den += len(gold_sentences[sent_id].entities)
        predicted_sent = pred_sentences[sent_id]
        gold_sent = gold_sentences[sent_id]

        for e in predicted_sent.entities_map:
            te = gold_sent.entities_map[e]
            te_hat = predicted_sent.entities_map[e]
            if len(te_hat) == 0:
                continue

            c = float(len(te.intersection(te_hat)))
            p_non += (c / len(te_hat))
            p_den += 1.0

        for e in gold_sent.entities_map:
            te = gold_sent.entities_map[e]
            te_hat = predicted_sent.entities_map[e]
            if len(te) == 0:
                continue

            c = float(len(te.intersection(te_hat)))
            r_non += (c / len(te))
            r_den += 1.0

    p = p_non / p_den
    r = r_non / r_den

    print(p_non, r_non, p_den, r_den)
    return p, r, 2 * p * r / (p + r)


def eval_loose_micro(gold_sentences, pred_sentences):
    p_non = 0.0
    r_non = 0.0
    p_den = 0.0
    r_den = 0.0

    for sent_id in range(len(gold_sentences)):
        # p_den += len(pred_sentences[sent_id].entities)
        # r_den += len(gold_sentences[sent_id].entities)
        predicted_sent = pred_sentences[sent_id]
        gold_sent = gold_sentences[sent_id]

        for e in predicted_sent.entities_map:
            te = gold_sent.entities_map[e]
            te_hat = predicted_sent.entities_map[e]
            c = float(len(te.intersection(te_hat)))
            p_non += c
            p_den += float(len(te_hat))

        for e in gold_sent.entities_map:
            te = gold_sent.entities_map[e]
            te_hat = predicted_sent.entities_map[e]
            c = float(len(te.intersection(te_hat)))
            r_non += c
            r_den += float(len(te))

    p = p_non / p_den
    r = r_non / r_den
    print(p_non, r_non, p_den, r_den)
    return p, r, 2 * p * r / (p + r)


def eval(a, b):
    p, r, f = eval_strict(a, b)
    print("Strict F1 :")
    print("P: %.3f\t R: %.3f\t F1: %.3f" % (p, r, f))
    print("\n\n")

    p, r, f = eval_loose_micro(a, b)
    print("Losse Mirco :")
    print("P: %.3f\t R: %.3f\t F1: %.3f" % (p, r, f))
    print("\n\n")

    p, r, f = eval_loose_macro(a, b)
    print("Losse Marco F1 :")
    print("P: %.3f\t R: %.3f\t F1: %.3f" % (p, r, f))

    x, y = analysis(a, b)

    with open("/tmp/count.json", "w") as output:
        json.dump(x, output)

    with open("/tmp/example.json", "w") as output:
        json.dump(y, output)


def eval_two_file(gold_file, pred_file):

    gold_labels_sents = load_labels(gold_file)
    pred_labels_sents = load_labels(pred_file)

    # figer_labels_set = set()
    # mine_labels_set = set()
    # for sent in gold_labels_sents:
    #     for e in sent.entities:
    #         for k in e.labels:
    #             figer_labels_set.add(k)

    # for sent in pred_labels_sents:
    #     for e in sent.entities:
    #         for k in e.labels:
    #             mine_labels_set.add(k)

    eval(gold_labels_sents, pred_labels_sents)


def main():
    gold_file = sys.argv[1]
    pred_file = sys.argv[2]
    eval_two_file(gold_file, pred_file)

    # print(" Unique in Figer :")
    # for x in figer_labels_set.difference(mine_labels_set):
    #     print("\t", x)

    # print(" Unique in Mine :")
    # for x in mine_labels_set.difference(figer_labels_set):
    #     print("\t", x)


if __name__ == '__main__':
    main()
