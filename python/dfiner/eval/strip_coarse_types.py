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
            # return "O"
            if label == "people":
                continue
            coarse_types.add("/%s" % label)
        else:
            root_label = tps.get_root(label)
            if label == root_label:
                continue
        coarse_types.add("/%s" % label)
    # print("-------------")
    if len(coarse_types) == 0:
        return "O"
    return ("%s-%s") % (bio, ",".join(sorted(list(coarse_types))))


def process(file, tps):
    ret = []
    with open(file) as input:
        for line in input:
            line = line.strip()
            if len(line) == 0:
                ret.append("")
                continue
                # break
            line = line.split("\t")
            word, label = line[0], line[1]
            ret.append("%s\t%s" % (word, strip_fine_type(label, tps)))
    return ret

def main(tps):
    gold_file = sys.argv[1]
    return process(gold_file, tps)


if __name__ == '__main__':
    config = get_default_config()
    tps = FinerTypeSystem.load_type_system(config)
    print "\n".join(main(tps))
