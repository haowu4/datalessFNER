import gensim


class EmbeddingsType:

    LSI = 'lsi'
    LDA = 'lda'


# LSI_DIM = 10, 32, 50, 100, 200, 500
# LDA_DIM = 10, 32, 50, 100, 200, 400

_emb_dims = {EmbeddingsType.LSI: [10, 32, 50, 100, 200, 500], EmbeddingsType.LDA: [10, 32, 50, 100, 200, 400]}


def get_model_embedding(topic_predictor, tokenized_doc, len_embedding):
    def convert_tuple_vec_to_embedding(tuple_vec):
        # assuming we have all the dimensions
        n = len_embedding
        dict_vec = dict(tuple_vec)
        embedding = []
        for i in xrange(n):
            if i in dict_vec:
                embedding.append(dict_vec[i])
            else:
                # print("%d missing from topic predictions" % i)
                embedding.append(0.)
        return embedding

    tuple_vec = topic_predictor(tokenized_doc)
    return convert_tuple_vec_to_embedding(tuple_vec)


def get_lsi_topic_predictor(lsi_model_path, tfidf_model_path):
    lsi_model = gensim.models.lsimodel.LsiModel.load(lsi_model_path)
    tfidf_model = gensim.models.TfidfModel.load(tfidf_model_path)
    assert lsi_model.id2word == tfidf_model.id2word
    topic_predictor = lambda tokenized_doc: lsi_model[tfidf_model[tfidf_model.id2word.doc2bow(tokenized_doc)]]
    return topic_predictor


def get_lda_topic_predictor(lda_model_path):
    lda_model = gensim.models.ldamulticore.LdaMulticore.load(lda_model_path)
    topic_predictor = lambda tokenized_doc: lda_model.get_document_topics(lda_model.id2word.doc2bow(tokenized_doc),
                                                                          minimum_probability=0)
    return topic_predictor


def get_embedding_func(config, emb_type, emb_dim):
    if emb_type == EmbeddingsType.LSI:
        lsi_model_path = config["lsi_model_path"]
        tfidf_model_path = config["tfidf_model_path"]
        topic_predictor = get_lsi_topic_predictor(lsi_model_path % str(emb_dim), tfidf_model_path)
    elif emb_type == EmbeddingsType.LDA:
        lda_model_path = config["lda_model_path"]
        topic_predictor = get_lda_topic_predictor(lda_model_path % str(emb_dim))
    else:
        raise ValueError("Unrecognized emb type -> %s" % emb_type)

    def get_embedding(tokenized_doc):
        return get_model_embedding(topic_predictor, tokenized_doc, emb_dim)

    return get_embedding


if __name__ == "__main__":
    pass
