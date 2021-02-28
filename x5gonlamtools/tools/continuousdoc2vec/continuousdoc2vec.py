import multiprocessing
import os
import joblib
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess

from x5gonwp3tools.tools.continuouswikifier.continuouswikifier import _get_overlap_chunks


def treat_corpus_part(textlist):
    for i, text in textlist:
        chunks = _get_overlap_chunks(text)
        yield i, [(f"{i}p{j}",
                   TaggedDocument(simple_preprocess(subtext[0]),
                                  [f"{i}p{j}"])) for j, subtext in enumerate(chunks)]


def train_a_part_model_fromdb(textlist,
                              outpath,
                              vector_size=300,
                              window=5,
                              min_count=1,
                              workers=multiprocessing.cpu_count()):
    doc_id2part_id = {}
    documents = []
    for doc_id, chunk in treat_corpus_part(textlist):
        pids, texts = zip(*chunk)
        documents.extend(texts)
        doc_id2part_id[doc_id] = pids
    model = Doc2Vec(vector_size=vector_size,
                    window=window,
                    min_count=min_count,
                    workers=workers)
    model.build_vocab(documents)
    model.train(documents,
                total_examples=model.corpus_count,
                epochs=model.epochs)
    if not os.path.exists(os.path.dirname(outpath)):
        os.makedirs(os.path.dirname(outpath))
    with open(os.path.join(os.path.dirname(outpath), "doc_id2part_id.pk"), "wb") as file:
        joblib.dump(doc_id2part_id, file, protocol=-1)
    model.save(outpath)
    return doc_id2part_id, model


def load_model(modelpath):
    with open(os.path.join(os.path.dirname(modelpath), "doc_id2part_id.pk"), "rb") as file:
        doc_id2part_id = joblib.load(file)
    return doc_id2part_id, Doc2Vec.load(modelpath)


def recover_vectors(arg, model):
    return __recover_vectors(arg, model) if arg in model[0] else __interpolate(arg, model)
    # raise RuntimeError("You have to give a path, or a document id")


def __recover_vectors(doc_id, model):
    return [model[1][pid].tolist() for pid in model[0][doc_id]]


def __interpolate(text, model):
    chunks = _get_overlap_chunks(text)
    vectors = []
    for subtext in chunks:
        # print(subtext)
        document = simple_preprocess(subtext[0])
        vectors.append(model[1].infer_vector(document).tolist())
    return vectors
