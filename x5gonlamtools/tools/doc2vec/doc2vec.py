import os
import multiprocessing
import smart_open
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.utils import simple_preprocess
from x5gonwp3tools.tools.continuouswikifier.continuouswikifier import _get_overlap_chunks


def read_corpus(fnames, doc_ids=[]):
    for i, fname in enumerate(fnames):
        with smart_open.smart_open(fname, encoding="iso-8859-1") as f:
                yield TaggedDocument(simple_preprocess("".join(f.readlines())),
                                     [doc_ids[i] if doc_ids else i])


def treat_corpus(textlist):
    for i, text in textlist:
        yield TaggedDocument(simple_preprocess(text),
                             [i])


def train_a_model(textspaths,
                  outpath,
                  vector_size=300,
                  window=5,
                  min_count=1,
                  workers=multiprocessing.cpu_count()):
    documents = list(read_corpus(textspaths))
    model = Doc2Vec(vector_size=vector_size,
                    window=window,
                    min_count=min_count,
                    workers=workers)
    model.build_vocab(documents)
    model.train(documents,
                total_examples=model.corpus_count,
                epochs=model.epochs)
    model.save(outpath)
    return model


def train_a_model_fromdb(textlist, outpath,
                         vector_size=300,
                         window=5,
                         min_count=1,
                         workers=multiprocessing.cpu_count()):
    documents = list(treat_corpus(textlist))
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
    model.save(outpath)
    return model

def load_model(modelpath):
    return Doc2Vec.load(modelpath)


def recover_vector(arg, model):
    if isinstance(arg, str):
        return __interpolate(arg, model)
    elif isinstance(arg, int):
        return __recover_vector(arg, model)
    else:
        raise RuntimeError("You have to give a text, or a document id")


def __recover_vector(doc_id, model):
    return model[doc_id]


def __interpolate(text, model):
    return model.infer_vector(simple_preprocess(text))
