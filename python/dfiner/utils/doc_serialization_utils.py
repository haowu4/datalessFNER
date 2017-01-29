import codecs
import json
import hashlib
import cPickle as pickle
from spacy.tokens import Doc
from spacy.strings import hash_string


_DOC_BYTE_STRING = "doc_byte_string"
_USER_DATA_PICKLE_STRING = "user_data_pickle_string"


def get_key_value_for_doc(doc):
    doc_byte_string = doc.to_bytes()
    doc_user_data_string = "" if len(doc.user_data) == 0 else pickle.dumps(doc.user_data, pickle.HIGHEST_PROTOCOL)
    key = hash_string(doc.string)
    value = {_DOC_BYTE_STRING: doc_byte_string, _USER_DATA_PICKLE_STRING: doc_user_data_string}
    return key, value


def retreive_doc_from_key_value(nlp, key, value):
    doc_byte_string = value[_DOC_BYTE_STRING]
    doc_user_data_string = value[_USER_DATA_PICKLE_STRING]
    doc = Doc(nlp.vocab).from_bytes(doc_byte_string)
    assert hash_string(doc.string) == key, "the hash doesn't map the given key"
    user_data = pickle.loads(doc_user_data_string) if len(doc_user_data_string) > 0 else {}
    doc.user_data = user_data
    return doc


def docs_to_serialized_dict(docs, tolerate_errors=True):
    j = {}
    errors = 0
    for doc in docs:
        try:
            key, value = get_key_value_for_doc(doc)
            j[key] = value
        except Exception as e:
            errors += 1
            if not tolerate_errors:
                raise e
    print("encountered %d errors while serializing docs" % (errors))
    return j


def docs_to_json(docs, json_path, tolerate_errors=True):
    j = docs_to_serialized_dict(docs, tolerate_errors)
    with codecs.open(json_path, 'w', 'utf-8') as f_out:
        json.dump(j, f_out)


def docs_from_json(nlp, json_path, tolerate_errors=True):
    with codecs.open(json_path, 'r', 'utf-8') as f_in:
        j = json.load(f_in)
    docs = []
    errors = 0
    for k, v in j.iteritems():
        try:
            docs.append(retreive_doc_from_key_value(nlp, k, v))
        except Exception as e:
            errors += 1
            if not tolerate_errors:
                raise e
    print("encountered %d errors while loading docs" % (errors))
    return docs
