import sys

def coarse_type(t):
    if "/" in t[1:]:
        return "/%s" % t[1:].split("/")[0]
    else:
        return t

with open(sys.argv[1]) as input:
    for line in input:
        line = line.strip()
        if len(line) == 0:
            print("")
            continue

        line_parts = line.split("\t")
        word = line_parts[0]
        tag = line_parts[1]
        if tag == "O":
            print(line)
            continue

        bio, alltype = tag.split("-")
        new_types = set()
        for t in alltype.split(","):
            new_types.add(t)
            new_types.add(coarse_type(t))

        print("%s\t%s-%s" % (word, bio, ",".join(new_types)))
