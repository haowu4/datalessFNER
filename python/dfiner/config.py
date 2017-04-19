from dfiner.annotators.fine_type_annotator import FineTypeView
from dfiner.annotators.hyp_pattern_annotator import HypView
from dfiner.annotators.nsd_annotator import NSDView
from dfiner.ontonote.ontonotes_data import read_figer

from dfiner.utils import get_default_config
from dfiner.utils.doc_serialization_utils import unserialize_docs_from_file
import spacy

if __name__ == '__main__':
    config = get_default_config()
    nlp = spacy.load('en')
    ds = read_figer(nlp, config["figer_path"])
    # cache_path = "/home/haowu4/codes/dataless_finer/cache/train.serial.json"
    # docs = unserialize_docs_from_file(nlp, cache_path)
