import sys
sys.path.append("../..")
# %%
import os
import pickle as pk
import tqdm
import json
DATAPATH = "/home/connes/code/yaleocw-corpus/data/YaleSeriesCorpus"


# %% markdown
# # WIKIFIER
# Format data as input of Scorer.predict_missing
# MutableMapping[Any, Dict[str, Any]]
def wikifier2candidates(names, wikifiers, score):
    data = {names[i]: {} for i in range(len(wikifiers))}
    for wik, name in tqdm.tqdm(zip(wikifiers, names),
                               total=len(wikifiers),
                               desc="Create wikifier candidates dict"):
        for c in wik:
            data[name][c["title"]] = c[score]
    return data


# %%
def recover(source):
    paths = [(dirpath,
              source) for (dirpath,
                           dirnames,
                           filenames) in tqdm.tqdm(os.walk(DATAPATH),
                                                   desc="Search wikifiers") if source in filenames]
    names, texts = [], []
    for d, p in tqdm.tqdm(paths, desc="Load wikifiers"):
        with open(d + "/" + p, "rb") as f:
            names.append(os.path.split(d)[1])
            texts.append(pk.load(f))
    return texts, names


# %%
RESPATH = "./models/"
####For launching model on api start
###RESPATH = "x5gonwp3tools/eval/models/"
scores = ["cosine", "pageRank"]
wikifiers, names = recover("wikipedia_concepts")
# %%
for s in scores:
    data = wikifier2candidates(names, wikifiers, s)
    with open(RESPATH + f"wikifier.{s}.candidates.json", "w") as f:
        json.dump(data, f)
    print(f"candidates saved at {RESPATH}wikifier.{s}.candidates.json")
