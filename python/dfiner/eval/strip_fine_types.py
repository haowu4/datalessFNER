import sys
from dfiner.types.finer_type_system import FinerTypeSystem
from dfiner.utils import get_default_config


def strip_fine_type(label, tps):
    if label == "O":
        return label
    bio, label = label.split("-")
    labels = label.split(",")
    coarse_types = set()
    # print("-------------")
    for label in labels:
        label = label.replace("/", ".")[1:]
        if not tps.has_type(label):
            print >> sys.stderr, "%s is missing" % label
            return "O"
        else:
            label = tps.get_root(label)
        coarse_types.add("/%s" % label)
    # print("-------------")
    return ("%s-%s") % (bio, ",".join(sorted(list(coarse_types))))


def process(file, tps):
    with open(file) as input:
        for line in input:
            line = line.strip()
            if len(line) == 0:
                print("")
                continue
                # break
            line = line.split("\t")
            word, label = line[0], line[1]
            print("%s\t%s" % (word, strip_fine_type(label, tps)))


def main(tps):
    gold_file = sys.argv[1]
    process(gold_file, tps)


if __name__ == '__main__':
    config = get_default_config()
    tps = FinerTypeSystem.load_type_system(config)
    main(tps)
