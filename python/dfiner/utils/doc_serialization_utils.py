import codecs
import json
import hashlib
import cPickle as pickle
from spacy.tokens import Doc
from spacy.strings import hash_string


_DOC_BYTE_STRING = "doc_byte_string"
_USER_DATA = "user_data"
_HASH = "doc_hash"


def serialize_doc(doc):
    doc_byte_string = doc.to_bytes()
    # doc_user_data_string = "" if len(doc.user_data) == 0 else pickle.dumps(doc.user_data, pickle.HIGHEST_PROTOCOL)
    value = {_DOC_BYTE_STRING: str(doc_byte_string),
             _USER_DATA: doc.user_data,
             _HASH: str(hash_string(doc.string))}
    return pickle.dumps(value, pickle.HIGHEST_PROTOCOL).encode('base64')


def unserialize_doc(nlp, serialized_string):
    value = pickle.loads(serialized_string.decode('base64'))
    doc_byte_string = value[_DOC_BYTE_STRING]
    user_data = value[_USER_DATA]
    doc_hash = value[_HASH]
    doc = Doc(nlp.vocab).from_bytes(doc_byte_string)
    assert str(hash_string(doc.string)) == doc_hash, "the hash doesn't match the hash"
    doc.user_data = user_data
    return doc


def serialize_docs(docs, tolerate_errors=True):
    serialized_strings = []
    errors = 0
    for doc in docs:
        try:
            serialized_string = serialize_doc(doc)
            serialized_strings.append(serialized_string)
        except Exception as e:
            errors += 1
            if not tolerate_errors:
                raise e
    print("encountered %d errors while serializing docs" % (errors))
    return serialized_strings


def serialize_docs_to_file(docs, serialization_path, tolerate_errors=True):
    serialized_strings = serialize_docs(docs, tolerate_errors)
    with codecs.open(serialization_path, 'w') as f_out:
        json.dump(serialized_strings, f_out)


def unserialize_docs_from_file(nlp, serialization_path, tolerate_errors=True):
    docs = []
    errors = 0
    with codecs.open(serialization_path, 'r') as f_in:
        strings = json.load(f_in)
        for string in strings:
            try:
                docs.append(unserialize_doc(nlp, string))
            except Exception as e:
                errors += 1
                if not tolerate_errors:
                    raise e
    print("encountered %d errors while loading docs" % (errors))
    return docs
