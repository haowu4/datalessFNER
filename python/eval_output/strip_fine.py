import sys
import yaml




def strip_fine_type(label):
    if label == "O":
        return label
    bio, label = label.split("-")
    labels = label.split(",")
    coarse_types = set()
    for label in labels:
        label = label.split("/")[1]
        coarse_types.add("/%s" % label)
    return ("%s-%s") % (bio, ",".join(sorted(list(coarse_types))))


def process(file):
    with open(file) as input:
        for line in input:
            line = line.strip()
            if len(line) == 0:
                print("")
            line = line.split("\t")
            word, label = line[0], line[1]
            print("%s\t%s" % (word, strip_fine_type(label)))


def main():
    gold_file = sys.argv[1]
    process(gold_file)


if __name__ == '__main__':
    main()
