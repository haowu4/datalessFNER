from collections import defaultdict


def set_to_string(set_of_type):
    labels = ["/" + s.replace(".", "/") for s in set_of_type]
    return ",".join(sorted(labels))


def id(typs):
    return [x for source, x in typs]


def to_column_format(doc, use_views, type_map_function=id):
    ret = ""
    bios = defaultdict(lambda: "O")
    typs = defaultdict(set)
    for v, use_all in use_views:
        view = doc.user_data[v]
        for c in view.constituents:
            for i in range(c.start, c.end):
                if use_all and c.label2score:
                    for t in c.label2score:
                        typs[i].add((v, t))
                else:
                    # use best
                    if c.best_label_name:
                        typs[i].add((v, c.best_label_name))
                bios[i] = "I"
            bios[c.start] = "B"
    for i, token in enumerate(doc):
        w = token.text
        if bios[i] == "O":
            if len(typs[i]) == 0:
                inc = "%s\t%s\n" % (w, "O")
                ret += inc
            else:
                raise ValueError("O tag have types..")
        else:
            if len(typs[i]) > 0:
                types = type_map_function(typs[i])
                inc = "%s\t%s-%s\n" % (w, bios[i], set_to_string(types))
                ret += inc
            else:
                raise ValueError("B-I tag have no types..")
    return ret
