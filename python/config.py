import os


embeddings_path = "/home/haowu4/data/autoextend/GoogleNews-vectors-negative300.combined_500k.txt"
synset_offset_pos_embeddings_path = "/home/haowu4/data/autoextend/synset_embeddings_300.txt"

project_root = "/home/haowu4/codes/dataless_finer"

fine_type_to_synset_file = os.path.join(project_root, "resources", "type_to_wordnet_senses.txt")
nsd_cache_path = os.path.join(project_root, "cache/nsd.pkl")

figer_test_json = "/home/muddire2/nlpresearch2/ner-datasets/Wiki/test.json"
