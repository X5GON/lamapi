import sys
sys.path.append("../..")
# %%
import os
import tqdm
import json
import re
import multiprocessing
from gensim.models.doc2vec import Doc2Vec
from x5gonwp3tools.tools.doc2vec.doc2vec import train_a_model
nb_workers = multiprocessing.cpu_count()
DATAPATH = "/home/connes/code/yaleocw-corpus/data/YaleSeriesCorpus"


# %% markdown
# # TFIDF
# Format data as input of Scorer.predict_missing
# MutableMapping[Any, Dict[str, Any]]


def doc2vec2candidates(model, names, doc_ids):
    data = {}
    for doc_id, name in tqdm.tqdm(zip(doc_ids, names),
                                  total=len(names),
                                  desc="Create doc2vec candidates dict"):
        data[name] = dict(list(enumerate(model[doc_id].astype(float))))
    return data


# %%
def recover(source):
    paths = [(dirpath,
              source) for (dirpath,
                           dirnames,
                           filenames) in tqdm.tqdm(os.walk(DATAPATH),
                                                   desc="Search texts")  if source in filenames]
    names, textspaths, doc_ids = [], [], []
    for d, p in tqdm.tqdm(paths, desc="Load texts"):
        names.append(os.path.split(d)[1])
        textspaths.append(d + "/" + p)
        doc_ids.append(int(re.findall(r"(\d+)\-.*", names[-1])[0]))
    return textspaths, names, doc_ids


RESPATH = "./models/"


textspaths, names, doc_ids = recover("rawtext")
# %%
if not os.path.exists(RESPATH + f"rawtext.doc2vec.model"):
    doc2vecmodel = train_a_model(textspaths, RESPATH + f"rawtext.doc2vec.model",
                                 doc_ids,
                                 vector_size=300,
                                 window=5,
                                 min_count=1,
                                 workers=multiprocessing.cpu_count())
    print(f"doc2vec model save at {RESPATH}rawtext.doc2vec.model")
else:
    doc2vecmodel = Doc2Vec.load(RESPATH + f"rawtext.doc2vec.model")
    print(f"doc2vec model load from {RESPATH}rawtext.doc2vec.model")

data = doc2vec2candidates(doc2vecmodel, names, doc_ids)
with open(RESPATH + f"rawtext.doc2vec.candidates.json", "w") as f:
    json.dump(data, f)
print(f"candidates saved at rawtext.doc2vec.candidates.json")
