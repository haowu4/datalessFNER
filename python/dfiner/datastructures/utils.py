from dfiner.datastructures import Constituent, View, Relation


def constituent_covers_index(constituent, index):
    return constituent.start <= index < constituent.end


def get_constituent_text(doc, constituent):
    txt = doc[constituent.start: constituent.end].text
    if constituent.name:
        txt = constituent.name + ":" + txt
    if constituent.label2score:
        txt += " (" + str(constituent.label2score) + ") "
    return txt


def print_view(doc, viewname):
    if viewname not in doc.user_data:
        print "%s not in doc" % viewname
        return
    for con in doc.user_data[viewname]:
        con_str = get_constituent_text(doc, con)
        rels = con.outgoing_relations
        if rels:
            rel_strs = ["%s -> %s" % (rel.relation_name, get_constituent_text(doc, rel.target)) for rel in rels]
            out_str = "%s -> [ %s ]" % (con_str, ", ".join(rel_strs))
        else:
            out_str = con_str
        print out_str


def get_available_view(doc):
    if doc.user_data and len(doc.user_data) > 0:
        return doc.user_data.keys()