import sys


def gen_data():
    with open(sys.argv[1]) as input:
        sentences = []
        curr_sentence_tokens = []
        has_fine_type = False
        for line in input:
            line = line.strip()
            if len(line) == 0:
                if has_fine_type:
                    sentences.append(curr_sentence_tokens)
                curr_sentence_tokens = []
                continue
            tk, tp = line.split()
            curr_sentence_tokens.append(tk)
            if tp.startswith("B"):
                tp = tp.split("-")[1]
                if "," in tp:
                    has_fine_type = True
                # has_fine_type = True

        return sentences


def main():
    sentences = gen_data()
    for sent in sentences:
        print(" ".join(sent))


if __name__ == '__main__':
    main()
