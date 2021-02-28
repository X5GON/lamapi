import sys
sys.path.append("../..")
# %%
import os
import pickle as pk
import tqdm
import json
from x5gonwp3tools.tools.text2tfidf.tfidf import tfidf_by_ngrams

DATAPATH = "/home/connes/code/yaleocw-corpus/data/YaleSeriesCorpus"


# %% markdown
# # TFIDF
# Format data as input of Scorer.predict_missing
# MutableMapping[Any, Dict[str, Any]]


def tfidf2candidates(X, features, names):
    print(X.shape)
    data = {names[i]: {} for i in range(X.shape[0])}
    X.eliminate_zeros()
    rindex = X.nonzero()
    for r, c in tqdm.tqdm(zip(rindex[0], rindex[1]),
                          total=rindex[0].shape[0],
                          desc="Create tfidf candidates dict"):
        data[names[r]][features[c]] = X[r, c]
    return data


# %%
def recover(source):
    paths = [(dirpath,
              source) for (dirpath,
                           dirnames,
                           filenames) in tqdm.tqdm(os.walk(DATAPATH),
                                                   desc="Search texts")  if source in filenames]
    names, texts = [], []
    for d, p in tqdm.tqdm(paths, desc="Load texts"):
        with open(d + "/" + p, "r", errors='ignore') as f:
            names.append(os.path.split(d)[1])
            texts.append("".join(f.readlines()))
    return texts, names


RESPATH = "./models/"
sources = ["phrased_3", "processedtext", "rawtext"]

for s in sources:
    texts, names = recover(s)
# %%
    if not os.path.exists(RESPATH + f"{s}.tfidf.pk"):
        tfidf = tfidf_by_ngrams(texts, names)
        with open(RESPATH + f"{s}.tfidf.pk", "wb") as f:
            pk.dump(tfidf, f)
            print(f"tfidf model save at {RESPATH + s}.tfidf.pk")
    else:
        with open(RESPATH + f"{s}.tfidf.pk", "rb") as f:
            tfidf = pk.load(f)
    print(f"tfidf model load from {RESPATH + s}.tfidf.pk")
    for n in tfidf:
        if n != "names":
            data = tfidf2candidates(tfidf[n]['X'],
                                    tfidf[n]['grams'],
                                    tfidf['names'])
            with open(RESPATH + f"{s}.{n}.tfidf.candidates.json", "w") as f:
                json.dump(data, f)
            print(f"candidates saved at {RESPATH + s}.{n}.tfidf.candidates.json")
